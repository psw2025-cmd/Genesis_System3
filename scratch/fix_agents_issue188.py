from pathlib import Path

p = Path("AGENTS.md")
text = p.read_text(encoding="utf-8")
addition = "\n- Architecture note: Issue #188 is historical and not a mandatory bus on local laptop."
if "Issue #188 is historical" not in text:
    text = text.rstrip() + addition + "\n"
    p.write_text(text, encoding="utf-8")
    print("Added Issue #188 note to AGENTS.md")
else:
    print("Note already present")
