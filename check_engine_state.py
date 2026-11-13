import json

with open(r"c:\Genesis_System3_clean\outputs\paper_engine_state.json", "r", encoding="utf-8") as f:
    d = json.load(f)
    print("keys:", list(d.keys()))
    for k in ["summary", "pnl", "history", "trades", "sessions"]:
        if k in d:
            val = d[k]
            print(f"{k} type={type(val)} len={len(val) if isinstance(val, list) else 'N/A'}")
            if isinstance(val, list) and len(val) > 0:
                print(f"  sample {k}[0]:", val[0])
