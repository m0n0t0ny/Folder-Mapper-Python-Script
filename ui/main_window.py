import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from utils.file_operations import generate_file_hierarchy
from utils.settings import load_settings, save_settings
from localization.translations import translations
from data.changelog import changelog
from ui.components import (
    ThemedWindow,
    ThemedButton,
    GreenButton,
    ThemedEntry,
    ThemedLink,
)


class FolderMapGenerator:
    def __init__(self, master):
        self.master = master
        self.master.title("FMG - Folder Map Generator")
        self.master.geometry("500x300")

        self.settings = load_settings()
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.current_language = tk.StringVar(value=self.settings["language"])
        self.dark_mode = tk.BooleanVar(value=self.settings["dark_mode"])

        self.style = ttk.Style()
        self.create_widgets()
        self.update_language()
        self.apply_theme()

    def create_widgets(self):
        # Frame principale
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame per input e output
        io_frame = ttk.Frame(self.main_frame)
        io_frame.pack(fill=tk.X, pady=10)

        # Configura le colonne del io_frame
        io_frame.columnconfigure(0, weight=0)  # Colonna dei pulsanti
        io_frame.columnconfigure(1, weight=1)  # Colonna delle entry

        # Input
        self.input_button = ThemedButton(
            io_frame, text="Select Input", command=self.select_source_folder, width=15
        )
        self.input_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        self.input_entry = ThemedEntry(
            io_frame, textvariable=self.source_folder, state="readonly"
        )
        self.input_entry.grid(row=0, column=1, pady=5, sticky="we")

        # Output
        self.output_button = ThemedButton(
            io_frame, text="Select Output", command=self.select_output_folder, width=15
        )
        self.output_button.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="w")
        self.output_entry = ThemedEntry(
            io_frame, textvariable=self.output_folder, state="readonly"
        )
        self.output_entry.grid(row=1, column=1, pady=5, sticky="we")

        # Pulsante Map Folder
        self.map_button = GreenButton(
            self.main_frame, text="Map Folder", command=self.generate_map
        )
        self.map_button.pack(pady=(20, 5), fill=tk.X)

        # Link sotto Map Folder
        self.kofi_link = ThemedLink(
            self.main_frame,
            text="Support the developer",
            cursor="hand2",
            command=self.open_kofi,
        )
        self.kofi_link.pack(pady=(0, 20))
        self.kofi_link.configure(font=("TkDefaultFont", 8))

        # Frame inferiore
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        # Pulsanti Changelog, Guida Utente, Toggle Lingua, Toggle Dark Mode e Close
        self.changelog_button = ThemedButton(
            bottom_frame, text="!", width=3, command=self.show_changelog
        )
        self.changelog_button.pack(side=tk.LEFT, padx=5)

        self.help_button = ThemedButton(
            bottom_frame, text="?", width=3, command=self.show_user_guide
        )
        self.help_button.pack(side=tk.LEFT, padx=5)

        self.toggle_lang_button = ThemedButton(
            bottom_frame, text="EN", width=3, command=self.toggle_language
        )
        self.toggle_lang_button.pack(side=tk.LEFT, padx=5)

        self.toggle_dark_mode_button = ThemedButton(
            bottom_frame, text="💡", width=3, command=self.toggle_dark_mode
        )
        self.toggle_dark_mode_button.pack(side=tk.LEFT, padx=5)

        self.close_button = ThemedButton(
            bottom_frame, text="Close FMG", command=self.master.quit
        )
        self.close_button.pack(side=tk.RIGHT)

    def update_language(self):
        lang = self.current_language.get()
        self.master.title(translations[lang]["title"])
        self.input_button.config(text=translations[lang]["select_input"])
        self.output_button.config(text=translations[lang]["select_output"])
        self.map_button.config(text=translations[lang]["map_folder"])
        self.close_button.config(text=translations[lang]["close"])

        # Aggiorna il testo del pulsante di toggle della lingua
        self.toggle_lang_button.config(text="EN" if lang == "Italiano" else "IT")

    def toggle_language(self):
        new_lang = (
            "English" if self.current_language.get() == "Italiano" else "Italiano"
        )
        self.current_language.set(new_lang)
        self.settings["language"] = new_lang
        save_settings(self.settings)
        self.update_language()

    def toggle_dark_mode(self):
        self.dark_mode.set(not self.dark_mode.get())
        self.settings["dark_mode"] = self.dark_mode.get()
        save_settings(self.settings)
        self.apply_theme()

    def update_language(self):
        lang = self.current_language.get()
        self.master.title(translations[lang]["title"])
        self.input_button.config(text=translations[lang]["select_input"])
        self.output_button.config(text=translations[lang]["select_output"])
        self.map_button.config(text=translations[lang]["map_folder"])
        self.close_button.config(text=translations[lang]["close"])

        # Modifica questa riga
        self.toggle_lang_button.config(text="EN" if lang == "Italiano" else "IT")

    def select_source_folder(self):
        folder = filedialog.askdirectory(
            title=translations[self.current_language.get()]["select_input"]
        )
        if folder:
            self.source_folder.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory(
            title=translations[self.current_language.get()]["select_output"]
        )
        if folder:
            self.output_folder.set(folder)

    def generate_map(self):
        lang = self.current_language.get()
        if not self.source_folder.get() or not self.output_folder.get():
            messagebox.showerror(
                translations[lang]["error"], translations[lang]["select_folders"]
            )
            return

        output_file = os.path.join(self.output_folder.get(), "FMG.txt")
        if os.path.exists(output_file):
            if not messagebox.askyesno(
                translations[lang]["file_exists"],
                translations[lang]["file_exists_message"],
            ):
                new_file = filedialog.asksaveasfilename(
                    initialdir=self.output_folder.get(),
                    initialfile="FMG.txt",
                    title=translations[lang]["save_as"],
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                )
                if new_file:
                    output_file = new_file
                else:
                    return  # L'utente ha annullato il salvataggio

        try:
            generate_file_hierarchy(
                self.source_folder.get(), output_file, translations, lang
            )
            messagebox.showinfo(
                translations[lang]["success"],
                f"{translations[lang]['map_generated']}\n{output_file}",
            )
        except Exception as e:
            messagebox.showerror(
                translations[lang]["error"],
                f"{translations[lang]['error_occurred']}\n{str(e)}",
            )

    def show_changelog(self):
        lang = self.current_language.get()
        changelog_window = tk.Toplevel(self.master)
        changelog_window.title(translations[lang]["changelog_title"])
        changelog_window.geometry("400x300")

        text_widget = tk.Text(changelog_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(expand=True, fill="both")
        text_widget.insert(tk.END, changelog)
        text_widget.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(
            changelog_window, orient="vertical", command=text_widget.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

    def show_user_guide(self):
        lang = self.current_language.get()
        messagebox.showinfo(
            translations[lang]["user_guide_title"], translations[lang]["user_guide"]
        )

    def show_settings(self):
        settings_window = ThemedWindow(self.master)
        settings_window.title(translations[self.current_language.get()]["settings"])
        settings_window.geometry("300x150")

        # Lingua
        lang_frame = ttk.Frame(settings_window)
        lang_frame.pack(pady=10)
        ttk.Label(
            lang_frame, text=translations[self.current_language.get()]["language"]
        ).pack(side=tk.LEFT)
        lang_menu = ttk.Combobox(
            lang_frame,
            textvariable=self.current_language,
            values=["English", "Italiano"],
            state="readonly",
            width=10,
        )
        lang_menu.pack(side=tk.LEFT, padx=5)

        # Modalità scura
        dark_mode_frame = ttk.Frame(settings_window)
        dark_mode_frame.pack(pady=10)
        ttk.Label(
            dark_mode_frame, text=translations[self.current_language.get()]["dark_mode"]
        ).pack(side=tk.LEFT)
        dark_mode_check = ttk.Checkbutton(dark_mode_frame, variable=self.dark_mode)
        dark_mode_check.pack(side=tk.LEFT, padx=5)

        # Pulsante Applica
        apply_button = ThemedButton(
            settings_window,
            text=translations[self.current_language.get()]["apply"],
            command=lambda: self.apply_settings(settings_window),
        )
        apply_button.pack(pady=20)

    def apply_theme(self):
        if self.dark_mode.get():
            self.style.theme_use("clam")
            bg_color = "#2E2E2E"
            fg_color = "white"
            entry_bg = "#4A4A4A"
            button_bg = "#4A4A4A"
            button_fg = "white"
            link_color = "lightblue"
            link_hover_color = "#ADD8E6"  # Azzurro chiaro per hover in modalità scura
        else:
            self.style.theme_use("default")
            bg_color = self.style.lookup("TFrame", "background")
            fg_color = "black"
            entry_bg = "white"
            button_bg = self.style.lookup("TButton", "background")
            button_fg = "black"
            link_color = "blue"
            link_hover_color = "#0000FF"  # Blu più scuro per hover in modalità chiara

        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=button_bg, foreground=button_fg)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)

        # Configurazione specifica per ThemedButton
        self.style.configure(
            "ThemedButton.TButton", background=button_bg, foreground=button_fg
        )
        self.style.map(
            "ThemedButton.TButton",
            background=[("active", "#5e5e5e" if self.dark_mode.get() else "#e1e1e1")],
            foreground=[("active", "white" if self.dark_mode.get() else "black")],
        )

        # Configurazione per GreenButton
        self.style.configure(
            "GreenButton.TButton", background="green", foreground="white"
        )
        self.style.map("GreenButton.TButton", background=[("active", "#45a049")])

        self.master.configure(bg=bg_color)
        self.main_frame.configure(style="TFrame")

        # Aggiorna lo stile del link
        self.style.configure("Link.TLabel", foreground=link_color)
        self.style.map(
            "Link.TLabel",
            foreground=[("active", link_hover_color)],
            font=[("active", ("TkDefaultFont", 9, "underline"))],
        )

        # Aggiorna tutti i widget
        for widget in self.master.winfo_children():
            self._update_widget_colors(widget)

        # Aggiorna anche i widget nella finestra principale
        self._update_widget_colors(self.master)

        # Aggiorna l'icona del pulsante dark mode
        self.toggle_dark_mode_button.config(text="🌞" if self.dark_mode.get() else "🌙")

    def _update_widget_colors(self, widget):
        if isinstance(widget, (ThemedButton, GreenButton, ThemedEntry)):
            widget.update_style()
        for child in widget.winfo_children():
            self._update_widget_colors(child)

    def apply_settings(self, settings_window):
        self.settings["language"] = self.current_language.get()
        self.settings["dark_mode"] = self.dark_mode.get()
        save_settings(self.settings)
        self.update_language()
        self.apply_theme()
        settings_window.destroy()

    def open_kofi(self):
        webbrowser.open_new("https://ko-fi.com/antoniobertuccio")
