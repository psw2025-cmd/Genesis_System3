"""
angel_data_fetcher.py — PRODUCTION v4 (API-DRIVEN)
==================================================
Unified Data Fetcher using Angel One (SmartAPI) for:
1. OHLCV Historical Data (Indices & Equities)
2. Option Chains (Real-time Greeks, OI, Volume via Broker API)

This version removes the unstable NSE scraping logic.
"""

import os, sys, time, json, datetime
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Ensure project root in path
ROOT_DIR = r"C:\Genesis_System3"
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger

# Configuration Paths
BASE_DIR    = ROOT_DIR
LIVE_DIR    = os.path.join(BASE_DIR, "storage", "data", "live")
CHAIN_DIR   = os.path.join(BASE_DIR, "storage", "data", "option_chains")
LOG_DIR     = os.path.join(BASE_DIR, "logs")

os.makedirs(LIVE_DIR,  exist_ok=True)
os.makedirs(CHAIN_DIR, exist_ok=True)
os.makedirs(LOG_DIR,   exist_ok=True)

# Symbols Configuration
NSE_SYMBOLS = {
    "NIFTY":      ("NFO", "99926000"), # Exchange NFO for options, NSE for spot
    "BANKNIFTY":  ("NFO", "99926009"),
    "FINNIFTY":   ("NFO", "99926037"),
    "MIDCPNIFTY": ("NFO", "99926074"),
    "RELIANCE":   ("NFO", "2885"),
    "HDFCBANK":   ("NFO", "1333"),
    "ICICIBANK":  ("NFO", "4963"),
    "INFY":       ("NFO", "1594"),
    "TCS":        ("NFO", "11536"),
    "SBIN":       ("NFO", "3045"),
    "AXISBANK":   ("NFO", "5900"),
    "KOTAKBANK":  ("NFO", "1922"),
    "LT":         ("NFO", "11483"),
    "ADANIENT":   ("NFO", "25"),
    "BHARTIARTL": ("NFO", "10604"),
    "WIPRO":      ("NFO", "3787"),
    "HCLTECH":    ("NFO", "7229"),
    "SUNPHARMA":  ("NFO", "3351"),
    "TATAMOTORS": ("NFO", "3456"),
    "MARUTI":     ("NFO", "10999"),
    "ASIANPAINT": ("NFO", "236"),
    "BAJFINANCE": ("NFO", "317"),
    "HINDUNILVR": ("NFO", "1394"),
    "NTPC":       ("NFO", "11630"),
}
BSE_SYMBOLS   = {"SENSEX": ("BFO", "99919000")}
ALL_SYMBOLS   = {**NSE_SYMBOLS, **BSE_SYMBOLS}

# Indices for specific processing
INDICES = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
EQUITIES = [s for s in ALL_SYMBOLS.keys() if s not in INDICES]

def fetch_ohlcv(broker, symbol, exchange, token, days=730):
    """Fetch OHLCV data via Angel One API."""
    # Note: For OHLCV, we use NSE/BSE exchange, not NFO/BFO
    actual_exchange = "NSE" if exchange == "NFO" else ("BSE" if exchange == "BFO" else exchange)
    
    end   = datetime.datetime.now()
    start = end - datetime.timedelta(days=days)
    try:
        resp = broker.smart.getCandleData({
            "exchange": actual_exchange, 
            "symboltoken": token,
            "interval": "ONE_HOUR",
            "fromdate": start.strftime("%Y-%m-%d %H:%M"),
            "todate":   end.strftime("%Y-%m-%d %H:%M"),
        })
        if resp['status'] and resp['data']:
            df = pd.DataFrame(resp['data'],
                columns=['Datetime','Open','High','Low','Close','Volume'])
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df.set_index('Datetime')
            for c in ['Open','High','Low','Close','Volume']:
                df[c] = pd.to_numeric(df[c])
            return df
    except Exception as e:
        print(f"err:{e}", end=' ')
    return None

def fetch_angel_option_chain(broker, symbol, exchange="NFO"):
    """Fetch option chain from Angel One API."""
    try:
        chain = broker.get_option_chain_by_underlying(symbol, exchange=exchange)
        if chain and len(chain) > 0:
            df = pd.DataFrame(chain)
            # Normalize column names for downstream signals
            if 'bidPrice' in df.columns: df = df.rename(columns={'bidPrice': 'bid'})
            if 'offerPrice' in df.columns: df = df.rename(columns={'offerPrice': 'ask'})
            # Ensure oi_change exists (Angel provides current OI, change is calculated by diffing snapshots)
            if 'oi_change' not in df.columns:
                df['oi_change'] = 0.0
            return df
        return None
    except Exception as e:
        print(f"  [Angel err: {e}]", end=' ')
        return None

def compute_signals(chain_df, price):
    """Calculate PCR, Max Pain, and Support/Resistance from chain data."""
    if chain_df is None or len(chain_df) == 0:
        return {}
    
    # Filter for nearest expiry (already done by broker.get_option_chain_by_underlying)
    ce = chain_df[chain_df['option_type'] == 'CE']
    pe = chain_df[chain_df['option_type'] == 'PE']
    s  = {}

    # 1. Put-Call Ratio (OI based)
    ce_oi = ce['oi'].sum() if 'oi' in ce.columns else 0
    pe_oi = pe['oi'].sum() if 'oi' in pe.columns else 0
    
    if pd.isna(ce_oi): ce_oi = 0
    if pd.isna(pe_oi): pe_oi = 0
    
    s['pcr']        = round(pe_oi / (ce_oi + 1e-9), 3)
    s['pcr_signal'] = ('BULLISH' if s['pcr'] < 0.7 else
                       'BEARISH' if s['pcr'] > 1.3 else 'NEUTRAL')

    # 2. IV Skew (at the money)
    # Find strike closest to price
    if not chain_df.empty and price > 0:
        atm_strike = chain_df.iloc[(chain_df['strike'] - price).abs().argsort()[:1]]['strike'].values[0]
        ce_iv = ce[ce['strike']==atm_strike]['iv'].mean() if 'iv' in ce.columns else 0
        pe_iv = pe[pe['strike']==atm_strike]['iv'].mean() if 'iv' in pe.columns else 0
        
        ce_iv = ce_iv if pd.notna(ce_iv) else 0
        pe_iv = pe_iv if pd.notna(pe_iv) else 0
        
        s['iv_skew']  = round(float(pe_iv - ce_iv), 3)
        s['iv_signal'] = ('BEARISH' if s['iv_skew'] > 2 else
                          'BULLISH' if s['iv_skew'] < -2 else 'NEUTRAL')
    else:
        s['iv_skew'] = 0
        s['iv_signal'] = 'NEUTRAL'

    # 3. Max Pain Calculation
    strikes = sorted(chain_df['strike'].unique()) if 'strike' in chain_df.columns else []
    pain = {}
    if strikes and price > 0:
        for st in strikes:
            # Sum loss for CE (if price > strike) and PE (if price < strike)
            cp_oi = ce[ce['strike'] <= st]['oi'].sum() if 'oi' in ce.columns else 0
            pp_oi = pe[pe['strike'] >= st]['oi'].sum() if 'oi' in pe.columns else 0
            
            cp = float(cp_oi if pd.notna(cp_oi) else 0) * max(0, st - price)
            pp = float(pp_oi if pd.notna(pp_oi) else 0) * max(0, price - st)
            pain[st] = cp + pp
    
    if pain:
        s['max_pain']          = min(pain, key=pain.get)
        s['max_pain_diff_pct'] = round((s['max_pain'] - price) / price * 100, 2)

    # 4. Support and Resistance (Highest OI strikes)
    # Use idxmax() only if there are valid (non-null) OI values
    if not ce.empty and 'oi' in ce.columns and ce['oi'].notna().any():
        idx = ce['oi'].idxmax()
        if pd.notna(idx):
            s['resistance'] = float(ce.loc[idx, 'strike'])
    
    if not pe.empty and 'oi' in pe.columns and pe['oi'].notna().any():
        idx = pe['oi'].idxmax()
        if pd.notna(idx):
            s['support'] = float(pe.loc[idx, 'strike'])
        
    s['oi_momentum'] = 'NEUTRAL' # Requires historical comparison
    return s

def run():
    print("=" * 70)
    print("  GENESIS SYSTEM3 — PRODUCTION DATA FETCHER v4")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # Initialize AngelOneBroker (Authenticated API)
        broker = AngelOneBroker(allow_data_only=True)
    except Exception as e:
        print(f"[CRITICAL] Broker Initialization Failed: {e}")
        return False

    ts      = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    summary = []

    # ── 1. OHLCV (HISTORICAL) ────────────────────────────────────────────────
    print(f"\n[1/2] Fetching OHLCV ({len(ALL_SYMBOLS)} symbols) via API...")
    for sym, (exch, tok) in ALL_SYMBOLS.items():
        print(f"  {sym}...", end=' ', flush=True)
        # Use broker.smart for direct API access if needed, or wrap in broker method
        df = fetch_ohlcv(broker, sym, exch, tok)
        if df is not None and len(df) > 50:
            df.to_csv(os.path.join(LIVE_DIR, f"{sym}_live.csv"))
            print(f"✓ {len(df)} bars")
            summary.append({'symbol': sym, 'status': 'OK', 'bars': len(df)})
        else:
            print("✗")
            summary.append({'symbol': sym, 'status': 'FAILED', 'bars': 0})
        time.sleep(0.2) # API Rate limit protection

    # ── 2. OPTION CHAINS (REAL-TIME API) ──────────────────────────────────────
    print(f"\n[2/2] Fetching option chains via Angel API...")
    
    all_signals = {}
    all_option_symbols = INDICES + EQUITIES

    for sym in all_option_symbols:
        exch = ALL_SYMBOLS[sym][0]
        print(f"  {sym}...", end=' ', flush=True)
        
        # Use the robust API method from our broker class
        chain = fetch_angel_option_chain(broker, sym, exchange=exch)

        if chain is not None and len(chain) > 0:
            chain.to_csv(os.path.join(CHAIN_DIR, f"{sym}_chain_{ts}.csv"), index=False)

            # Get latest price from OHLCV or chain spot
            live_f = os.path.join(LIVE_DIR, f"{sym}_live.csv")
            if os.path.exists(live_f):
                price = float(pd.read_csv(live_f, index_col=0)['Close'].iloc[-1])
            else:
                price = float(chain['spot_price'].iloc[0]) if 'spot_price' in chain.columns else 0.0

            if price > 0:
                sigs = compute_signals(chain, price)
                all_signals[sym] = {'price': price, 'rows': len(chain), **sigs}
                print(f"✓ {len(chain)} contracts | "
                      f"PCR:{sigs.get('pcr',0):.2f} {sigs.get('pcr_signal','')} | "
                      f"MaxPain:{sigs.get('max_pain','?')}")
            else:
                print("✗ No price")
                all_signals[sym] = {}
        else:
            print("✗ API No data")
            all_signals[sym] = {}
        
        # API Rate limit protection is built into broker.py (exponential backoff)
        # but we add a small throttle here to be safe
        time.sleep(0.1)

    # Save signals for Dashboard/Ranker
    for fname in [f"chain_signals_{ts}.json", "chain_signals_LATEST.json"]:
        with open(os.path.join(CHAIN_DIR, fname), 'w') as f:
            json.dump(all_signals, f, indent=2, default=str)

    ok  = sum(1 for s in summary if s['status']=='OK')
    chains_ok = sum(1 for v in all_signals.values() if v.get('rows',0) > 0)

    print(f"\n[✓] OHLCV: {ok}/{len(ALL_SYMBOLS)} | Option Chains: {chains_ok}/{len(all_option_symbols)}")
    print(f"[READY] .venv\\Scripts\\python.exe live_train_and_rank.py")
    return True

if __name__ == "__main__":
    run()
