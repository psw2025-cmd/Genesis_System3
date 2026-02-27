"""
Convenience script to run the System3 Auto-Test Generator.

Usage:
    python system3_generate_tests.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the generator
if __name__ == "__main__":
    from core.tools.system3_auto_test_generator import main
    sys.exit(main())

