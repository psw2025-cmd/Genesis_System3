from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
for p in root.rglob("*.py"):
    if ".venv" in str(p) or ".git" in str(p):
        continue
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "gates_passing" in txt or "auto_gates" in txt:
            for i, l in enumerate(txt.splitlines()):
                if "stale" in l.lower() and ("gate" in l.lower() or "auto" in l.lower()):
                    print(f"{p.relative_to(root)} L{i+1}: {l.strip()[:100]}")
    except Exception:
        pass
