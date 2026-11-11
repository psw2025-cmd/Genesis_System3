import re
from pathlib import Path

path = Path("src/ranking/daily_gain_scanner.py")
content = path.read_text(encoding="utf-8")

replacement = '''def load_chain_from_storage(symbol: str):
    """Load latest option chain for a symbol via DataSourceManager, chain_cache JSON, or stored CSV."""
    import pandas as pd

    # 1. Primary: Load via DataSourceManager (Dhan API client & live cache)
    try:
        from core.data.datasource_manager import DataSourceManager
        dsm = DataSourceManager()
        res = dsm.fetch_option_chain(symbol)
        if res:
            df, spot = res
            if df is not None and not df.empty:
                df = df.copy()
                df["spot_price"] = spot
                logger.info(f"[CHAIN] Successfully fetched option chain for {symbol} via DataSourceManager: {len(df)} rows, spot={spot}")
                return df
    except Exception as e:
        logger.debug(f"[CHAIN] DataSourceManager fetch error for {symbol}: {e}")

    # 2. Secondary: Load from state/chain_cache/{symbol}.json
    try:
        cache_file = os.path.join(ROOT_DIR, "state", "chain_cache", f"{symbol.upper()}.json")
        if os.path.isfile(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            strikes = data.get("strikes", [])
            spot = float(data.get("spot") or data.get("underlying_value") or 0.0)
            rows = []
            for s in strikes:
                for leg in ("ce", "pe"):
                    if leg in s and isinstance(s[leg], dict):
                        row = dict(s[leg])
                        row["strike"] = s.get("strike")
                        row["option_type"] = leg.upper()
                        row["spot_price"] = spot
                        rows.append(row)
            if rows:
                df = pd.DataFrame(rows)
                logger.info(f"[CHAIN] Loaded cached chain for {symbol} from state/chain_cache: {len(df)} rows, spot={spot}")
                return df
    except Exception as e:
        logger.debug(f"[CHAIN] chain_cache JSON load error for {symbol}: {e}")

    # 3. Tertiary: Legacy CSV scan in storage/ and storage/live/
    for folder in [os.path.join(ROOT_DIR, "storage"), os.path.join(ROOT_DIR, "storage", "live")]:
        if os.path.isdir(folder):
            candidates = sorted(
                [f for f in os.listdir(folder) if symbol.lower() in f.lower() and f.endswith(".csv")],
                reverse=True
            )
            if candidates:
                p = os.path.join(folder, candidates[0])
                try:
                    df = pd.read_csv(p)
                    if not df.empty:
                        logger.info(f"[CHAIN] Loaded legacy CSV chain for {symbol} from {p}: {len(df)} rows")
                        return df
                except Exception:
                    pass

    # Diagnostic log if all sources fail
    logger.warning(f"[CHAIN DIAGNOSTIC] Failed to obtain option chain for {symbol} | chain_source=DSM+chain_cache+storage | response_status=NO_DATA | records_received=0")
    return None'''

# Find the function def load_chain_from_storage
pattern = r"def load_chain_from_storage\(symbol: str\):.*?(?=\ndef load_spot_from_chain)"
new_content, count = re.subn(pattern, replacement + "\n\n", content, flags=re.DOTALL)
print(f"Replaced {count} occurrences")
assert count == 1, f"Expected 1 replacement, got {count}"
path.write_text(new_content, encoding="utf-8")
print("Successfully patched src/ranking/daily_gain_scanner.py")
