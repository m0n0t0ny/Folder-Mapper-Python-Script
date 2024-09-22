import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from PIL import Image, ImageTk
from utils.file_operations import generate_file_hierarchy_threaded
from utils.settings import load_settings, save_settings
from localization.translations import translations


class FolderMapGenerator:
    def __init__(self, master):
        self.master = master
        self.master.title("FMG - Folder Map Generator")
        self.master.geometry("500x300")
        self.master.resizable(False, False)

        self.settings = self.load_settings()
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.current_language = tk.StringVar(
            value=self.settings.get("language", "English")
        )
        self.dark_mode = tk.BooleanVar(value=self.settings.get("dark_mode", False))
        self.auto_open = tk.BooleanVar(value=True)
        self.last_generated_file = None
        print(f"Initial auto_open value: {self.auto_open.get()}")

        self.style = ttk.Style()
        self.icon_images = {}
        self.center_frame = None
        self.load_icons()
        self.create_widgets()
        self.update_language()
        self.apply_theme()

        self.default_input_path = os.path.expanduser("~")  # %HOMEPATH% su Windows
        self.default_output_path = os.path.abspath("./Mapped Folders")

        if not os.path.exists(self.default_output_path):
            os.makedirs(self.default_output_path)

        self.progress_bar = ttk.Progressbar(
            self.center_frame, orient=tk.HORIZONTAL, length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10, fill=tk.X)
        self.progress_bar.pack_forget()  # Nascondi inizialmente la barra di progresso

    def load_settings(self):
        # Simulate loading settings
        try:
            return {"language": "English", "dark_mode": False}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def load_icons(self):
        # Load all icons from the assets folder
        try:
            self.icon_images["app_icon"] = ImageTk.PhotoImage(
                Image.open("assets/FMG.icon.png").resize(
                    (16, 16), Image.Resampling.LANCZOS
                )
            )
            self.icon_images["input_icon"] = ImageTk.PhotoImage(
                Image.open("assets/FMG.input.icon.png").resize(
                    (16, 16), Image.Resampling.LANCZOS
                )
            )
            self.icon_images["output_icon"] = ImageTk.PhotoImage(
                Image.open("assets/FMG.output.icon.png").resize(
                    (16, 16), Image.Resampling.LANCZOS
                )
            )
            self.icon_images["exit_icon"] = ImageTk.PhotoImage(
                Image.open("assets/FMG.exit.icon.png").resize(
                    (16, 16), Image.Resampling.LANCZOS
                )
            )
        except Exception as e:
            print(f"Error loading icons: {e}")

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Crea il center_frame
        self.center_frame = ttk.Frame(self.main_frame)
        self.center_frame.pack(fill=tk.BOTH, expand=True)

        # Percorsi di default
        input_default = os.path.expandvars(r"%HOMEPATH%")
        output_default = os.path.abspath("./FMG - Mapped Folders")

        self.source_folder.set(input_default)
        self.output_folder.set(output_default)

        # Frame per input/output
        io_frame = ttk.Frame(self.main_frame)
        io_frame.pack(fill=tk.X, pady=10)

        # Configura la griglia responsiva
        io_frame.columnconfigure(1, weight=1)

        # Input Folder button
        self.input_button = ttk.Button(
            io_frame,
            text="Select Input",
            command=self.select_source_folder,
            image=self.icon_images.get("input_icon"),  # Use the input icon
            compound=tk.LEFT,
        )
        self.input_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Input Folder entry
        self.input_entry = ttk.Entry(
            io_frame, textvariable=self.source_folder, state="readonly"
        )
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Output Folder button
        self.output_button = ttk.Button(
            io_frame,
            text="Select Output",
            command=self.select_output_folder,
            image=self.icon_images.get("output_icon"),  # Use the output icon
            compound=tk.LEFT,
        )
        self.output_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Output Folder entry
        self.output_entry = ttk.Entry(
            io_frame, textvariable=self.output_folder, state="readonly"
        )
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Map Folder button
        self.map_button = ttk.Button(
            self.center_frame,
            text="Map Folder",
            command=self.generate_map,
            image=self.icon_images.get("app_icon"),
            compound=tk.LEFT,
        )
        self.map_button.pack(pady=10, fill=tk.X)

        # Frame per i nuovi pulsanti e la checkbox
        self.actions_frame = ttk.Frame(self.main_frame)
        self.actions_frame.pack(fill=tk.X, pady=(10, 0))

        # Frame inferiore per bottoni (!, ?, IT/EN, Modalità scura, Chiudi)
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)

        # Changelog button (!)
        self.changelog_button = ttk.Button(
            bottom_frame, text="!", width=3, command=self.show_changelog
        )
        self.changelog_button.pack(side=tk.LEFT, padx=5)

        # Help button (?)
        self.help_button = ttk.Button(
            bottom_frame, text="?", width=3, command=self.show_user_guide
        )
        self.help_button.pack(side=tk.LEFT, padx=5)

        # Language toggle button (IT/EN)
        self.toggle_lang_button = ttk.Button(
            bottom_frame,
            text="IT" if self.current_language.get() == "English" else "EN",
            width=3,
            command=self.toggle_language,
        )
        self.toggle_lang_button.pack(side=tk.LEFT, padx=5)

        # Toggle Dark Mode button
        self.toggle_dark_mode_button = ttk.Button(
            bottom_frame,
            text="🌞" if self.dark_mode.get() else "🌙",
            width=3,
            command=self.toggle_dark_mode,
        )
        self.toggle_dark_mode_button.pack(side=tk.LEFT, padx=5)

        # Frame per i nuovi pulsanti e la checkbox
        actions_frame = ttk.Frame(self.center_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))

        # Pulsante per aprire la cartella di output
        self.open_output_button = ttk.Button(
            self.actions_frame,
            text="Open Output Folder",
            command=self.open_output_folder,
        )
        self.open_output_button.pack(side=tk.LEFT, padx=(0, 5))

        # Pulsante per aprire il file generato
        self.open_file_button = ttk.Button(
            self.actions_frame,
            text="Open Generated File",
            command=self.open_generated_file,
        )
        self.open_file_button.pack(side=tk.LEFT, padx=5)

        # Checkbox per l'apertura automatica
        self.auto_open_check = ttk.Checkbutton(
            self.actions_frame,
            text="Auto-open file on completion",
            variable=self.auto_open,
            command=self.update_auto_open,
        )
        self.auto_open_check.pack(side=tk.LEFT, padx=5)

        # Close button
        self.close_button = ttk.Button(
            bottom_frame,
            text="Close FMG",
            command=self.master.quit,
            image=self.icon_images.get("exit_icon"),  # Use the exit icon
            compound=tk.LEFT,
        )
        self.close_button.pack(side=tk.RIGHT)

        # Link to "Support the developer", spostato in fondo e centrato
        link_frame = ttk.Frame(self.main_frame)
        link_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self.link_button = ttk.Label(
            link_frame,
            text="Support the developer: Antonio Bertuccio",
            cursor="hand2",
            foreground="blue",
            anchor="center",
        )
        self.link_button.pack(expand=True)
        self.link_button.bind("<Button-1>", lambda e: self.open_link())

    def create_link(master, text, command):
        link_frame = ttk.Frame(master)
        link_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)  # Riduci il padding
        link_button = ttk.Label(
            link_frame, text=text, cursor="hand2", foreground="blue", anchor="center"
        )
        link_button.pack(expand=True)
        link_button.bind("<Button-1>", lambda e: command())

    def select_source_folder(self):
        folder = filedialog.askdirectory(
            title="Select Input Folder", initialdir=self.default_input_path
        )
        if folder:
            self.source_folder.set(folder)
            print(f"Input folder selected: {folder}")

    def select_output_folder(self):
        folder = filedialog.askdirectory(
            title="Select Output Folder", initialdir=self.default_output_path
        )
        if folder:
            self.output_folder.set(folder)
            print(f"Output folder selected: {folder}")

    def update_auto_open(self):
        print(f"Auto-open updated. New value: {self.auto_open.get()}")  # Debug print

    def generate_map(self):
        print(f"Auto-open value at start: {self.auto_open.get()}")
        source_folder = self.source_folder.get() or self.default_input_path
        output_folder = self.output_folder.get() or self.default_output_path

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Usa il nome della cartella selezionata come nome del file di output
        folder_name = os.path.basename(source_folder)
        output_file = os.path.join(output_folder, f"{folder_name}_map.txt")

        # Controlla che il nome del file sia unico
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(
                output_folder, f"{folder_name}_map_{counter}.txt"
            )
            counter += 1

        self.last_generated_file = output_file  # Salva il percorso del file generato

        # Mostra la barra di progresso
        self.progress_bar.pack(pady=10, fill=tk.X)
        self.progress_bar["value"] = 0

        def update_progress(value):
            self.progress_bar["value"] = value
            self.master.update_idletasks()

        def on_completion(success, error_message):
            self.progress_bar.pack_forget()
            print(
                f"Completion callback. Success: {success}, Auto-open value: {self.auto_open.get()}"
            )  # Debug print
            if success:
                messagebox.showinfo(
                    translations[self.current_language.get()]["success"],
                    f"{translations[self.current_language.get()]['map_generated']}\n{output_file}",
                )
                if self.auto_open.get():
                    print(f"Attempting to open file: {self.last_generated_file}")
                    self.open_generated_file()
                else:
                    print("Auto-open is not checked")
            else:
                messagebox.showerror(
                    translations[self.current_language.get()]["error"],
                    f"{translations[self.current_language.get()]['error_occurred']}\n{error_message}",
                )

        generate_file_hierarchy_threaded(
            source_folder,
            output_file,
            translations,
            self.current_language.get(),
            update_progress,
            on_completion,
        )

    def open_output_folder(self):
        output_folder = self.output_folder.get() or self.default_output_path
        if os.path.exists(output_folder):
            if sys.platform == "win32":
                os.startfile(output_folder)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_folder])
            else:  # linux variants
                subprocess.Popen(["xdg-open", output_folder])
        else:
            messagebox.showerror("Error", "Output folder does not exist.")

    def open_generated_file(self):
        if self.last_generated_file and os.path.exists(self.last_generated_file):
            print(f"Opening file: {self.last_generated_file}")  # Log per debug
            if sys.platform == "win32":
                os.startfile(self.last_generated_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", self.last_generated_file])
            else:  # linux variants
                subprocess.Popen(["xdg-open", self.last_generated_file])
        else:
            print(f"File not found: {self.last_generated_file}")  # Log per debug
            messagebox.showerror(
                "Error", "No file has been generated yet or the file does not exist."
            )

    def show_changelog(self):
        # Logica per mostrare il changelog aggiornato
        changelog_text = """Changelog:
        - Version 1.0: Initial release.
        - Version 1.1: Added error handling.
        - Version 1.2: Improved folder mapping functionality.
        - Version 1.3: Added dark mode toggle.
        - Version 1.4: Moved 'Support the developer' to the bottom center.
        """
        changelog_window = tk.Toplevel(self.master)
        changelog_window.title("Changelog")
        changelog_window.geometry("400x300")

        changelog_label = tk.Text(changelog_window, wrap=tk.WORD)
        changelog_label.insert(tk.END, changelog_text)
        changelog_label.config(state=tk.DISABLED)
        changelog_label.pack(expand=True, fill=tk.BOTH)

    def show_user_guide(self):
        # Logica per mostrare la guida utente
        user_guide_text = """User Guide:
        1. Select the source folder.
        2. Select the output folder.
        3. Click 'Map Folder' to generate a map of the folder structure.
        4. Toggle dark mode or switch language if needed.
        """
        messagebox.showinfo("User Guide", user_guide_text)

    def toggle_language(self):
        new_lang = "Italiano" if self.current_language.get() == "English" else "English"
        self.current_language.set(new_lang)
        self.toggle_lang_button.config(text="IT" if new_lang == "English" else "EN")
        self.update_language()

    def update_language(self):
        lang = self.current_language.get()
        self.master.title(
            "FMG - Folder Map Generator"
            if lang == "English"
            else "FMG - Generatore Mappa Cartelle"
        )
        self.input_button.config(
            text="Select Input" if lang == "English" else "Seleziona Input"
        )
        self.output_button.config(
            text="Select Output" if lang == "English" else "Seleziona Output"
        )
        self.map_button.config(
            text="Map Folder" if lang == "English" else "Mappa Cartella"
        )
        self.close_button.config(
            text="Close FMG" if lang == "English" else "Chiudi FMG"
        )
        self.help_button.config(text="?" if lang == "English" else "?")
        self.changelog_button.config(text="!" if lang == "English" else "!")

    def toggle_dark_mode(self):
        self.dark_mode.set(not self.dark_mode.get())
        self.settings["dark_mode"] = self.dark_mode.get()
        self.toggle_dark_mode_button.config(text="🌞" if self.dark_mode.get() else "🌙")
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode.get():
            self.style.theme_use("clam")
            bg_color = "#2E2E2E"
            fg_color = "white"
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=bg_color, foreground=fg_color)
        else:
            self.style.theme_use("default")
            bg_color = self.style.lookup("TFrame", "background")
            fg_color = "black"
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background=bg_color, foreground=fg_color)

        # Aggiorna lo stile dei widget nel frame
        for widget in self.master.winfo_children():
            self._update_widget_colors(widget)

    def _update_widget_colors(self, widget):
        for child in widget.winfo_children():
            self._update_widget_colors(child)

    def open_link(self):
        import webbrowser

        webbrowser.open_new("https://ko-fi.com/antoniobertuccio")


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Set up logging
def setup_logging(log_file="fmg_log.log"):
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Main function to start the app
def main():
    setup_logging()  # Initialize logging
    try:
        root = tk.Tk()
        app = FolderMapGenerator(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
