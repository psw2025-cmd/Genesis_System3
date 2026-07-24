import os

OLD_URL = "http://127.0.0.1:8000"
NEW_URL = "http://127.0.0.1:8000"

EXCLUDE_DIRS = {".git", "venv", "__pycache__", "reports", "state"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".ico", ".pdf", ".zip", ".lock"}

updated_files = 0

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        if os.path.splitext(file)[1].lower() in EXCLUDE_EXTS:
            continue
        file_path = os.path.join(root, file)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if OLD_URL in content:
                new_content = content.replace(OLD_URL, NEW_URL)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                updated_files += 1
                print(f" -> Patched URL in: {file_path}")
        except Exception as e:
            pass

print(f"\n[SUCCESS] Successfully replaced Render URLs with Localhost in {updated_files} files!")