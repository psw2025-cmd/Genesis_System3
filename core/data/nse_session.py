"""
Hardened NSE public API session helpers.

NSE often returns HTML 404 pages to naked or legacy API calls. The live option-chain
page works in a browser because cookies/session are established first.

As of 2025–2026 NSE migrated index option chains from:
  /api/option-chain-indices?symbol=NIFTY
to:
  /api/option-chain-contract-info?symbol=NIFTY  (expiry list)
  /api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=DD-Mon-YYYY

This module:
  - warms session (option-chain page — homepage often 403 from Akamai)
  - resolves nearest expiry via contract-info when not supplied
  - uses option-chain-v3 (falls back to legacy indices URL)
  - validates JSON content-type before parse
  - detects HTML error bodies
  - retries once with a fresh session
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

NSE_BASE = "https://www.nseindia.com"
NSE_OPTION_CHAIN_PAGE = f"{NSE_BASE}/option-chain"
NSE_OPTION_CHAIN_LEGACY = f"{NSE_BASE}/api/option-chain-indices?symbol={{symbol}}"
NSE_CONTRACT_INFO_API = f"{NSE_BASE}/api/option-chain-contract-info?symbol={{symbol}}"
NSE_OPTION_CHAIN_V3_API = f"{NSE_BASE}/api/option-chain-v3?type={{chain_type}}&symbol={{symbol}}&expiry={{expiry}}"
NSE_ALL_INDICES_API = f"{NSE_BASE}/api/allIndices"

# Symbols routed through type=Indices on option-chain-v3
INDEX_SYMBOLS = frozenset(
    {
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "NIFTYIT",
        "NIFTY MID SELECT",
    }
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": NSE_OPTION_CHAIN_PAGE,
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
}


class NSEFetchError(Exception):
    """NSE returned non-JSON or empty payload in this client context."""


def new_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def warm_session(session: requests.Session, timeout: float = 12.0) -> None:
    """Establish Akamai cookies via the option-chain page (homepage often 403)."""
    session.get(NSE_OPTION_CHAIN_PAGE, timeout=timeout)


def _parse_json_response(resp: requests.Response) -> Dict[str, Any]:
    ct = (resp.headers.get("content-type") or "").lower()
    body = resp.text or ""
    snippet = body[:200].lower()

    if resp.status_code == 404 and ("not found" in snippet or body.lstrip().startswith("<")):
        raise NSEFetchError(
            "NSE served HTML/not-found page (status=404) — likely legacy endpoint "
            "or anti-bot/session rejection, not necessarily a dead product"
        )
    if body.lstrip().startswith("<") or "text/html" in ct:
        raise NSEFetchError(f"NSE returned HTML (status={resp.status_code}, ct={ct})")
    if resp.status_code >= 400:
        raise NSEFetchError(f"NSE HTTP {resp.status_code}: {body[:120]}")

    try:
        return resp.json()
    except json.JSONDecodeError as exc:
        raise NSEFetchError(f"NSE body is not JSON (ct={ct}): {body[:120]}") from exc


def _is_index_symbol(symbol: str) -> bool:
    return symbol.upper() in INDEX_SYMBOLS


def _nse_symbol(symbol: str) -> str:
    """Map internal symbols to NSE contract-info / v3 symbol names."""
    mapping = {
        "MIDCPNIFTY": "MIDCPNIFTY",
        "NIFTY MID SELECT": "MIDCPNIFTY",
    }
    return mapping.get(symbol.upper(), symbol.upper())


def fetch_contract_info(
    symbol: str,
    session: requests.Session,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    sym = quote(_nse_symbol(symbol), safe="")
    url = NSE_CONTRACT_INFO_API.format(symbol=sym)
    resp = session.get(url, timeout=timeout)
    return _parse_json_response(resp)


def nearest_expiry(symbol: str, session: requests.Session, timeout: float = 15.0) -> str:
    info = fetch_contract_info(symbol, session, timeout=timeout)
    expiries: List[str] = info.get("expiryDates") or []
    if not expiries:
        raise NSEFetchError(f"No expiry dates returned for {symbol}")
    return expiries[0]


def fetch_option_chain_v3(
    symbol: str,
    session: requests.Session,
    expiry: Optional[str] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    sym = _nse_symbol(symbol)
    chain_type = "Indices" if _is_index_symbol(sym) else "Equity"
    exp = expiry or nearest_expiry(sym, session, timeout=timeout)
    url = NSE_OPTION_CHAIN_V3_API.format(
        chain_type=chain_type,
        symbol=quote(sym, safe=""),
        expiry=quote(exp, safe=""),
    )
    resp = session.get(url, timeout=timeout)
    data = _parse_json_response(resp)
    rows = data.get("records", {}).get("data") or []
    if not rows:
        raise NSEFetchError(
            f"option-chain-v3 returned empty chain for {sym} expiry={exp} " "(market closed or stale expiry)"
        )
    return data


def fetch_option_chain_legacy(
    symbol: str,
    session: requests.Session,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    sym = quote(_nse_symbol(symbol), safe="")
    url = NSE_OPTION_CHAIN_LEGACY.format(symbol=sym)
    resp = session.get(url, timeout=timeout)
    return _parse_json_response(resp)


def fetch_json(
    url: str,
    session: Optional[requests.Session] = None,
    timeout: float = 15.0,
    retry: bool = True,
    warm: bool = True,
) -> Dict[str, Any]:
    """
    GET url with warmed session and JSON validation.
    Retries once with a fresh session on NSEFetchError.
    """
    last_err: Optional[Exception] = None

    for attempt in range(2 if retry else 1):
        s = session if attempt == 0 and session is not None else new_session()
        try:
            if warm:
                warm_session(s, timeout=timeout)
            resp = s.get(url, timeout=timeout)
            return _parse_json_response(resp)
        except NSEFetchError as exc:
            last_err = exc
            session = None
            continue
        except requests.RequestException as exc:
            last_err = exc
            session = None
            continue

    raise NSEFetchError(str(last_err) if last_err else "NSE fetch failed")


def fetch_option_chain_json(
    symbol: str,
    session: Optional[requests.Session] = None,
    expiry: Optional[str] = None,
    retry: bool = True,
) -> Dict[str, Any]:
    """
    Fetch full NSE option-chain JSON for an index or equity symbol.

    Uses option-chain-v3 (current API). Legacy option-chain-indices is attempted
    only if v3 fails with a transport/session error.
    """
    last_err: Optional[Exception] = None

    attempts = 2 if retry else 1
    for attempt in range(attempts):
        s = session if attempt == 0 and session is not None else new_session()
        try:
            warm_session(s)
            return fetch_option_chain_v3(symbol, s, expiry=expiry)
        except NSEFetchError as exc:
            last_err = exc
            session = None
            if attempt + 1 < attempts:
                continue
        except requests.RequestException as exc:
            last_err = exc
            session = None
            if attempt + 1 < attempts:
                continue

    # Last resort: legacy endpoint (often 404 HTML on modern NSE)
    try:
        s = new_session()
        warm_session(s)
        data = fetch_option_chain_legacy(symbol, s)
        rows = data.get("records", {}).get("data") or []
        if rows:
            logger.debug("NSE legacy option-chain-indices succeeded for %s", symbol)
            return data
    except Exception as legacy_exc:
        last_err = legacy_exc

    raise NSEFetchError(str(last_err) if last_err else "NSE option chain fetch failed")


def fetch_all_indices_json(session: Optional[requests.Session] = None) -> Dict[str, Any]:
    return fetch_json(NSE_ALL_INDICES_API, session=session)
