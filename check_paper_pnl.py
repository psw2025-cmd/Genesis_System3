import json

with open(r"c:\Genesis_System3_clean\outputs\paper_pnl_summary.json", "r", encoding="utf-8") as f:
    text = f.read()
    # Strip any trailing markdown
    end = text.rfind("}")
    if end != -1:
        text = text[:end+1]
    d = json.loads(text)
    print("paper_pnl_summary keys:", list(d.keys()))
    print("history count:", len(d.get("history", [])))
    if d.get("history"):
        print("sample history[0]:", d["history"][0])
        print("sample history[-1]:", d["history"][-1])
