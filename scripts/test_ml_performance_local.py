import sys
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dashboard" / "backend"))

from dashboard.backend.routers.ml import _validation_truth_payload
truth = _validation_truth_payload()
print("ML VALIDATION TRUTH:")
print(" - ready_for_live:", truth.get("ready_for_live"))
print(" - rho:", truth.get("rho"))
print(" - hit_rate:", truth.get("hit_rate"))
print(" - reason:", truth.get("ready_for_live_reason"))
print(" - checklist items count:", len(truth.get("validations_checklist", [])))
for item in truth.get("validations_checklist", []):
    print(f"    * {item.get('label')}: pass={item.get('pass')} ({item.get('detail')})")
