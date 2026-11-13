import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

from dashboard.backend.autonomous_market_daemon import perform_market_sync_and_heal
from dashboard.backend.index_history_service import get_index_baseline

print("--- Testing Index Baselines ---")
for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX", "INDIAVIX"]:
    b = get_index_baseline(sym)
    print(f"{sym}: spot={b.get('spot')}, change={b.get('change')} ({b.get('change_pct')}%), pcr={b.get('pcr')}")

print("\n--- Running perform_market_sync_and_heal() ---")
res = perform_market_sync_and_heal()
print("Market sync result:", res)

# Verify chain_cache files
for sym in ["NIFTY", "BANKNIFTY"]:
    fpath = root_dir / "state" / "chain_cache" / f"{sym}.json"
    if fpath.exists():
        import json
        d = json.loads(fpath.read_text(encoding="utf-8"))
        print(f"\n{sym} chain_cache: spot={d.get('spot')}, atm={d.get('atm_strike')}, contracts={len(d.get('contracts') or [])}, status={d.get('status')}")
    else:
        print(f"\n{sym} chain_cache missing!")
