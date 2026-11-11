import os

search_dir = r"c:\Genesis_System3_clean"
found = []
for root, dirs, files in os.walk(search_dir):
    if ".git" in root or ".venv" in root:
        continue
    for f in files:
        if "pnl" in f.lower() or "summary" in f.lower():
            found.append(os.path.join(root, f))

print(f"Found {len(found)} files:")
for f in found[:30]:
    print(f)
