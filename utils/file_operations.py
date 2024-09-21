import os
import threading
import queue
import logging


def generate_file_hierarchy(
    start_path, output_file, translations, lang, progress_callback=None
):
    try:
        total_items = sum(
            [len(files) + len(dirs) for _, dirs, files in os.walk(start_path)]
        )
        processed_items = 0

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{translations[lang]['folder_map_of']} {start_path}\n")
            f.write("=" * 50 + "\n")
            for root, dirs, files in os.walk(start_path):
                level = root.replace(start_path, "").count(os.sep)
                indent = "│   " * (level - 1) + "├── " if level > 0 else ""
                f.write(f"{indent}{os.path.basename(root)}/\n")
                processed_items += 1
                if progress_callback:
                    progress_callback(processed_items / total_items * 100)

                for i, file in enumerate(files):
                    sub_indent = "│   " * level
                    if i == len(files) - 1 and len(dirs) == 0:
                        sub_indent += "└── "
                    else:
                        sub_indent += "├── "
                    f.write(f"{sub_indent}{file}\n")
                    processed_items += 1
                    if progress_callback:
                        progress_callback(processed_items / total_items * 100)

        logging.info(f"Folder map successfully generated at {output_file}.")
    except Exception as e:
        logging.error(f"Error generating folder hierarchy: {e}")
        raise


def generate_file_hierarchy_threaded(
    start_path,
    output_file,
    translations,
    lang,
    progress_callback=None,
    completion_callback=None,
):
    def target():
        try:
            generate_file_hierarchy(
                start_path, output_file, translations, lang, progress_callback
            )
            if completion_callback:
                completion_callback(True, None)
        except Exception as e:
            if completion_callback:
                completion_callback(False, str(e))

    thread = threading.Thread(target=target)
    thread.start()
    return thread
