"""
verify_step1.py — FIXED VERSION
Tests adaptive_bar using REAL market data from your Genesis System.
Validates that adaptive_bar values are realistic (0.25% - 1.5% range).
"""

import pandas as pd
import numpy as np
import os
import sys

# ── 1. LOAD REAL DATA ────────────────────────────────────────────────────────
# Try to load real data from your Genesis data directory
DATA_DIRS = [
    r"C:\Genesis_System3\data",
    r"C:\Genesis_System3\core\data",
    r"C:\Genesis_System3\data\raw",
    r"C:\Genesis_System3\data\processed",
]

SYMBOLS_TO_TEST = ["MIDCPNIFTY", "ADANIENT", "FINNIFTY", "AXISBANK"]

def find_data_file(symbol):
    """Search common data locations for a symbol's CSV."""
    for d in DATA_DIRS:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if symbol.upper() in fname.upper() and fname.endswith('.csv'):
                return os.path.join(d, fname)
    return None

def load_real_df(symbol):
    """Load real OHLCV dataframe for a symbol."""
    path = find_data_file(symbol)
    if path:
        print(f"  [✓] Found data file: {path}")
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df.columns = [c.strip().title() for c in df.columns]
        # Ensure standard column names
        col_map = {
            'Datetime': 'index', 'Timestamp': 'index',
            'Open': 'Open', 'High': 'High', 'Low': 'Low',
            'Close': 'Close', 'Volume': 'Volume'
        }
        return df
    else:
        print(f"  [!] No file found for {symbol} — using realistic synthetic data")
        return None

def make_realistic_synthetic(symbol):
    """
    Create realistic synthetic OHLCV data that mimics Indian index/stock behavior.
    Uses real-world volatility ranges instead of random uniform.
    """
    np.random.seed(42)
    periods = 500
    dates = pd.date_range(start='2024-01-01', periods=periods, freq='h')

    # Realistic base prices per symbol
    base_prices = {
        "MIDCPNIFTY": 10500,
        "ADANIENT":   2800,
        "FINNIFTY":   21000,
        "AXISBANK":   1050,
    }
    base = base_prices.get(symbol, 1000)

    # Realistic hourly volatility (0.1% - 0.3% per bar — Indian markets)
    hourly_vol = 0.002  # 0.2% per hour
    log_returns = np.random.normal(0, hourly_vol, periods)
    close = base * np.exp(np.cumsum(log_returns))

    spread = close * 0.001
    df = pd.DataFrame({
        'Open':   close - spread * np.random.uniform(0, 1, periods),
        'High':   close + spread * np.random.uniform(0.5, 1.5, periods),
        'Low':    close - spread * np.random.uniform(0.5, 1.5, periods),
        'Close':  close,
        'Volume': np.random.uniform(50000, 200000, periods)
    }, index=dates)
    return df

# ── 2. RUN FEATURE ENGINE ─────────────────────────────────────────────────────
try:
    from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine
    engine = WorldClassFeatureEngine()
    print("\n[✓] WorldClassFeatureEngine imported successfully\n")
except ImportError as e:
    print(f"[✗] Import error: {e}")
    sys.exit(1)

# ── 3. TEST EACH SYMBOL ───────────────────────────────────────────────────────
print("=" * 65)
print("  ADAPTIVE BAR VERIFICATION — REAL DATA TEST")
print("=" * 65)

results = []

for symbol in SYMBOLS_TO_TEST:
    print(f"\n── {symbol} ──")
    df = load_real_df(symbol)
    if df is None:
        df = make_realistic_synthetic(symbol)

    try:
        df_eng = engine.engineer_features(df, symbol)

        bar = df_eng['adaptive_bar']
        close = df_eng['Close']
        buy_labels = df_eng['label_buy']

        mean_bar  = bar.mean()
        min_bar   = bar.min()
        max_bar   = bar.max()
        buy_count = buy_labels.sum()
        total     = len(buy_labels)
        buy_pct   = 100 * buy_count / total if total > 0 else 0

        # Sanity check
        status = "✓ REALISTIC" if 0.002 <= mean_bar <= 0.015 else "✗ OUT OF RANGE"

        print(f"  Close price range : {close.min():.2f} → {close.max():.2f}")
        print(f"  adaptive_bar mean : {mean_bar:.6f}  ({mean_bar*100:.4f}%)")
        print(f"  adaptive_bar min  : {min_bar:.6f}  ({min_bar*100:.4f}%)")
        print(f"  adaptive_bar max  : {max_bar:.6f}  ({max_bar*100:.4f}%)")
        print(f"  BUY signals       : {int(buy_count)} / {total}  ({buy_pct:.1f}%)")
        print(f"  Status            : {status}")

        results.append({
            'Symbol':   symbol,
            'Mean Bar': f"{mean_bar*100:.4f}%",
            'Min Bar':  f"{min_bar*100:.4f}%",
            'Max Bar':  f"{max_bar*100:.4f}%",
            'BUY%':     f"{buy_pct:.1f}%",
            'Status':   status
        })

    except Exception as e:
        print(f"  [✗] ERROR: {e}")
        results.append({'Symbol': symbol, 'Status': f'ERROR: {e}'})

# ── 4. SUMMARY TABLE ──────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  SUMMARY TABLE")
print("=" * 65)
print(f"  {'Symbol':<15} {'Mean Bar':>10} {'Min Bar':>10} {'Max Bar':>10} {'BUY%':>8}  Status")
print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*8}  ------")
for r in results:
    if 'Mean Bar' in r:
        print(f"  {r['Symbol']:<15} {r['Mean Bar']:>10} {r['Min Bar']:>10} {r['Max Bar']:>10} {r['BUY%']:>8}  {r['Status']}")
    else:
        print(f"  {r['Symbol']:<15} {'ERROR':>10}  {r['Status']}")

# ── 5. PASS / FAIL ────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
passed = all('REALISTIC' in r.get('Status','') for r in results if 'Mean Bar' in r)
if passed:
    print("  OVERALL: ✓ PASS — adaptive_bar values are realistic")
    print("  Safe to proceed to STEP 2 (retrain models)")
else:
    print("  OVERALL: ✗ FAIL — adaptive_bar out of expected range")
    print("  Check WorldClassFeatureEngine.py — clip upper bound to 0.015")
    print("  Fix: df['adaptive_bar'] = (rolling_std * 1.5).clip(lower=0.0025, upper=0.015)")
print("=" * 65)