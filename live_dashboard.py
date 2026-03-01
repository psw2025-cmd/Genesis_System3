"""
live_dashboard.py
=================
GENESIS SYSTEM3 — TERMINAL DASHBOARD
Shows Top 5 signals + market regime + option chain data
Refreshes every 60 seconds during market hours.

Run: .venv\Scripts\python.exe live_dashboard.py
"""

import os, json, time, datetime, glob
import pandas as pd

BASE_DIR    = r"C:\Genesis_System3"
SIGNALS_DIR = os.path.join(BASE_DIR, "storage", "signals")
CHAIN_DIR   = os.path.join(BASE_DIR, "storage", "data", "option_chains")
LIVE_DIR    = os.path.join(BASE_DIR, "storage", "data", "live")

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def load_top5():
    path = os.path.join(SIGNALS_DIR, "top5_LATEST.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def load_chain_signals():
    path = os.path.join(CHAIN_DIR, "chain_signals_LATEST.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def load_live_price(symbol):
    path = os.path.join(LIVE_DIR, f"{symbol}_live.csv")
    if not os.path.exists(path):
        return None, None
    try:
        df  = pd.read_csv(path, index_col=0, parse_dates=True)
        ltp = float(df['Close'].iloc[-1])
        chg = float((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100) if len(df)>1 else 0
        return ltp, chg
    except:
        return None, None

def is_market_open():
    now = datetime.datetime.now()
    if now.weekday() >= 5: return False
    t = now.time()
    return datetime.time(9,15) <= t <= datetime.time(15,30)

def render():
    clear()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    market = "🟢 MARKET OPEN" if is_market_open() else "🔴 MARKET CLOSED"

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       GENESIS SYSTEM3 — LIVE TRADING DASHBOARD                  ║")
    print(f"║  {now}                    {market}  ║")
    print("╠══════════════════════════════════════════════════════════════════╣")

    # Key indices
    indices = ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY"]
    print("║  INDEX PRICES                                                    ║")
    idx_line = "║  "
    for sym in indices:
        ltp, chg = load_live_price(sym)
        if ltp:
            arrow = "▲" if chg >= 0 else "▼"
            idx_line += f"{sym}:{ltp:,.0f} {arrow}{abs(chg):.2f}%  "
    print(f"{idx_line:<68}║")

    print("╠══════════════════════════════════════════════════════════════════╣")

    # Top 5
    data = load_top5()
    if not data:
        print("║  No signals file found.                                          ║")
        print("║  Run: .venv\\Scripts\\python.exe live_train_and_rank.py           ║")
    else:
        gen_at = data.get('generated_at','?')[:19]
        thresh = data.get('threshold', 0.60)
        scored = data.get('total_symbols_scored', 0)
        top5   = data.get('top5', [])

        print(f"║  🏆 TOP 5 BUY SIGNALS  (generated: {gen_at})           ║")
        print(f"║  Threshold: {thresh} | Symbols scored: {scored:<3}                          ║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        print("║  #  Symbol       Score  OOT Ret%  Sharpe  Win%  PCR Signal      ║")
        print("║  ─  ──────────   ─────  ────────  ──────  ────  ──────────      ║")

        if not top5:
            print("║  ⚠️  NO BUY SIGNALS at current threshold.                        ║")
            print(f"║     Best candidate from last run:                                ║")
            # Show best from all_rankings
            rank_files = sorted(glob.glob(os.path.join(SIGNALS_DIR,"all_rankings_*.csv")))
            if rank_files:
                df = pd.read_csv(rank_files[-1])
                df = df.sort_values('rank_score', ascending=False).head(3)
                for _, row in df.iterrows():
                    sym   = str(row.get('symbol','?'))
                    score = float(row.get('score', 0))
                    ret   = float(row.get('oot_ret', 0))
                    sh    = float(row.get('oot_sharpe', 0))
                    print(f"║     {sym:<12} Score:{score:>5.1f}  Ret:{ret:>+6.2f}%  Sh:{sh:>6.2f}        ║")
        else:
            chain_sigs = load_chain_signals()
            for i, r in enumerate(top5, 1):
                sym   = r.get('symbol','?')
                score = float(r.get('score', 0))
                ret   = float(r.get('oot_ret', 0))
                sh    = float(r.get('oot_sharpe', 0))
                win   = float(r.get('win_rate', 0))
                pcr_s = chain_sigs.get(sym, {}).get('pcr_signal', r.get('chain_pcr','N/A'))
                ltp, chg = load_live_price(sym)
                ltp_str = f"LTP:{ltp:,.1f}({chg:+.1f}%)" if ltp else ""
                print(f"║  {i}  {sym:<12}{score:>5.1f}  {ret:>+7.2f}%  {sh:>6.2f}  {win:>4.0f}%  {pcr_s:<10}  {ltp_str:<12}║")

        print("╠══════════════════════════════════════════════════════════════════╣")

        # Option chain summary
        chain_sigs = load_chain_signals()
        if chain_sigs:
            print("║  OPTION CHAIN SIGNALS                                            ║")
            print("║  Symbol      PCR    Signal    Max Pain    Support   Resistance   ║")
            print("║  ──────────  ─────  ────────  ─────────   ───────   ─────────   ║")
            shown = 0
            for sym in ["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","SBIN","AXISBANK"]:
                s = chain_sigs.get(sym, {})
                if not s: continue
                pcr  = s.get('pcr', 0)
                pcrs = s.get('pcr_signal','N/A')
                mp   = s.get('max_pain','N/A')
                sup  = s.get('support','N/A')
                res  = s.get('resistance','N/A')
                print(f"║  {sym:<10}  {pcr:>5.2f}  {pcrs:<8}  {str(mp):>9}   {str(sup):>7}   {str(res):>9}   ║")
                shown += 1
                if shown >= 5: break

    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  COMMANDS:                                                       ║")
    print("║  Refresh signals : .venv\\Scripts\\python.exe live_train_and_rank.py ║")
    print("║  Fetch new data  : .venv\\Scripts\\python.exe angel_data_fetcher.py  ║")
    print("║  Auto pipeline   : .venv\\Scripts\\python.exe genesis_scheduler.py   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\n  [Auto-refresh in 60s — Ctrl+C to stop]\n")


def main():
    print("Starting Genesis Dashboard... (Ctrl+C to exit)")
    while True:
        try:
            render()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n[Dashboard stopped]")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
