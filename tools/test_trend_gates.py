import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dashboard.backend.accuracy_trend_service import build_accuracy_trend_payload
from dashboard.backend.auto_gates_service import build_auto_gates_report

trend = build_accuracy_trend_payload(ROOT, retrain_needed=False)
print("=== ACCURACY TREND ===")
print("days_available:", trend.get("days_available"))
print("avg_rho:", trend.get("avg_rho"))
print("status:", trend.get("status"))

gates = build_auto_gates_report(refresh=True, live_state=None)
print("=== AUTO GATES ===")
print("gates count:", len(gates.get("proof_gates", [])))
for g in gates.get("proof_gates", []):
    print(f"  {g['name']}: pass={g['pass']}, note={g.get('note')}")
