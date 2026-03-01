"""
genesis_scheduler.py
====================
GENESIS SYSTEM3 — AUTO SCHEDULER
Runs the full pipeline every hour during NSE market hours:
  09:15 → 15:30 IST, Monday–Friday

Pipeline per cycle:
  1. angel_data_fetcher.py    → fetch live OHLCV + option chains
  2. live_train_and_rank.py   → retrain + rank → Top 5 signals
  3. Log results + optional Telegram alert

Run once at market open:
  .venv\Scripts\python.exe genesis_scheduler.py

Stop: Ctrl+C
"""

import os, sys, time, datetime, subprocess, json
import pytz

BASE_DIR   = r"C:\Genesis_System3"
OUTPUT_DIR = os.path.join(BASE_DIR, "storage", "signals")
LOG_DIR    = os.path.join(BASE_DIR, "logs", "scheduler")
PYTHON     = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
IST        = pytz.timezone('Asia/Kolkata')

os.makedirs(LOG_DIR, exist_ok=True)

# Market hours IST
MARKET_OPEN  = datetime.time(9, 15)
MARKET_CLOSE = datetime.time(15, 30)

# Telegram config (optional — fill to get alerts)
TELEGRAM_TOKEN  = ""   # "1234567890:ABCdef..."
TELEGRAM_CHAT_ID = ""  # "-1001234567890"


def is_market_open():
    now_ist = datetime.datetime.now(IST)
    if now_ist.weekday() >= 5:  # Saturday/Sunday
        return False
    t = now_ist.time()
    return MARKET_OPEN <= t <= MARKET_CLOSE


def run_script(script_name):
    """Run a python script and return (success, output)."""
    script_path = os.path.join(BASE_DIR, script_name)
    try:
        result = subprocess.run(
            [PYTHON, script_path],
            capture_output=True, text=True,
            timeout=300, cwd=BASE_DIR
        )
        success = result.returncode == 0
        output  = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT after 300s"
    except Exception as e:
        return False, str(e)


def send_telegram(message):
    """Send Telegram alert (optional)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
    except:
        pass


def format_top5_alert(json_path):
    """Format Top 5 signals as Telegram message."""
    try:
        with open(json_path) as f:
            data = json.load(f)
        
        top5 = data.get('top5', [])
        ts   = data.get('generated_at', '')
        
        if not top5:
            return f"⚪ <b>GENESIS SYSTEM3</b>\n{ts}\nNo BUY signals at threshold 0.72"
        
        lines = [f"🏆 <b>GENESIS SYSTEM3 — TOP 5 SIGNALS</b>", f"⏰ {ts}", ""]
        for i, r in enumerate(top5, 1):
            sym   = r.get('symbol','?')
            score = r.get('score', 0)
            ret   = r.get('oot_ret', 0)
            sharpe= r.get('oot_sharpe', 0)
            win   = r.get('win_rate', 0)
            lines.append(
                f"#{i} <b>{sym}</b> | Score: {score:.0f} | "
                f"Ret: {ret:+.1f}% | Sharpe: {sharpe:.1f} | Win: {win:.0f}%"
            )
        
        lines.append(f"\n📊 {data.get('total_symbols_scored',0)} symbols scored")
        lines.append(f"🎯 Threshold: {data.get('threshold', 0.72)}")
        return "\n".join(lines)
    except:
        return "Genesis signal update — check dashboard"


def run_full_pipeline():
    """Execute one full pipeline cycle."""
    now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
    print(f"\n{'='*65}")
    print(f"  🚀 PIPELINE START — {now}")
    print(f"{'='*65}")
    
    # Step 1: Fetch live data
    print("\n[1/2] Fetching Angel Broking live data...")
    ok1, out1 = run_script("angel_data_fetcher.py")
    status1 = "✓" if ok1 else "✗"
    print(f"  {status1} Data fetch {'complete' if ok1 else 'FAILED'}")
    if not ok1:
        print(f"  Error: {out1[-300:]}")
    
    # Step 2: Train + rank
    print("\n[2/2] Training models + generating Top 5...")
    ok2, out2 = run_script("live_train_and_rank.py")
    status2 = "✓" if ok2 else "✗"
    print(f"  {status2} Ranking {'complete' if ok2 else 'FAILED'}")
    
    # Print Top 5 summary
    latest_path = os.path.join(OUTPUT_DIR, "top5_LATEST.json")
    if os.path.exists(latest_path):
        with open(latest_path) as f:
            data = json.load(f)
        top5 = data.get('top5', [])
        
        print(f"\n  {'─'*55}")
        print(f"  TOP 5 THIS HOUR:")
        if top5:
            for i, r in enumerate(top5, 1):
                print(f"  #{i} {r.get('symbol','?'):<12} "
                      f"Score:{r.get('score',0):>5.1f}  "
                      f"Ret:{r.get('oot_ret',0):>+6.2f}%  "
                      f"Sharpe:{r.get('oot_sharpe',0):>6.2f}")
        else:
            print("  No BUY signals this hour.")
        
        # Telegram alert
        alert = format_top5_alert(latest_path)
        send_telegram(alert)
    
    # Log this run
    log_entry = {
        'timestamp': now,
        'fetch_ok':  ok1,
        'rank_ok':   ok2,
        'top5_count': len(top5) if ok2 else 0
    }
    log_path = os.path.join(LOG_DIR, "scheduler_log.jsonl")
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    print(f"\n  [✓] Run logged: {log_path}")
    return ok1 and ok2


def main():
    print("=" * 65)
    print("  GENESIS SYSTEM3 SCHEDULER — STARTED")
    print(f"  Market hours: 09:15–15:30 IST (Mon–Fri)")
    print(f"  Pipeline runs: Every hour on the hour")
    print(f"  Stop: Ctrl+C")
    print("=" * 65)
    
    run_count = 0
    
    while True:
        now_ist = datetime.datetime.now(IST)
        
        if is_market_open():
            # Run pipeline
            success = run_full_pipeline()
            run_count += 1
            
            # Wait until next hour (or 60 min)
            next_run = (now_ist + datetime.timedelta(hours=1)).replace(
                minute=0, second=30, microsecond=0)
            wait_sec = (next_run - datetime.datetime.now(IST)).total_seconds()
            wait_sec = max(60, min(wait_sec, 3600))
            
            print(f"\n  💤 Next run at {next_run.strftime('%H:%M IST')} "
                  f"({wait_sec/60:.0f} min)")
            time.sleep(wait_sec)
        
        else:
            # Outside market hours — check every 5 min
            open_time = now_ist.replace(hour=9, minute=15, second=0)
            if now_ist.time() < MARKET_OPEN:
                wait_sec = (open_time - now_ist).total_seconds()
                print(f"\r  ⏳ Market opens in {wait_sec/60:.0f} min "
                      f"({open_time.strftime('%H:%M IST')})    ", end='')
            else:
                print(f"\r  🔒 Market closed. Next open: tomorrow 09:15 IST    ", end='')
            time.sleep(300)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  [STOPPED] Scheduler shut down cleanly.")
