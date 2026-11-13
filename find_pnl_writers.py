import os

search_dir = r"c:\Genesis_System3_clean"
found = []
for root, dirs, files in os.walk(search_dir):
    if any(skip in root for skip in [".git", ".venv", "agent_deep_audit", "node_modules"]):
        continue
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    c = fl.read()
                    if "pnl_summary.json" in c:
                        found.append(p)
            except Exception:
                pass

print(f"Found {len(found)} scripts referencing pnl_summary.json:")
for f in found:
    print(f)
