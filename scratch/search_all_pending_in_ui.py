import os
import re

frontend_dir = "dashboard/frontend/src"
pending_usages = []

for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith((".ts", ".tsx")):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines):
                if "PENDING" in line or "pending" in line.lower():
                    # clean line
                    sline = line.strip()
                    if not sline.startswith("//") and not sline.startswith("/*"):
                        pending_usages.append({
                            "file": f,
                            "line": idx + 1,
                            "code": sline[:120]
                        })

print(f"Total occurrences of PENDING/pending in frontend: {len(pending_usages)}\n")
by_file = {}
for u in pending_usages:
    by_file.setdefault(u["file"], []).append(u)

for fname, items in by_file.items():
    print(f"[{fname}] {len(items)} occurrences:")
    for it in items[:4]:
        print(f"   Line {it['line']}: {it['code']}")
    if len(items) > 4:
        print(f"   ... and {len(items) - 4} more")
    print()
