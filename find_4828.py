import os

search_dir = r"c:\Genesis_System3_clean"
found = []
for root, dirs, files in os.walk(search_dir):
    if any(s in root for s in [".git", ".venv", "agent_deep_audit", "node_modules"]):
        continue
    for f in files:
        if f.endswith((".json", ".py", ".csv")):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    c = fl.read()
                    if "-4828" in c or "-321.88" in c:
                        found.append(p)
            except Exception:
                pass

print(f"Found in {len(found)} files:")
for f in found:
    print(f)
