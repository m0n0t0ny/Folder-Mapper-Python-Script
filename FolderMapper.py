import os
import sys
import tkinter as tk
from tkinter import messagebox
import logging
from ui.main_window import FolderMapper

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    import ctypes

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def setup_logging(log_file="folder_mapper_log.log"):
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    setup_logging()  # Initialize logging
    try:
        root = tk.Tk()
        app = FolderMapper(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
