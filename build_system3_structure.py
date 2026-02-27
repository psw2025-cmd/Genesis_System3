import os

ROOT = os.getcwd()

FOLDERS = [
    "config",
    "core",
    "core/data",
    "core/models",
    "core/engine",
    "core/utils",
    "storage",
    "storage/history",
    "storage/live",
    "logs",
    "tests",
    "docs",
]

FILES = {
    "README.md": "# GENESIS SYSTEM 3\n\nAutomated trading system initialized.\n",
    "SYSTEM3_PROGRESS_LOG.md": "## System3 Build Log\n\n- Project initialized.\n",
    "config/__init__.py": "",
    "core/__init__.py": "",
    "core/data/__init__.py": "",
    "core/models/__init__.py": "",
    "core/engine/__init__.py": "",
    "core/utils/__init__.py": "",
    "core/engine/main_launcher.py": "print('Genesis System 3 Launcher Loaded')",
}

def create_structure():
    print("Creating folders...")
    for folder in FOLDERS:
        path = os.path.join(ROOT, folder)
        os.makedirs(path, exist_ok=True)
        print(f" - Created: {path}")

    print("\nCreating files...")
    for file_path, content in FILES.items():
        full_path = os.path.join(ROOT, file_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" - File written: {full_path}")

    print("\nSystem 3 project structure completed successfully!")

if __name__ == "__main__":
    create_structure()
