import json
from pathlib import Path

def inspect_details():
    top_ce_pe_path = Path("state/market_top_ce_pe.json")
    if top_ce_pe_path.exists():
        with open(top_ce_pe_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        for seg in ["NIFTY", "BANKNIFTY"]:
            if seg in d:
                data = d[seg]
                print(f"=== {seg} in market_top_ce_pe ===")
                print(f"  keys: {list(data.keys())}")
                if "top_ce" in data:
                    print(f"  top_ce count: {len(data['top_ce'])}")
                    if data["top_ce"]:
                        print(f"  top_ce[0]: {data['top_ce'][0]}")
                if "top_pe" in data:
                    print(f"  top_pe count: {len(data['top_pe'])}")
                    if data["top_pe"]:
                        print(f"  top_pe[0]: {data['top_pe'][0]}")

    mc_path = Path("state/moneycontrol_option_gainers.json")
    if mc_path.exists():
        with open(mc_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        table = d.get("market_top_table", [])
        print(f"\n=== moneycontrol_option_gainers table count: {len(table)} ===")
        for row in table[:3]:
            print(f"  row: {row}")

if __name__ == "__main__":
    inspect_details()
