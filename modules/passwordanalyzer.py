import math
import tkinter as tk
from tkinter import ttk
import theme

COMMON_PASSWORDS = {"password", "123456", "123456789", "qwerty", "admin",
                     "letmein", "welcome", "monkey", "password123", "abc123"}


class PasswordAnalyzerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        ttk.Label(top, text="Password:").pack(side="left", padx=5)
        self.pw_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.pw_var, width=40, show="*")
        entry.pack(side="left", padx=5)
        entry.bind("<KeyRelease>", lambda e: self.analyze())

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Show", variable=self.show_var,
                       command=lambda: entry.configure(show="" if self.show_var.get() else "*")).pack(side="left", padx=10)

        self.bar = ttk.Progressbar(self, maximum=100, mode="determinate")
        self.bar.pack(fill="x", padx=15, pady=(10, 5))

        self.strength_label = ttk.Label(self, text="Strength: -", font=theme.FONT_BOLD)
        self.strength_label.pack(anchor="w", padx=15)

        self.entropy_label = ttk.Label(self, text="Entropy: -", foreground=theme.MUTED)
        self.entropy_label.pack(anchor="w", padx=15, pady=(5, 0))

        self.crack_label = ttk.Label(self, text="Estimated crack time: -", foreground=theme.MUTED)
        self.crack_label.pack(anchor="w", padx=15, pady=(5, 0))

        self.tips_label = ttk.Label(self, text="", foreground=theme.RED, wraplength=850, justify="left")
        self.tips_label.pack(anchor="w", padx=15, pady=(15, 0))

    def analyze(self):
        pw = self.pw_var.get()
        if not pw:
            self.bar["value"] = 0
            self.strength_label.configure(text="Strength: -")
            self.entropy_label.configure(text="Entropy: -")
            self.crack_label.configure(text="Estimated crack time: -")
            self.tips_label.configure(text="")
            return

        pool = 0
        if any(c.islower() for c in pw):
            pool += 26
        if any(c.isupper() for c in pw):
            pool += 26
        if any(c.isdigit() for c in pw):
            pool += 10
        if any(not c.isalnum() for c in pw):
            pool += 32
        pool = max(pool, 1)

        entropy = len(pw) * math.log2(pool)
        guesses = 2 ** entropy
        seconds = guesses / 1_000_000_000

        if pw.lower() in COMMON_PASSWORDS:
            entropy = 0
            seconds = 0

        if entropy < 28:
            level, color, score = "Very Weak", "#e5231b", 15
        elif entropy < 36:
            level, color, score = "Weak", "#e5231b", 35
        elif entropy < 60:
            level, color, score = "Moderate", "#d99c00", 60
        elif entropy < 80:
            level, color, score = "Strong", "#2ecc71", 85
        else:
            level, color, score = "Very Strong", "#2ecc71", 100

        self.bar["value"] = score
        self.strength_label.configure(text=f"Strength: {level}", foreground=color)
        self.entropy_label.configure(text=f"Entropy: {entropy:.1f} bits")
        self.crack_label.configure(text=f"Estimated crack time (brute force @ 1B guesses/sec): {self.format_time(seconds)}")

        tips = []
        if len(pw) < 12:
            tips.append("Use at least 12 characters.")
        if not any(c.isupper() for c in pw):
            tips.append("Add an uppercase letter.")
        if not any(c.isdigit() for c in pw):
            tips.append("Add a digit.")
        if not any(not c.isalnum() for c in pw):
            tips.append("Add a symbol.")
        if pw.lower() in COMMON_PASSWORDS:
            tips.append("This is one of the most common passwords in the world.")
        self.tips_label.configure(text="  ".join(tips))

    def format_time(self, seconds):
        if seconds < 1:
            return "instantly"
        units = [("years", 31536000), ("days", 86400), ("hours", 3600), ("minutes", 60), ("seconds", 1)]
        for name, size in units:
            if seconds >= size:
                return f"{seconds / size:,.0f} {name}"
        return "instantly"