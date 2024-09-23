import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from PIL import Image, ImageTk
import webbrowser
from utils.file_operations import generate_file_hierarchy_threaded
from utils.settings import load_settings, save_settings
from localization.translations import translations
from typing import Dict, Any


class FolderMapper:
    def __init__(self, master: tk.Tk):
        """
        🚀 Initialize Folder Mapper
        """
        self.master = master
        self.master.title("Folder Mapper")
        self.master.resizable(False, False)

        # ===== Initialize variables =====
        self.settings = self.load_settings()
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.current_language = tk.StringVar(
            value=self.settings.get("language", "English")
        )
        self.dark_mode = tk.BooleanVar(value=self.settings.get("dark_mode", False))
        self.auto_open = tk.BooleanVar(value=True)
        self.last_generated_file: str | None = None

        self.style = ttk.Style()
        self.icon_images: Dict[str, ImageTk.PhotoImage] = {}

        # ===== Initialize the interface =====
        self.load_icons()
        self.create_widgets()
        self.update_language()
        self.apply_theme()

        # ===== Set default paths =====
        self.default_input_path = os.path.expanduser("~")
        self.default_output_path = os.path.abspath("./Mapped Folders")
        if not os.path.exists(self.default_output_path):
            os.makedirs(self.default_output_path)

    # ===== WIDGET CREATION METHODS =====

    def create_widgets(self) -> None:
        """
        🏗️ Create all widgets for the application
        """
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_top_frame()
        self.create_io_frame()
        self.create_action_buttons()
        self.create_bottom_widgets()

    def create_top_frame(self) -> None:
        """
        🔝 Create the top frame with changelog, help, and toggle buttons
        """
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Changelog and help buttons on the left
        left_buttons_frame = ttk.Frame(top_frame)
        left_buttons_frame.pack(side=tk.LEFT)

        self.changelog_button = ttk.Button(
            left_buttons_frame, text="!", width=3, command=self.show_changelog
        )
        self.changelog_button.pack(side=tk.LEFT, padx=(0, 5))

        self.help_button = ttk.Button(
            left_buttons_frame, text="?", width=3, command=self.show_user_guide
        )
        self.help_button.pack(side=tk.LEFT)

        # Toggle buttons on the right
        right_buttons_frame = ttk.Frame(top_frame)
        right_buttons_frame.pack(side=tk.RIGHT)

        self.toggle_lang_button = ttk.Button(
            right_buttons_frame,
            text="IT" if self.current_language.get() == "English" else "EN",
            width=3,
            command=self.toggle_language,
        )
        self.toggle_lang_button.pack(side=tk.LEFT, padx=(0, 5))

        self.toggle_dark_mode_button = ttk.Button(
            right_buttons_frame,
            text="🌞" if self.dark_mode.get() else "🌙",
            width=3,
            command=self.toggle_dark_mode,
        )
        self.toggle_dark_mode_button.pack(side=tk.LEFT)

    def create_io_frame(self) -> None:
        """
        📂 Create the input/output frame with folder selection buttons and entries
        """
        io_frame = ttk.Frame(self.main_frame)
        io_frame.pack(fill=tk.X, pady=10)
        io_frame.columnconfigure(1, weight=1)

        # Input Folder
        self.input_button = ttk.Button(
            io_frame,
            text="Select Input",
            command=self.select_source_folder,
            image=self.icon_images.get("input_icon"),
            compound=tk.LEFT,
        )
        self.input_button.grid(row=0, column=0, pady=5, sticky="ew")

        self.input_entry = ttk.Entry(
            io_frame, textvariable=self.source_folder, state="readonly"
        )
        self.input_entry.grid(row=0, column=1, pady=5, sticky="ew")

        # Output Folder
        self.output_button = ttk.Button(
            io_frame,
            text="Select Output",
            command=self.select_output_folder,
            image=self.icon_images.get("output_icon"),
            compound=tk.LEFT,
        )
        self.output_button.grid(row=1, column=0, pady=5, sticky="ew")

        self.output_entry = ttk.Entry(
            io_frame, textvariable=self.output_folder, state="readonly"
        )
        self.output_entry.grid(row=1, column=1, pady=5, sticky="ew")

    def create_action_buttons(self) -> None:
        """
        🎬 Create action buttons: Map Folder, Open Output Folder, and Auto-open checkbox
        """
        # Map Folder button
        self.map_button = ttk.Button(
            self.main_frame,
            text="Map Folder",
            command=self.generate_map,
            image=self.icon_images.get("app_icon"),
            compound=tk.LEFT,
        )
        self.map_button.pack(pady=10, fill=tk.X)

        # Frame for other buttons and checkbox
        self.actions_frame = ttk.Frame(self.main_frame)
        self.actions_frame.pack(fill=tk.X, pady=(0, 10))

        self.open_output_button = ttk.Button(
            self.actions_frame,
            text="Open Output Folder",
            command=self.open_output_folder,
        )
        self.open_output_button.pack(side=tk.LEFT, padx=(0, 5))

        self.auto_open_check = ttk.Checkbutton(
            self.actions_frame,
            text="Auto-open file on completion",
            variable=self.auto_open,
            command=self.update_auto_open,
        )
        self.auto_open_check.pack(side=tk.LEFT, padx=5)

    def create_bottom_widgets(self) -> None:
        """
        👇 Create bottom widgets: Close button and developer support link
        """
        self.close_button = ttk.Button(
            self.main_frame,
            text="Close Folder Mapper",
            command=self.master.quit,
            image=self.icon_images.get("exit_icon"),
            compound=tk.LEFT,
        )
        self.close_button.pack(side=tk.BOTTOM, pady=(10, 0))

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

    # ===== EVENT HANDLING METHODS =====

    def select_source_folder(self) -> None:
        """
        📁 Open a dialog to select the source folder
        """
        folder = filedialog.askdirectory(
            title="Select Input Folder", initialdir=self.default_input_path
        )
        if folder:
            self.source_folder.set(folder)

    def select_output_folder(self) -> None:
        """
        💾 Open a dialog to select the output folder
        """
        folder = filedialog.askdirectory(
            title="Select Output Folder", initialdir=self.default_output_path
        )
        if folder:
            self.output_folder.set(folder)

    def update_auto_open(self) -> None:
        """
        🔄 Update the auto-open setting when the checkbox is clicked
        """
        print(f"Auto-open updated. New value: {self.auto_open.get()}")

    def generate_map(self) -> None:
        """
        🗺️ Generate the folder map
        """
        source_folder = self.source_folder.get() or self.default_input_path
        output_folder = self.output_folder.get() or self.default_output_path

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        folder_name = os.path.basename(source_folder)
        output_file = os.path.join(output_folder, f"{folder_name}_map.txt")

        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(
                output_folder, f"{folder_name}_map_{counter}.txt"
            )
            counter += 1

        self.last_generated_file = output_file

        self.show_progress_bar()
        generate_file_hierarchy_threaded(
            source_folder,
            output_file,
            translations,
            self.current_language.get(),
            self.update_progress,
            self.on_map_generation_complete,
        )

    def show_progress_bar(self) -> None:
        """
        📊 Show the progress bar during map generation
        """
        self.progress_bar = ttk.Progressbar(
            self.main_frame, orient=tk.HORIZONTAL, length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10, fill=tk.X)

    def update_progress(self, value: float) -> None:
        """
        📈 Update the progress bar value
        """
        self.progress_bar["value"] = value
        self.master.update_idletasks()

    def on_map_generation_complete(
        self, success: bool, error_message: str | None
    ) -> None:
        """
        🏁 Handle the completion of map generation
        """
        self.progress_bar.pack_forget()
        if success:
            messagebox.showinfo(
                translations[self.current_language.get()]["success"],
                f"{translations[self.current_language.get()]['map_generated']}\n{self.last_generated_file}",
            )
            if self.auto_open.get():
                self.open_generated_file()
        else:
            messagebox.showerror(
                translations[self.current_language.get()]["error"],
                f"{translations[self.current_language.get()]['error_occurred']}\n{error_message}",
            )

    def open_output_folder(self) -> None:
        """
        📂 Open the output folder in the file explorer
        """
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

    def open_generated_file(self) -> None:
        """
        📄 Open the generated map file
        """
        if self.last_generated_file and os.path.exists(self.last_generated_file):
            if sys.platform == "win32":
                os.startfile(self.last_generated_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", self.last_generated_file])
            else:  # linux variants
                subprocess.Popen(["xdg-open", self.last_generated_file])
        else:
            messagebox.showerror(
                "Error", "No file has been generated yet or the file does not exist."
            )

    def show_changelog(self) -> None:
        """
        📜 Show the changelog in a new window
        """
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

    def show_user_guide(self) -> None:
        """
        📘 Show the user guide in a message box
        """
        user_guide_text = """User Guide:
        1. Select the source folder.
        2. Select the output folder.
        3. Click 'Map Folder' to generate a map of the folder structure.
        4. Toggle dark mode or switch language if needed.
        """
        messagebox.showinfo("User Guide", user_guide_text)

    def toggle_language(self) -> None:
        """
        🌐 Toggle between English and Italian languages
        """
        new_lang = "Italiano" if self.current_language.get() == "English" else "English"
        self.current_language.set(new_lang)
        self.toggle_lang_button.config(text="IT" if new_lang == "English" else "EN")
        self.update_language()

    def toggle_dark_mode(self) -> None:
        """
        🌓 Toggle between light and dark mode
        """
        self.dark_mode.set(not self.dark_mode.get())
        self.settings["dark_mode"] = self.dark_mode.get()
        self.toggle_dark_mode_button.config(text="🌞" if self.dark_mode.get() else "🌙")
        self.apply_theme()

    def open_link(self) -> None:
        """
        🔗 Open the developer's Ko-fi page in a web browser
        """
        webbrowser.open_new("https://ko-fi.com/antoniobertuccio")

    # ===== UTILITY METHODS =====

    def load_settings(self) -> Dict[str, Any]:
        """
        ⚙️ Load application settings
        """
        try:
            return load_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def load_icons(self) -> None:
        """
        🖼️ Load application icons
        """
        try:
            icon_files = {
                "app_icon": "assets/folder-mapper-icon.png",
                "input_icon": "assets/folder-mapper-input-icon.png",
                "output_icon": "assets/folder-mapper-output-icon.png",
                "exit_icon": "assets/folder-mapper-exit-icon.png",
            }
            for key, path in icon_files.items():
                self.icon_images[key] = ImageTk.PhotoImage(
                    Image.open(path).resize((16, 16), Image.Resampling.LANCZOS)
                )
        except Exception as e:
            print(f"Error loading icons: {e}")

    def update_language(self) -> None:
        """
        🌍 Update the language of all UI elements
        """
        lang = self.current_language.get()
        self.master.title("Folder Mapper" if lang == "English" else "Folder Mapper")
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
        self.open_output_button.config(
            text=(
                "Open Output Folder" if lang == "English" else "Apri Cartella di Output"
            )
        )
        self.auto_open_check.config(
            text=(
                "Auto-open file on completion"
                if lang == "English"
                else "Apri file automaticamente al completamento"
            )
        )
        self.link_button.config(
            text=(
                "☕ Support the developer"
                if lang == "English"
                else "☕ Supporta lo sviluppatore"
            )
        )

    def apply_theme(self) -> None:
        """
        🎨 Apply the current theme (light or dark) to all UI elements
        """
        if self.dark_mode.get():
            self.style.theme_use("clam")
            bg_color = "#2E2E2E"
            fg_color = "white"
            entry_bg = "#4A4A4A"
        else:
            self.style.theme_use("default")
            bg_color = self.style.lookup("TFrame", "background")
            fg_color = "black"
            entry_bg = "white"

        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TCheckbutton", background=bg_color, foreground=fg_color)

        self.master.configure(bg=bg_color)
        self.main_frame.configure(style="TFrame")
        self.link_button.configure(
            foreground="light blue" if self.dark_mode.get() else "blue"
        )

        # Update all widgets
        for widget in self.master.winfo_children():
            self._update_widget_colors(widget)

    def _update_widget_colors(self, widget):
        """
        🖌️ Recursively update colors of all widgets
        """
        widget_type = widget.winfo_class()
        if widget_type in ("Frame", "Label", "Button"):
            widget.configure(bg=self.style.lookup("TFrame", "background"))
        if widget_type in ("Label", "Button"):
            widget.configure(fg=self.style.lookup("TLabel", "foreground"))
        if widget_type == "Entry":
            widget.configure(
                readonlybackground=self.style.lookup("TEntry", "fieldbackground")
            )

        for child in widget.winfo_children():
            self._update_widget_colors(child)


# Main function to start the app
def main():
    """
    🚀 Main function to start the FolderMapGenerator application
    """
    setup_logging()  # Initialize logging
    try:
        root = tk.Tk()
        app = FolderMapGenerator(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


# Set up logging
def setup_logging(log_file="folder-mapper_log.log"):
    """
    📝 Set up logging for the application
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    main()
