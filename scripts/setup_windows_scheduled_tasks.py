"""Genesis System3 — Windows Scheduled Tasks Manager."""

import os
import subprocess
import sys

TASKS = [
    {
        "name": "GenesisSystem3_AutoSupervisor",
        "command": r"C:\Genesis_System3_Runtime\START_SYSTEM3.bat",
        "schedule": "ONLOGON",
        "description": "Genesis System3 Local Supervisor startup on user logon",
    },
    {
        "name": "GenesisSystem3_DhanTokenRotator",
        "command": r'C:\Python310\python.exe C:\Users\ADMIN\Genesis_System3\Genesis_System3\scripts\local_dhan_token_rotate.py',
        "schedule": "DAILY",
        "time": "08:30",
        "description": "Daily Dhan Token Refresh at 08:30 IST",
    },
    {
        "name": "GenesisSystem3_DailyBackup",
        "command": r'C:\Python310\python.exe C:\Genesis_System3_Runtime\backup_state.py',
        "schedule": "DAILY",
        "time": "23:45",
        "description": "Daily State Backup at 23:45 IST",
    },
    {
        "name": "GenesisSystem3_LogRotator",
        "command": r'C:\Python310\python.exe C:\Genesis_System3_Runtime\rotate_logs.py',
        "schedule": "DAILY",
        "time": "00:05",
        "description": "Daily Log Rotation and Drive Sync at 00:05 IST",
    },
]

def register_tasks():
    print("=" * 70)
    print("   GENESIS SYSTEM3 — WINDOWS SCHEDULED TASKS REGISTRATION")
    print("=" * 70)

    for t in TASKS:
        name = t["name"]
        sched = t["schedule"]
        cmd = t["command"]
        print(f"\n[*] Configuring task: {name}")

        # Check existing
        chk = subprocess.run(["schtasks", "/query", "/tn", name], capture_output=True, text=True)
        if chk.returncode == 0:
            print(f"    [OK] Task already registered.")
        else:
            if sched == "ONLOGON":
                sch_args = ["schtasks", "/create", "/tn", name, "/tr", cmd, "/sc", "ONLOGON", "/f"]
            else:
                st_time = t.get("time", "08:00")
                sch_args = ["schtasks", "/create", "/tn", name, "/tr", cmd, "/sc", "DAILY", "/st", st_time, "/f"]

            res = subprocess.run(sch_args, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"    [OK] Registered successfully ({sched} {t.get('time', '')}).")
            else:
                print(f"    [WARN] Registration notice: {res.stderr.strip() or res.stdout.strip()}")

    print("\n" + "=" * 70)
    print("   [OK] Task configuration reconciled.")
    print("=" * 70)

if __name__ == "__main__":
    register_tasks()
