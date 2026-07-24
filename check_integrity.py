import os

OLD_RENDER_URL = "http://127.0.0.1:8000"
NEW_LOCAL_URL = "http://127.0.0.1:8000"

# Directories aur extensions jo scan karni hain
TARGET_EXTENSIONS = {".yml", ".yaml", ".py", ".md", ".json", ".ts", ".mjs", ".sh"}
EXCLUDE_DIRS = {".git", "venv", "__pycache__", "reports", "state"}

print("==================================================")
print("     SYSTEM3 RENDER TO LOCAL URL ALIGNMENT SCRIPT   ")
print("==================================================")

updated_count = 0

for root, dirs, files in os.walk("."):
    # Unwanted folders skip karo
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext not in TARGET_EXTENSIONS:
            continue
            
        file_path = os.path.join(root, file)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            if OLD_RENDER_URL in content:
                new_content = content.replace(OLD_RENDER_URL, NEW_LOCAL_URL)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                updated_count += 1
                print(f" -> Aligned local URL in: {file_path}")
        except Exception as e:
            pass

print("==================================================")
print(f" -> [SUCCESS] Total files successfully aligned: {updated_count}")
print("==================================================")