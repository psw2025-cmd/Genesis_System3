import os

search_dir = r"c:\Genesis_System3_clean"
found = []
for root, dirs, files in os.walk(search_dir):
    if any(skip in root for skip in [".git", ".venv", "agent_deep_audit", "node_modules"]):
        continue
    for f in files:
        if f.endswith((".py", ".json", ".ts", ".tsx", ".js")):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    content = fl.read()
                    if "23053" in content:
                        found.append(p)
            except Exception:
                pass

print(f"Found in {len(found)} files:")
for f in found:
    print(f)
