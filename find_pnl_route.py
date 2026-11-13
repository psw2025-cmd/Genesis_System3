import os

search_dir = r"c:\Genesis_System3_clean\dashboard\backend"
for root, dirs, files in os.walk(search_dir):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fl:
                    content = fl.read()
                    if "/api/pnl" in content or 'api.get("/pnl"' in content or 'get("/pnl"' in content or 'get_pnl' in content:
                        print(f"Match in {p}")
            except Exception:
                pass
