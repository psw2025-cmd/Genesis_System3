import json

with open("c:/Genesis_System3_clean/state/market_validations/market_validation_2026-11-09.json", "r", encoding="utf-8") as f:
    text = f.read()
    end = text.rfind("}")
    if end != -1:
        text = text[:end+1]
    d = json.loads(text)
    print("keys in market_validation_2026-11-09:", list(d.keys()))
    for k in ["summary", "costed_walkforward", "trades", "pnl", "metrics"]:
        if k in d:
            print(f"Key {k}:", type(d[k]))
