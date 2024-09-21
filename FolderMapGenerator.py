import os
import sys
import tkinter as tk
import logging
from ui.main_window import FolderMapGenerator

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def setup_logging(log_file="fmg_log.log"):
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
        app = FolderMapGenerator(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        tk.messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
