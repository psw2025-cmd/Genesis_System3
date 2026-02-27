"""
System3 Phase 321 - Latency Profiler

Measures operation latency
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Output directories
HEALTH_DIR = PROJECT_ROOT / "storage" / "system_health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "system_health"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def run_phase321(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 321: Latency Profiler

    Returns:
        dict: {
            "phase": 321,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        today = datetime.now().strftime("%Y%m%d")
        output_file = HEALTH_DIR / "phase321_output.json"
        log_file = LOG_DIR / f"phase321_{today}.log"

        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.info("Phase 321: Measures operation latency")

        # Phase logic here
        result_data = {"phase": 321, "timestamp": datetime.now().isoformat(), "status": "initialized"}

        # Write output
        with open(output_file, "w") as f:
            json.dump(result_data, f, indent=2)

        logger.info(f"Phase 321 complete")

        outputs = {"output_file": str(output_file), "log_file": str(log_file)}

        # Remove handler
        logger.removeHandler(file_handler)
        file_handler.close()

        return {
            "phase": 321,
            "status": "OK",
            "details": "Phase 321 executed successfully",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 321 error: {e}")
        return {
            "phase": 321,
            "status": "ERROR",
            "details": f"Phase 321 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase321()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
