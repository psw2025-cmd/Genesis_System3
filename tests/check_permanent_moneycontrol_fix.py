"""Verification script for Moneycontrol baked JSON permanent fix."""
import json
import os
import re
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    
    # 1. Verify .dockerignore
    dockerignore_path = root / ".dockerignore"
    if not dockerignore_path.exists():
        print(json.dumps({"verified": False, "error": ".dockerignore missing"}))
        sys.exit(1)
    dockerignore_text = dockerignore_path.read_text(encoding="utf-8", errors="replace")
    if "moneycontrol" not in dockerignore_text:
        print(json.dumps({"verified": False, "error": "moneycontrol not in .dockerignore"}))
        sys.exit(1)
        
    # 2. Verify moneycontrol_live.py
    service_file = root / "dashboard" / "backend" / "services" / "moneycontrol_live.py"
    if not service_file.exists():
        print(json.dumps({"verified": False, "error": "moneycontrol_live.py missing"}))
        sys.exit(1)
    from dashboard.backend.services.moneycontrol_live import get_live_data
    res = get_live_data()
    if res.get("_source") != "LIVE_API_PATH_B":
        print(json.dumps({"verified": False, "error": f"Unexpected source: {res.get('_source')}"}))
        sys.exit(1)
        
    # 3. Verify Dockerfile has no COPY of moneycontrol json
    dockerfile_path = root / "Dockerfile"
    dockerfile_text = dockerfile_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"COPY[^\n]*moneycontrol", dockerfile_text, re.IGNORECASE):
        print(json.dumps({"verified": False, "error": "Found COPY moneycontrol in Dockerfile"}))
        sys.exit(1)
        
    # 4. Verify PERMANENT_FIX_DONE.txt
    forensic_file = Path(r"C:\Temp\Genesis_Forensic\PERMANENT_FIX_DONE.txt")
    if not forensic_file.exists() or forensic_file.stat().st_size == 0:
        print(json.dumps({"verified": False, "error": "PERMANENT_FIX_DONE.txt missing or empty"}))
        sys.exit(1)
        
    print(json.dumps({"verified": True, "status": "ALL_CHECKS_PASSED"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
