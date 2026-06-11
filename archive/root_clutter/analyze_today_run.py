"""Analyze today's System3 run and generate reports."""
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, Any, List, Tuple
import re

PROJECT_ROOT = Path(__file__).parent.absolute()
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Today's date
TODAY = datetime(2025, 12, 3).date()
TODAY_STR = TODAY.strftime("%Y%m%d")

def parse_log_timeline(log_file: Path) -> List[Dict[str, Any]]:
    """Parse master log and extract timeline events."""
    events = []
    if not log_file.exists():
        return events
    
    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            # Parse timestamp and message
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[(\w+)\] (.+)", line)
            if match:
                ts_str, level, msg = match.groups()
                try:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    events.append({
                        "time": ts,
                        "level": level,
                        "message": msg
                    })
                except:
                    pass
    return events

def analyze_master_log() -> Dict[str, Any]:
    """Analyze master log for today."""
    log_file = LOGS_DIR / f"system3_autorun_master_{TODAY_STR}.log"
    events = parse_log_timeline(log_file)
    
    timeline = []
    key_events = {
        "start_time": None,
        "pre_market_phases": [],
        "autopilot_start": None,
        "phase_runs": [],
        "op_cycles": [],
        "curated_refreshes": [],
        "archive_time": None,
        "eod_learning": None,
        "shutdown_time": None,
        "restarts": []
    }
    
    for event in events:
        msg = event["message"]
        ts = event["time"]
        
        if "SYSTEM3 AUTORUN MASTER - STARTING" in msg:
            key_events["start_time"] = ts
            timeline.append({"time": ts, "event": "Master started"})
        
        if "PRE-MARKET: Running phases" in msg:
            timeline.append({"time": ts, "event": "Pre-market phases started"})
            key_events["pre_market_phases"].append(ts)
        
        if "9:15 AM: Starting DRY-RUN Autopilot" in msg:
            key_events["autopilot_start"] = ts
            timeline.append({"time": ts, "event": "Autopilot started"})
        
        if "30-MIN INTERVAL: Running phases" in msg:
            timeline.append({"time": ts, "event": f"30-min phase run"})
            key_events["phase_runs"].append(ts)
        
        if "HOURLY: Running OP Cycle" in msg:
            timeline.append({"time": ts, "event": "OP cycle"})
            key_events["op_cycles"].append(ts)
        
        if "2-HOUR INTERVAL: Refreshing curated file" in msg:
            timeline.append({"time": ts, "event": "Curated file refresh"})
            key_events["curated_refreshes"].append(ts)
        
        if "3:30 PM: Archiving signals" in msg:
            key_events["archive_time"] = ts
            timeline.append({"time": ts, "event": "Signals archived"})
        
        if "3:35 PM: Running EOD Learning" in msg:
            key_events["eod_learning"] = ts
            timeline.append({"time": ts, "event": "EOD learning"})
        
        if "4:00 PM: Shutting down" in msg:
            key_events["shutdown_time"] = ts
            timeline.append({"time": ts, "event": "Shutdown initiated"})
        
        if "SYSTEM3 AUTORUN MASTER - SHUTDOWN COMPLETE" in msg:
            timeline.append({"time": ts, "event": "Shutdown complete"})
        
        if "Interrupted by user" in msg:
            timeline.append({"time": ts, "event": "User interrupt (Ctrl+C)"})
            key_events["restarts"].append({"time": ts, "reason": "user_interrupt"})
    
    return {
        "timeline": sorted(timeline, key=lambda x: x["time"]),
        "key_events": key_events,
        "total_events": len(events)
    }

def analyze_watchdog_log() -> Dict[str, Any]:
    """Analyze watchdog log for today."""
    log_file = LOGS_DIR / f"system3_watchdog_{TODAY_STR}.log"
    events = parse_log_timeline(log_file)
    
    watchdog_events = {
        "start_time": None,
        "shutdown_flag_detections": [],
        "restart_attempts": [],
        "market_hours_checks": []
    }
    
    for event in events:
        msg = event["message"]
        ts = event["time"]
        
        if "SYSTEM3 WATCHDOG - STARTING" in msg:
            watchdog_events["start_time"] = ts
        
        if "Shutdown flag detected" in msg:
            watchdog_events["shutdown_flag_detections"].append(ts)
        
        if "Master is NOT running - attempting restart" in msg:
            watchdog_events["restart_attempts"].append({"time": ts, "reason": "master_not_running"})
    
    return watchdog_events

def analyze_signals() -> Dict[str, Any]:
    """Analyze signal files for today."""
    signals_file = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"
    
    result = {
        "total_signals": 0,
        "buy_count": 0,
        "sell_count": 0,
        "hold_count": 0,
        "top_buy": [],
        "top_sell": [],
        "score_distribution": {},
        "file_exists": signals_file.exists()
    }
    
    if not signals_file.exists():
        return result
    
    try:
        df = pd.read_csv(signals_file, on_bad_lines="skip")
        if len(df) == 0:
            return result
        
        # Try to filter by date if timestamp column exists
        if "ts" in df.columns or "timestamp" in df.columns:
            ts_col = "ts" if "ts" in df.columns else "timestamp"
            df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
            today_df = df[df[ts_col].dt.date == TODAY]
        else:
            # Use all rows if no timestamp
            today_df = df
        
        result["total_signals"] = len(today_df)
        
        if "side" in today_df.columns:
            result["buy_count"] = len(today_df[today_df["side"].str.upper() == "BUY"])
            result["sell_count"] = len(today_df[today_df["side"].str.upper() == "SELL"])
            result["hold_count"] = len(today_df[today_df["side"].str.upper() == "HOLD"])
        
        if "final_score" in today_df.columns:
            result["top_buy"] = today_df[today_df["side"].str.upper() == "BUY"].nlargest(10, "final_score").to_dict("records")
            result["top_sell"] = today_df[today_df["side"].str.upper() == "SELL"].nlargest(10, "final_score").to_dict("records")
            result["score_distribution"] = {
                "min": float(today_df["final_score"].min()) if len(today_df) > 0 else 0,
                "max": float(today_df["final_score"].max()) if len(today_df) > 0 else 0,
                "mean": float(today_df["final_score"].mean()) if len(today_df) > 0 else 0
            }
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_hardened_behaviors() -> Dict[str, Any]:
    """Check hardened behaviors A-E."""
    master_file = PROJECT_ROOT / "system3_autorun_master.py"
    watchdog_file = PROJECT_ROOT / "system3_watchdog.py"
    heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
    shutdown_flag = PROJECT_ROOT / "system3_shutdown_flag.json"
    
    results = {}
    
    # A1: Restart loop prevention
    if master_file.exists():
        master_content = master_file.read_text(encoding="utf-8")
        results["A1_restart_loop_prevention"] = {
            "shutdown_flag_check": "check_shutdown_flag" in master_content,
            "shutdown_flag_write": "write_shutdown_flag" in master_content,
            "shutdown_completed_today": "shutdown_completed_today" in master_content
        }
    
    # A2: Market hours restriction
    if watchdog_file.exists():
        watchdog_content = watchdog_file.read_text(encoding="utf-8")
        results["A2_market_hours"] = {
            "is_market_hours": "is_market_hours()" in watchdog_content,
            "shutdown_flag_check": "check_shutdown_flag" in watchdog_content
        }
    
    # A3: Heartbeat freeze protection
    if master_file.exists():
        results["A3_heartbeat_freeze"] = {
            "heartbeat_errors": "heartbeat_errors" in master_content,
            "staleness_check": "frozen" in master_content.lower() or "stale" in master_content.lower()
        }
    
    # A4: Error detection & retry logic
    if master_file.exists():
        results["A4_retry_logic"] = {
            "network_retry": "ConnectionError" in master_content or "TimeoutError" in master_content,
            "file_lock_retry": "IOError" in master_content or "OSError" in master_content,
            "phase_retry": "max_retries" in master_content
        }
    
    # A5: DRY-RUN safety
    if master_file.exists():
        results["A5_dry_run_safety"] = {
            "safety_check": "enforce_safety_checks" in master_content,
            "live_trading_check": "LIVE_TRADING_ENABLED" in master_content
        }
    
    # Check actual files
    results["heartbeat_exists"] = heartbeat_file.exists()
    results["shutdown_flag_exists"] = shutdown_flag.exists()
    
    if heartbeat_file.exists():
        try:
            hb_data = json.loads(heartbeat_file.read_text(encoding="utf-8"))
            hb_ts = datetime.fromisoformat(hb_data.get("timestamp", ""))
            results["heartbeat_age_seconds"] = (datetime.now() - hb_ts).total_seconds()
            results["heartbeat_status"] = hb_data.get("status")
            results["autopilot_running"] = hb_data.get("autopilot_running")
        except:
            pass
    
    if shutdown_flag.exists():
        try:
            sf_data = json.loads(shutdown_flag.read_text(encoding="utf-8"))
            results["shutdown_date"] = sf_data.get("shutdown_date")
            results["shutdown_time"] = sf_data.get("shutdown_time")
        except:
            pass
    
    return results

def main():
    """Generate all reports."""
    print("Analyzing today's run...")
    
    master_analysis = analyze_master_log()
    watchdog_analysis = analyze_watchdog_log()
    signals_analysis = analyze_signals()
    hardened_check = check_hardened_behaviors()
    
    # Save results
    results = {
        "date": TODAY_STR,
        "master": master_analysis,
        "watchdog": watchdog_analysis,
        "signals": signals_analysis,
        "hardened_behaviors": hardened_check
    }
    
    results_file = DOCS_DIR / f"system3_{TODAY_STR}_analysis.json"
    results_file.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    
    print(f"Analysis complete. Results saved to {results_file}")
    return results

if __name__ == "__main__":
    main()

