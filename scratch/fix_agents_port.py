from pathlib import Path

p = Path("AGENTS.md")
text = p.read_text(encoding="utf-8")
old = "## 🚨 RULE 0: LOCAL FIRST, CLOUD SECOND\n1. **Staging is Local Laptop (localhost:8008)**"
new = "## 🚨 RULE 0: LOCAL FIRST, CLOUD SECOND\n1. **Staging is Local Laptop (127.0.0.1:8000 / localhost:8008)**"
if old in text:
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")
    print("Added 127.0.0.1:8000 to AGENTS.md")
else:
    # Try another pattern
    text = text.replace("localhost:8008", "127.0.0.1:8000 / localhost:8008", 1)
    p.write_text(text, encoding="utf-8")
    print("Replaced first localhost:8008 in AGENTS.md")
