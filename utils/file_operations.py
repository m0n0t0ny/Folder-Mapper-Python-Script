import os


def generate_file_hierarchy(start_path, output_file, translations, lang):
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
