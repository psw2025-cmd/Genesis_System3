from pathlib import Path

p = Path("AGENTS.md")
text = p.read_text(encoding="utf-8")
old = "1. **Stage 1 (Local):** The local laptop C:\\Genesis_System3_Clean is the absolute truth."
new = "1. **Stage 1 (Local):** The local laptop C:\\Genesis_System3_Clean (127.0.0.1:8000 / localhost:8008) is the absolute truth."
if old in text:
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")
    print("Updated line 4 of AGENTS.md successfully")
else:
    print("old not found in AGENTS.md")
