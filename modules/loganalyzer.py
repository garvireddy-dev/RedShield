import re
import threading
from collections import Counter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import theme

PATTERN = re.compile(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)")


class LogAnalyzerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        ttk.Button(top, text="Choose Log File", command=self.choose_file).pack(side="left")
        self.file_label = ttk.Label(top, text="No file selected", foreground=theme.MUTED)
        self.file_label.pack(side="left", padx=10)

        ttk.Label(top, text="Threshold:").pack(side="left", padx=(20, 5))
        self.threshold_var = tk.StringVar(value="5")
        ttk.Entry(top, textvariable=self.threshold_var, width=5).pack(side="left")

        ttk.Button(top, text="Analyze", command=self.start_analyze).pack(side="left", padx=15)

        self.status = ttk.Label(self, text="Ready", foreground=theme.MUTED)
        self.status.pack(anchor="w", padx=15, pady=10)

        self.tree = ttk.Treeview(self, columns=("ip", "count", "verdict"), show="headings", height=15)
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("count", text="Failed Attempts")
        self.tree.heading("verdict", text="Verdict")
        self.tree.column("ip", width=250, anchor="center")
        self.tree.column("count", width=200, anchor="center")
        self.tree.column("verdict", width=250, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Log/Text files", "*.log *.txt"), ("All files", "*.*")])
        if path:
            self.file_path = path
            self.file_label.configure(text=path.split("/")[-1].split("\\")[-1])

    def start_analyze(self):
        if not hasattr(self, "file_path"):
            messagebox.showerror("Error", "Choose a log file first.")
            return
        try:
            threshold = int(self.threshold_var.get())
        except ValueError:
            messagebox.showerror("Error", "Threshold must be a number.")
            return
        self.status.configure(text="Analyzing...")
        threading.Thread(target=self.analyze, args=(threshold,), daemon=True).start()

    def analyze(self, threshold):
        counts = Counter()
        try:
            with open(self.file_path, errors="ignore") as f:
                for line in f:
                    m = PATTERN.search(line)
                    if m:
                        counts[m.group(1)] += 1
        except OSError:
            counts = Counter()
        self.after(0, self.show_results, counts, threshold)

    def show_results(self, counts, threshold):
        self.tree.delete(*self.tree.get_children())
        for ip, count in sorted(counts.items(), key=lambda x: -x[1]):
            verdict = "BRUTE FORCE SUSPECTED" if count >= threshold else "Normal"
            self.tree.insert("", "end", values=(ip, count, verdict))
        alerts = sum(1 for c in counts.values() if c >= threshold)
        self.status.configure(text=f"{len(counts)} IP(s) found, {alerts} alert(s)")