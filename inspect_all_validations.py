import glob, json, os

files = sorted(glob.glob("c:/Genesis_System3_clean/state/*validations/*.json"))
print(f"Found {len(files)} validation files:")
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fl:
            text = fl.read()
            end = text.rfind("}")
            if end != -1:
                text = text[:end+1]
            d = json.loads(text)
            dt = d.get("date") or os.path.basename(f)
            rho = d.get("spearman_correlation") or d.get("rho")
            hit = d.get("hit_rate")
            status = d.get("status")
            trades = d.get("walk_forward_trades") or d.get("trades") or []
            print(f"  {os.path.basename(f)}: date={dt} rho={rho} hit={hit} status={status} trades_count={len(trades) if isinstance(trades, list) else trades}")
    except Exception as e:
        print(f"  {os.path.basename(f)}: ERROR {e}")
