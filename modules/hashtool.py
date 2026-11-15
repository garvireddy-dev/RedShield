import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import theme

HASH_LENGTHS = {32: "md5", 40: "sha1", 64: "sha256"}


class HashToolTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.wordlist_path = tk.StringVar(value="No wordlist selected")
        self.cracking = False
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        ttk.Label(top, text="Hash:").grid(row=0, column=0, padx=5, sticky="w")
        self.hash_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.hash_var, width=60).grid(row=0, column=1, padx=5, columnspan=3, sticky="w")

        ttk.Button(top, text="Identify Type", command=self.identify).grid(row=0, column=4, padx=10)

        self.type_label = ttk.Label(top, text="Type: unknown", foreground=theme.RED)
        self.type_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(top, text="Choose Wordlist", command=self.choose_wordlist).grid(row=2, column=0, pady=10, sticky="w")
        ttk.Label(top, textvariable=self.wordlist_path, foreground=theme.MUTED).grid(row=2, column=1, columnspan=3, sticky="w")

        self.crack_btn = ttk.Button(top, text="Crack Hash", command=self.start_crack)
        self.crack_btn.grid(row=3, column=0, pady=10, sticky="w")

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=15)

        self.result = ttk.Label(self, text="Ready", foreground=theme.MUTED, font=theme.FONT_BOLD)
        self.result.pack(anchor="w", padx=15, pady=15)

        note = ("Note: a salted hash cannot be cracked this way. "
                "Salting adds random data before hashing, so the "
                "same password never produces the same hash twice.")
        ttk.Label(self, text=note, foreground=theme.MUTED, wraplength=850).pack(anchor="w", padx=15)

    def identify(self):
        h = self.hash_var.get().strip()
        algo = HASH_LENGTHS.get(len(h))
        if algo and all(c in "0123456789abcdefABCDEF" for c in h):
            self.type_label.configure(text=f"Type: {algo.upper()} ({len(h)} hex chars)")
            self.detected_algo = algo
        else:
            self.type_label.configure(text="Type: unknown or invalid hash")
            self.detected_algo = None

    def choose_wordlist(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.wordlist_path.set(path)

    def start_crack(self):
        h = self.hash_var.get().strip().lower()
        if not h:
            messagebox.showerror("Error", "Enter a hash first.")
            return
        if not hasattr(self, "detected_algo") or not self.detected_algo:
            self.identify()
        if not self.detected_algo:
            messagebox.showerror("Error", "Could not identify the hash type.")
            return
        path = self.wordlist_path.get()
        if path == "No wordlist selected":
            messagebox.showerror("Error", "Choose a wordlist file first.")
            return
        self.cracking = True
        self.crack_btn.configure(state="disabled")
        self.progress.start(10)
        self.result.configure(text="Cracking...", foreground=theme.MUTED)
        threading.Thread(target=self.crack, args=(h, self.detected_algo, path), daemon=True).start()

    def crack(self, target, algo, path):
        found = None
        try:
            with open(path, errors="ignore") as f:
                for line in f:
                    word = line.strip()
                    if not word:
                        continue
                    if hashlib.new(algo, word.encode()).hexdigest() == target:
                        found = word
                        break
        except OSError:
            found = None
        self.after(0, self.finish_crack, found)

    def finish_crack(self, found):
        self.cracking = False
        self.crack_btn.configure(state="normal")
        self.progress.stop()
        if found:
            self.result.configure(text=f"Password found: {found}", foreground=theme.RED)
        else:
            self.result.configure(text="Not found in this wordlist", foreground=theme.MUTED)