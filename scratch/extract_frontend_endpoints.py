import os
import re

frontend_dir = "dashboard/frontend/src"
endpoints = set()

for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith((".ts", ".tsx", ".js", ".jsx")):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                c = fp.read()
            found = re.findall(r'[\'"`](/(?:api|ws)/[^\'"`\s?#]+)', c)
            for ep in found:
                endpoints.add(ep)

print(f"Total distinct frontend API endpoints: {len(endpoints)}")
for ep in sorted(endpoints):
    print(ep)
