import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from core.data.datasource_manager import DataSourceManager
from src.ranking.gain_rank_engine import GainRankEngine

dsm = DataSourceManager()
all_data = {}
spots = {}

for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
    res = dsm.fetch_option_chain(sym)
    if res:
        df, spot = res
        df["spot_price"] = spot
        all_data[sym] = df
        spots[sym] = spot
        print(f"Loaded {sym}: {len(df)} option rows | Spot: {spot}")
    else:
        print(f"Failed to load {sym}")

print("Running GainRankEngine...")
engine = GainRankEngine(top_n=3)
ranked = engine.rank_all(all_data, spots)
top3 = engine.get_top_n(all_data, spots)

print(f"Ranked DataFrame shape: {ranked.shape}")
print("Top 3 Predictions:")
for p in top3:
    print(f"  #{p['rank']} {p['underlying']} | score={p['gain_score']:.2f} | expected_move={p['expected_move_pct']*100:.2f}% | rec={p['recommendation']}")
