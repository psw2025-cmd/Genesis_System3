import json

with open(r"c:\Genesis_System3_clean\outputs\pnl_live.json", "r", encoding="utf-8") as f:
    d = json.load(f)
    print("keys:", list(d.keys()))
    print("summary:", d.get("summary"))
    print("history len:", len(d.get("history", [])))
    if d.get("history"):
        print("history[0]:", d["history"][0])
        print("history[-1]:", d["history"][-1])
