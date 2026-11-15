from tkinter import ttk

BG = "#0a0a0a"
PANEL = "#141414"
RED = "#e50914"
DARK_RED = "#8b0000"
TEXT = "#f5f5f5"
MUTED = "#9a9a9a"

FONT = ("Consolas", 11)
FONT_BOLD = ("Consolas", 11, "bold")
TITLE_FONT = ("Consolas", 24, "bold")


def apply_theme(root):
    root.configure(bg=BG)
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT)

    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT,
                    padding=(14, 8), font=FONT_BOLD)
    style.map("TNotebook.Tab",
              background=[("selected", RED)],
              foreground=[("selected", "#ffffff")])

    style.configure("TButton", background=RED, foreground="#ffffff",
                    font=FONT_BOLD, padding=8, borderwidth=0)
    style.map("TButton", background=[("active", DARK_RED)])

    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT,
                    insertcolor=TEXT)

    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, font=FONT, rowheight=26)
    style.configure("Treeview.Heading", background=RED, foreground="#ffffff",
                    font=FONT_BOLD)

    style.configure("Horizontal.TProgressbar", background=RED,
                    troughcolor=PANEL)