
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from SmartApi.smartConnect import SmartConnect
    print("SmartAPI import: OK")
    # Don't actually login, just check import
    print("SmartAPI login check: SKIPPED (dry-run mode)")
except ImportError as e:
    print(f"SmartAPI not available: {e}")
    sys.exit(1)
except Exception as e:
    print(f"SmartAPI check error: {e}")
    sys.exit(1)
