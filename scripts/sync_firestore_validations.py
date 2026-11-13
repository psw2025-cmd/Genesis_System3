import os
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["SYSTEM3_FIRESTORE_PROJECT"] = "system3-openalgo-safe"

def sync_validations():
    try:
        from google.cloud import firestore
        db = firestore.Client(project="system3-openalgo-safe")
        val_dir = ROOT / "state" / "market_validations"
        count = 0
        for f in sorted(val_dir.glob("market_validation_*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                day = data.get("date") or f.stem.replace("market_validation_", "")
                if not day:
                    continue
                doc_ref = db.collection("market_validations").document(str(day))
                doc_ref.set(data, merge=True)
                print(f"Synced validation to Firestore: {day} -> rho={data.get('spearman_rho')}")
                count += 1
            except Exception as e:
                print(f"Error syncing {f.name}: {e}")
        print(f"Total synced: {count} validation days to Firestore.")
    except Exception as exc:
        print(f"Firestore Client Error: {exc}")

if __name__ == "__main__":
    sync_validations()
