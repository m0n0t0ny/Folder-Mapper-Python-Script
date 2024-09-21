import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from ui.main_window import FolderMapGenerator


def main():
    try:
        root = tk.Tk()
        app = FolderMapGenerator(root)
        root.mainloop()
    except Exception as e:
        tk.messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
