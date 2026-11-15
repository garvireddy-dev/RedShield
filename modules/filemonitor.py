import os
import hashlib
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import theme

BASELINE_FILE = "redshield_baseline.json"


class FileMonitorTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.folder_var = tk.StringVar(value="No folder selected")
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        ttk.Button(top, text="Choose Folder", command=self.choose_folder).pack(side="left")
        ttk.Label(top, textvariable=self.folder_var, foreground=theme.MUTED).pack(side="left", padx=10)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=15)
        ttk.Button(btns, text="Save Baseline", command=self.save_baseline).pack(side="left", padx=(0, 10))
        ttk.Button(btns, text="Check Now", command=self.check_now).pack(side="left")

        self.status = ttk.Label(self, text="Ready", foreground=theme.MUTED)
        self.status.pack(anchor="w", padx=15, pady=10)

        self.tree = ttk.Treeview(self, columns=("file", "status"), show="headings", height=15)
        self.tree.heading("file", text="File")
        self.tree.heading("status", text="Status")
        self.tree.column("file", width=600)
        self.tree.column("status", width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_var.set(path)

    def hash_folder(self, folder):
        hashes = {}
        for root, _, files in os.walk(folder):
            for name in files:
                full = os.path.join(root, name)
                try:
                    h = hashlib.sha256()
                    with open(full, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            h.update(chunk)
                    hashes[full] = h.hexdigest()
                except OSError:
                    continue
        return hashes

    def save_baseline(self):
        folder = self.folder_var.get()
        if folder == "No folder selected":
            messagebox.showerror("Error", "Choose a folder first.")
            return
        self.status.configure(text="Scanning folder...")
        threading.Thread(target=self._save_baseline_thread, args=(folder,), daemon=True).start()

    def _save_baseline_thread(self, folder):
        hashes = self.hash_folder(folder)
        data = {"folder": folder, "hashes": hashes}
        with open(BASELINE_FILE, "w") as f:
            json.dump(data, f)
        self.after(0, lambda: self.status.configure(
            text=f"Baseline saved: {len(hashes)} file(s)"))

    def check_now(self):
        if not os.path.exists(BASELINE_FILE):
            messagebox.showerror("Error", "No baseline saved yet. Click 'Save Baseline' first.")
            return
        self.status.configure(text="Checking for changes...")
        threading.Thread(target=self._check_thread, daemon=True).start()

    def _check_thread(self):
        with open(BASELINE_FILE) as f:
            data = json.load(f)
        old = data["hashes"]
        new = self.hash_folder(data["folder"])

        added = [p for p in new if p not in old]
        removed = [p for p in old if p not in new]
        modified = [p for p in new if p in old and new[p] != old[p]]

        self.after(0, self._show_results, added, removed, modified)

    def _show_results(self, added, removed, modified):
        self.tree.delete(*self.tree.get_children())
        for p in modified:
            self.tree.insert("", "end", values=(p, "MODIFIED"))
        for p in added:
            self.tree.insert("", "end", values=(p, "ADDED"))
        for p in removed:
            self.tree.insert("", "end", values=(p, "DELETED"))
        total = len(added) + len(removed) + len(modified)
        if total == 0:
            self.status.configure(text="No changes detected")
        else:
            self.status.configure(text=f"{total} change(s) detected")