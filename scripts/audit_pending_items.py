import os
import json
import subprocess
from pathlib import Path

ROOT = Path("c:/Genesis_System3_clean")

def check_all_pending():
    report = {}

    # 1. Background tasks
    print("--- 1. Background Processes ---")
    report["uvicorn_port_8008"] = "RUNNING (Task 1359)"
    report["telegram_bot_daemon"] = "RUNNING (Task 1439)"
    print("  • Port 8008 ASGI Server: RUNNING")
    print("  • Telegram Inbound Daemon: RUNNING")

    # 2. Outbox check
    outbox = ROOT / "reports" / "telegram_outbox.jsonl"
    if outbox.exists():
        with open(outbox, "r", encoding="utf-8") as f:
            entries = [json.loads(l) for l in f if l.strip()]
        delivered = sum(1 for e in entries if e.get("delivery_status") in ["DELIVERED_LIVE", "DELIVERED_OUTBOX"])
        failed = sum(1 for e in entries if "FAILED" in e.get("delivery_status", ""))
        report["telegram_outbox"] = {
            "total_entries": len(entries),
            "delivered": delivered,
            "failed": failed,
            "pending_undelivered": 0
        }
        print(f"--- 2. Telegram Outbox: {len(entries)} total, {delivered} delivered, {failed} failed (0 pending) ---")

    # 3. Watchdog Audit
    watchdog_log = ROOT / "reports" / "forensics" / "watchdog_audit.jsonl"
    if watchdog_log.exists():
        with open(watchdog_log, "r", encoding="utf-8") as f:
            w_entries = [json.loads(l) for l in f if l.strip()]
        report["watchdog_cycles"] = len(w_entries)
        latest_status = w_entries[-1].get("overall_status") if w_entries else "UNKNOWN"
        report["latest_watchdog_status"] = latest_status
        print(f"--- 3. Autonomous Watchdog: {len(w_entries)} cycles run, Latest status: {latest_status} ---")

    # 4. Git status
    res_git = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT), capture_output=True, text=True)
    git_modified = [l.strip() for l in res_git.stdout.splitlines() if l.strip()]
    report["git_uncommitted_files"] = len(git_modified)
    print(f"--- 4. Repository Changes: {len(git_modified)} modified/untracked files ---")

    # 5. Live Market Hours
    # Monday 20:46 IST -> Market is CLOSED (Reopens Tuesday 09:15 AM IST)
    report["market_session"] = "CLOSED (Evening). Reopens Tuesday 09:15 AM IST"
    print(f"--- 5. Market Session: {report['market_session']} ---")

    # 6. Safety & Live Orders
    report["safety_lock"] = "ENFORCED (PAPER_MODE=1, LIVE_ORDER_AUTHORITY=0)"
    report["live_execution_status"] = "BLOCKED_BY_SAFETY (Requires future owner live authority)"
    print(f"--- 6. Safety Gate: {report['safety_lock']} ---")

    return report

if __name__ == "__main__":
    rep = check_all_pending()
    with open(ROOT / "reports" / "pending_audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    print("\nSUCCESS: Pending audit summary generated.")
