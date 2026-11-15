import tkinter as tk
from tkinter import ttk, messagebox
import theme
from modules.portscanner import PortScannerTab
from modules.hashtool import HashToolTab
from modules.passwordanalyzer import PasswordAnalyzerTab
from modules.filemonitor import FileMonitorTab
from modules.loganalyzer import LogAnalyzerTab
from modules.history import HistoryTab, init_db


class RedShieldApp:
    def __init__(self, root):
        self.root = root
        root.title("RedShield - Cybersecurity Toolkit")
        root.geometry("1000x700")
        theme.apply_theme(root)
        init_db()

        ttk.Label(root, text="REDSHIELD", font=theme.TITLE_FONT,
                  foreground=theme.RED).pack(pady=(15, 0))
        ttk.Label(root, text="Cybersecurity Toolkit",
                  foreground=theme.MUTED).pack(pady=(0, 10))

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tabs.add(PortScannerTab(self.tabs), text="Port Scanner")
        self.tabs.add(HashToolTab(self.tabs), text="Hash Tool")
        self.tabs.add(PasswordAnalyzerTab(self.tabs), text="Password Analyzer")
        self.tabs.add(FileMonitorTab(self.tabs), text="File Monitor")
        self.tabs.add(LogAnalyzerTab(self.tabs), text="Log Analyzer")
        self.tabs.add(HistoryTab(self.tabs), text="History")

        root.after(300, self.show_disclaimer)

    def show_disclaimer(self):
        messagebox.showwarning(
            "Authorized Use Only",
            "RedShield is for educational use.\n"
            "Only scan systems you own or have written permission to test.")


if __name__ == "__main__":
    root = tk.Tk()
    RedShieldApp(root)
    root.mainloop()