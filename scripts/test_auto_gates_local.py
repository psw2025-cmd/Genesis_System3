import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dashboard" / "backend"))

from dashboard.backend.auto_gates_service import build_auto_gates_report

rep = build_auto_gates_report(refresh=True)
print("STATUS:", rep.get("status"))
print("GATES PASSING:", rep.get("gates_passing"), "/", rep.get("gates_total"))
print("OPEN BLOCKERS:", rep.get("open_blockers"))
for p in rep.get("proof_gates", []):
    print(f" - [{p.get('status')}] {p.get('label')}: {p.get('note')}")
