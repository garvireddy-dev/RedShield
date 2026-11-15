import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import theme

DB_FILE = "redshield.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT, target TEXT, result TEXT, timestamp TEXT)""")
    conn.commit()
    conn.close()


def log_scan(module, target, result):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO scans (module, target, result, timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))",
                 (module, target, result))
    conn.commit()
    conn.close()


class HistoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Export CSV", command=self.export_csv).pack(side="left", padx=10)

        self.tree = ttk.Treeview(self, columns=("time", "module", "target", "result"), show="headings", height=18)
        for col, label, width in [("time", "Time", 160), ("module", "Module", 140),
                                   ("target", "Target", 200), ("result", "Result", 350)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT timestamp, module, target, result FROM scans ORDER BY id DESC LIMIT 200").fetchall()
        conn.close()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT timestamp, module, target, result FROM scans ORDER BY id DESC").fetchall()
        conn.close()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Module", "Target", "Result"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Report saved to {path}")