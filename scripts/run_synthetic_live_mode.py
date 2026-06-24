"""
Run Synthetic Live Mode - Continuously updates market data to simulate live trading
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    """Run synthetic data generator in a loop"""
    script_path = Path("scripts") / "generate_synthetic_live_data.py"

    if not script_path.exists():
        print(f"ERROR: {script_path} not found")
        return

    print("=" * 80)
    print("SYNTHETIC LIVE MODE - Simulating Live Market Conditions")
    print("=" * 80)
    print("This will continuously update market data every 5 seconds")
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"[Cycle {cycle}] Generating synthetic market data...", end=" ")

            # Run the generator script
            result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, cwd=Path.cwd())

            if result.returncode == 0:
                print("✅ Success")
                # Extract key info from output
                if "contracts" in result.stdout:
                    print(f"   {result.stdout.strip().split(chr(10))[-1]}")
            else:
                print("❌ Failed")
                print(f"   Error: {result.stderr}")

            # Wait 5 seconds before next update
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nStopped by user")
        print("=" * 80)


if __name__ == "__main__":
    main()
