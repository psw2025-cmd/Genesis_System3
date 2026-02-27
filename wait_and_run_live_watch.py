"""
wait_and_run_live_watch.py

Scheduler script for Genesis_System3.

Usage (from project root after activating venv):

    (venv) C:\Genesis_System3> python wait_and_run_live_watch.py

This will:
- Calculate the next 09:15 (IST, based on your Windows clock)
- Show a countdown in the console
- At 09:15, automatically start the same Angel One
  index options LIVE watch loop as menu option 7
  in run_system3.py.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# -------------------------------------------------------------------
# 1) Ensure project root is on sys.path (same pattern as run_system3)
# -------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# -------------------------------------------------------------------
# 2) Import the SAME main() that menu option 7 uses
#    In run_system3.py:
#       from core.engine.angel_options_watch_loop import main as angel_options_watch_loop_main
# -------------------------------------------------------------------
from core.engine.angel_options_watch_loop import main as angel_live_watch_main


# -------------------------------------------------------------------
# 3) Configuration: target time (market start)
# -------------------------------------------------------------------
TARGET_HOUR = 9      # 09:15
TARGET_MINUTE = 15   # 09:15


def get_next_run_time() -> datetime:
    """
    Return the next datetime at which we should start the live watch.

    If current time is already past today's 09:15, schedule for tomorrow 09:15.
    """
    now = datetime.now()
    target = now.replace(
        hour=TARGET_HOUR,
        minute=TARGET_MINUTE,
        second=0,
        microsecond=0,
    )

    # If already past target time today, move to tomorrow
    if now >= target:
        target = target + timedelta(days=1)

    return target


def wait_until(target: datetime) -> None:
    """
    Sleep in chunks until the target time is reached.
    Shows a simple countdown in the console.
    """
    while True:
        now = datetime.now()
        if now >= target:
            break

        remaining_sec = int((target - now).total_seconds())
        if remaining_sec < 0:
            break

        mins = remaining_sec // 60
        secs = remaining_sec % 60

        print(
            f"[Scheduler] Waiting {mins:02d}m {secs:02d}s "
            f"until {target.strftime('%Y-%m-%d %H:%M:%S')}...",
            end="\r",
        )

        # Sleep in 60-second chunks when far from target,
        # then in 5-second chunks when close.
        if remaining_sec > 300:
            time.sleep(60)
        else:
            time.sleep(5)

    print("\n[Scheduler] Target time reached.")


def main():
    # 1) Decide when to start
    target = get_next_run_time()
    print(
        "[Scheduler] Will start Angel One index options LIVE watch loop at: "
        f"{target.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 2) Wait until that time
    wait_until(target)

    # 3) Start the same continuous loop as menu option 7
    print("[Scheduler] Starting Angel One index options LIVE watch loop now...")
    print("           (same as menu option 7 in run_system3.py)")
    print("           Leave this window open; press Ctrl + C to stop in the evening.\n")

    # This will keep running until you manually stop it
    angel_live_watch_main()


if __name__ == "__main__":
    main()
