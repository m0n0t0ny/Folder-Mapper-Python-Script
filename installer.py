import os
import sys
import subprocess
import platform


def get_desktop_path():
    """Get the path to the desktop based on the operating system."""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "Desktop")
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~"), "Desktop")
    else:  # Linux and other Unix-like systems
        return os.path.join(os.path.expanduser("~"), "Desktop")


def create_folder_mapper_directory():
    """Create the Folder Mapper directory on the desktop."""
    desktop_path = get_desktop_path()
    folder_mapper_path = os.path.join(desktop_path, "Folder Mapper")

    if not os.path.exists(folder_mapper_path):
        os.makedirs(folder_mapper_path)
        print(f"Created 'Folder Mapper' directory at: {folder_mapper_path}")
    else:
        print(f"'Folder Mapper' directory already exists at: {folder_mapper_path}")

    return folder_mapper_path


def clone_github_repo(destination):
    """Clone the GitHub repository to the specified destination."""
    repo_url = "https://github.com/m0n0t0ny/Folder-Mapper-Python-Script.git"
    try:
        subprocess.run(["git", "clone", repo_url, destination], check=True)
        print(f"Successfully cloned the repository to: {destination}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")
        sys.exit(1)


def main():
    folder_mapper_path = create_folder_mapper_directory()
    clone_github_repo(folder_mapper_path)
    print("Setup completed successfully!")


if __name__ == "__main__":
    main()
