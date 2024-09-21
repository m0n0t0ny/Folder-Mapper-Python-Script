import tkinter as tk
from tkinter import ttk
from tkinter.font import Font


class ThemedWindow(tk.Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.configure(bg=self.style.lookup("TFrame", "background"))

    def update_theme(self):
        bg_color = self.style.lookup("TFrame", "background")
        self.configure(bg=bg_color)
        for widget in self.winfo_children():
            self._update_widget_colors(widget, bg_color)

    def _update_widget_colors(self, widget, bg_color):
        if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button)):
            widget.configure(style="TFrame")
        elif isinstance(widget, ttk.Entry):
            widget.configure(style="TEntry")

        for child in widget.winfo_children():
            self._update_widget_colors(child, bg_color)


class ThemedButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.update_style()

    def update_style(self):
        if self.style.theme_use() == "clam":  # Dark mode
            bg_color = "#4A4A4A"
            fg_color = "white"
            hover_color = "#5e5e5e"
        else:  # Light mode
            bg_color = self.style.lookup("TButton", "background")
            fg_color = "black"
            hover_color = "#e1e1e1"

        self.style.configure(
            "ThemedButton.TButton",
            background=bg_color,
            foreground=fg_color,
            padding=(10, 5),
        )
        self.style.map(
            "ThemedButton.TButton",
            background=[("active", hover_color)],
            foreground=[
                ("active", "white" if self.style.theme_use() == "clam" else "black")
            ],
        )
        self.configure(style="ThemedButton.TButton")


class GreenButton(ThemedButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.update_style()

    def update_style(self):
        self.style.configure(
            "GreenButton.TButton",
            background="green",
            foreground="white",
            padding=(10, 5),
        )
        self.style.map("GreenButton.TButton", background=[("active", "#45a049")])
        self.configure(style="GreenButton.TButton")


class ThemedEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.update_style()

    def update_style(self):
        if self.style.theme_use() == "clam":  # Dark mode
            bg_color = "#4A4A4A"
            fg_color = "white"
        else:  # Light mode
            bg_color = "white"
            fg_color = "black"

        self.style.configure(
            "ThemedEntry.TEntry",
            fieldbackground=bg_color,
            foreground=fg_color,
            padding=(5, 5),
        )
        self.configure(style="ThemedEntry.TEntry")


class ThemedLink(ttk.Label):
    def __init__(self, master=None, **kwargs):
        self.command = kwargs.pop("command", None)
        super().__init__(master, **kwargs)
        self.style = ttk.Style()
        self.update_style()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Store the original font
        self.original_font = Font(font=self.cget("font"))
        self.underline_font = Font(font=self.cget("font"))
        self.underline_font.configure(underline=True)

    def update_style(self):
        if self.style.theme_use() == "clam":  # Dark mode
            fg_color = "lightblue"
            hover_color = "#ADD8E6"
        else:  # Light mode
            fg_color = "blue"
            hover_color = "#0000FF"

        self.style.configure("Link.TLabel", foreground=fg_color, cursor="hand2")
        self.style.map("Link.TLabel", foreground=[("active", hover_color)])
        self.configure(style="Link.TLabel")

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.configure(font=self.underline_font)

    def _on_leave(self, event):
        self.configure(font=self.original_font)
