import threading
import os
import logging


def generate_file_hierarchy(start_path, output_file, translations, lang):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{translations[lang]['folder_map_of']} {start_path}\n")
            f.write("=" * 50 + "\n")
            for root, dirs, files in os.walk(start_path):
                level = root.replace(start_path, "").count(os.sep)
                indent = "│   " * (level - 1) + "├── " if level > 0 else ""
                f.write(f"{indent}{os.path.basename(root)}/\n")
                for i, file in enumerate(files):
                    sub_indent = "│   " * level
                    if i == len(files) - 1 and len(dirs) == 0:
                        sub_indent += "└── "
                    else:
                        sub_indent += "├── "
                    f.write(f"{sub_indent}{file}\n")
            logging.info(f"Folder map successfully generated at {output_file}.")
    except Exception as e:
        logging.error(f"Error generating folder hierarchy: {e}")
        raise


# New function to run in a separate thread
def generate_file_hierarchy_threaded(
    start_path, output_file, translations, lang, callback=None
):
    def target():
        generate_file_hierarchy(start_path, output_file, translations, lang)
        if callback:
            callback()  # This will execute once the operation is complete

    # Create and start the thread
    thread = threading.Thread(target=target)
    thread.start()
