import socket
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox
import theme

SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 443: "HTTPS",
    445: "SMB", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    8000: "HTTP-Alt", 8080: "HTTP-Proxy",
}

SAFE_HOSTS = ("127.0.0.1", "localhost", "scanme.nmap.org")
NUM_WORKERS = 100


class PortScannerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.result_queue = queue.Queue()
        self.stop_flag = threading.Event()
        self.scanning = False
        self.total = 0
        self.done = 0
        self.start_time = 0
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        ttk.Label(top, text="Target:").grid(row=0, column=0, padx=5)
        self.host_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(top, textvariable=self.host_var, width=22).grid(row=0, column=1, padx=5)

        ttk.Label(top, text="Ports:").grid(row=0, column=2, padx=5)
        self.start_var = tk.StringVar(value="1")
        self.end_var = tk.StringVar(value="1024")
        ttk.Entry(top, textvariable=self.start_var, width=7).grid(row=0, column=3)
        ttk.Label(top, text="to").grid(row=0, column=4, padx=3)
        ttk.Entry(top, textvariable=self.end_var, width=7).grid(row=0, column=5)

        self.scan_btn = ttk.Button(top, text="Scan", command=self.start_scan)
        self.scan_btn.grid(row=0, column=6, padx=(15, 5))
        self.stop_btn = ttk.Button(top, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_btn.grid(row=0, column=7, padx=5)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=15)

        self.status = ttk.Label(self, text="Ready", foreground=theme.MUTED)
        self.status.pack(anchor="w", padx=15, pady=5)

        self.tree = ttk.Treeview(self, columns=("port", "service"), show="headings", height=15)
        self.tree.heading("port", text="Open Port")
        self.tree.heading("service", text="Service")
        self.tree.column("port", width=150, anchor="center")
        self.tree.column("service", width=300, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def start_scan(self):
        host = self.host_var.get().strip()
        try:
            start, end = int(self.start_var.get()), int(self.end_var.get())
        except ValueError:
            messagebox.showerror("Error", "Ports must be numbers.")
            return
        if not (1 <= start <= end <= 65535):
            messagebox.showerror("Error", "Use ports 1-65535, with start <= end.")
            return
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            messagebox.showerror("Error", "Could not resolve that host.")
            return
        if host not in SAFE_HOSTS:
            if not messagebox.askyesno(
                    "Authorization",
                    "Do you own this system or have written permission to scan it?"):
                return

        self.tree.delete(*self.tree.get_children())
        self.result_queue = queue.Queue()
        self.stop_flag.clear()
        self.total = end - start + 1
        self.done = 0
        self.progress.configure(maximum=self.total, value=0)
        self.start_time = time.time()
        self.scanning = True
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status.configure(text=f"Scanning {ip} ...")

        tasks = queue.Queue()
        for p in range(start, end + 1):
            tasks.put(p)
        for _ in range(min(NUM_WORKERS, self.total)):
            threading.Thread(target=self.worker,
                             args=(ip, tasks, self.result_queue),
                             daemon=True).start()

        self.after(100, self.poll_queue)

    def stop_scan(self):
        self.stop_flag.set()
        self.scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status.configure(text="Stopped by user")

    def worker(self, ip, tasks, results):
        while not self.stop_flag.is_set():
            try:
                port = tasks.get_nowait()
            except queue.Empty:
                return
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                is_open = (s.connect_ex((ip, port)) == 0)
            except OSError:
                is_open = False
            finally:
                s.close()
            results.put((port, is_open))

    def poll_queue(self):
        try:
            for _ in range(200):
                port, is_open = self.result_queue.get_nowait()
                self.done += 1
                if is_open:
                    service = SERVICES.get(port, "Unknown")
                    self.tree.insert("", "end", values=(port, service))
        except queue.Empty:
            pass

        self.progress["value"] = self.done
        if not self.scanning:
            return
        if self.done >= self.total:
            self.finish_scan()
        else:
            self.after(100, self.poll_queue)

    def finish_scan(self):
        self.scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        rows = sorted(self.tree.get_children(),
                      key=lambda i: int(self.tree.set(i, "port")))
        for index, row in enumerate(rows):
            self.tree.move(row, "", index)
        took = time.time() - self.start_time
        self.status.configure(
            text=f"Done: {len(rows)} open port(s) found in {took:.1f}s")