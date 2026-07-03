"""
NSE Session — DISABLED.
All data now from DhanHQ API directly.
This file kept as stub for import compatibility.
"""
# NSE scraping removed — Dhan API used instead
# This prevents requests.Session pool from loading (~50MB)

def get_nse_session():
    """Deprecated — Dhan API used instead."""
    raise NotImplementedError("NSE scraping disabled. Use Dhan API.")

def fetch_option_chain_nse(symbol, expiry=None):
    """Deprecated — use core.data.nse_provider.get_option_chain() instead."""
    raise NotImplementedError("NSE scraping disabled. Use Dhan API.")
