"""Moneycontrol All-Options Top Gainers — reference scrape (NOT trading truth).

Labeled LIVE_SCRAPED for UI comparison only. Paper/live execution must use Dhan.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MC_URL = (
    "https://www.moneycontrol.com/stocks/fno/marketstats/options/gainers/homebody.php"
    "?optiontopic=gainers&optinst=allopt&sel_mth=all"
)

IST = timezone(timedelta(hours=5, minutes=30))


def _ist_now() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def _parse_num(text: str) -> Optional[float]:
    raw = (text or "").strip().replace(",", "").replace("%", "")
    if not raw or raw in {"-", "—", "NA", "N/A"}:
        return None
    # Moneycontrol Change column often "126.25  4,590.91%" — take first token for ₹ change
    if " " in raw and not raw.replace(".", "", 1).replace("-", "", 1).isdigit():
        parts = raw.split()
        raw = parts[0]
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_change_pair(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse '126.25  4,590.91%' -> (change_rs, gain_pct)."""
    cleaned = (text or "").replace(",", " ").strip()
    if not cleaned:
        return None, None
    nums = re.findall(r"-?\d+(?:\.\d+)?", cleaned.replace(",", ""))
    if not nums:
        return None, None
    change = float(nums[0]) if nums else None
    gain = float(nums[1]) if len(nums) > 1 else None
    # If only one number and original had %, treat as gain
    if gain is None and "%" in (text or "") and change is not None:
        gain = change
        change = None
    return change, gain


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.capture = False
        self.rows: List[List[str]] = []
        self._row: List[str] = []
        self._cell: List[str] = []
        self._tables: List[List[List[str]]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        t = tag.lower()
        if t == "table":
            self.in_table = True
            self.rows = []
        elif self.in_table and t == "tr":
            self.in_row = True
            self._row = []
        elif self.in_row and t in {"td", "th"}:
            self.in_cell = True
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in {"td", "th"} and self.in_cell:
            self.in_cell = False
            self._row.append(" ".join("".join(self._cell).split()))
        elif t == "tr" and self.in_row:
            self.in_row = False
            if self._row:
                self.rows.append(self._row)
        elif t == "table" and self.in_table:
            self.in_table = False
            if self.rows:
                self._tables.append(self.rows)

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self._cell.append(data)


def _pick_gainers_table(tables: List[List[List[str]]]) -> List[List[str]]:
    for table in tables:
        if not table:
            continue
        header = " ".join(table[0]).lower()
        if "symbol" in header and ("option" in header or "strike" in header) and (
            "chg" in header or "change" in header or "last" in header
        ):
            return table
    # Fallback: widest table with CE/PE cells
    best: List[List[str]] = []
    for table in tables:
        flat = " ".join(" ".join(r) for r in table[:5]).upper()
        if " CE " in f" {flat} " or flat.count("CE") > 2:
            if len(table) > len(best):
                best = table
    return best


def _row_to_record(cells: List[str], rank: int, refreshed_at: str) -> Optional[Dict[str, Any]]:
    if len(cells) < 6:
        return None
    symbol = re.sub(r"[^A-Z0-9\-&]", "", (cells[0] or "").upper())
    if not symbol or symbol in {"SYMBOL", "COMPANY"}:
        return None
    expiry = cells[1] if len(cells) > 1 else ""
    opt = (cells[2] if len(cells) > 2 else "").strip().upper()
    if opt not in {"CE", "PE"}:
        # sometimes type is elsewhere
        for c in cells[1:5]:
            if str(c).strip().upper() in {"CE", "PE"}:
                opt = str(c).strip().upper()
                break
    strike = _parse_num(cells[3] if len(cells) > 3 else "")
    ltp = _parse_num(cells[4] if len(cells) > 4 else "")
    change_rs, gain_pct = _parse_change_pair(cells[5] if len(cells) > 5 else "")
    # Volume / OI positions vary; Moneycontrol: High Low, Avg, Vol, Value, OI, OI Chg
    volume = None
    oi = None
    if len(cells) >= 11:
        volume = _parse_num(cells[8])
        oi = _parse_num(cells[10])
    elif len(cells) >= 9:
        volume = _parse_num(cells[7])
        oi = _parse_num(cells[8])
    if gain_pct is None and ltp is None:
        return None
    return {
        "rank": rank,
        "underlying": symbol,
        "symbol": symbol,
        "expiry_date": expiry,
        "option_type": opt or "CE",
        "strike": strike,
        "ltp": ltp,
        "change": change_rs,
        "change_rs": change_rs,
        "gain_pct": round(gain_pct, 4) if gain_pct is not None else None,
        "volume": int(volume) if volume is not None else None,
        "oi": int(oi) if oi is not None else None,
        "market_match_note": (
            f"LIVE SCRAPED GAINER [+{gain_pct:.1f}%]" if gain_pct is not None else "LIVE SCRAPED GAINER"
        ),
        "refreshed_at": refreshed_at,
        "data_provenance": "LIVE_SCRAPED",
        "source": "moneycontrol",
    }


def fetch_moneycontrol_option_gainers(top_n: int = 25, timeout_s: float = 25.0) -> Dict[str, Any]:
    """Fetch Moneycontrol All Options Top Gainers. Fail-closed on scrape errors."""
    refreshed_at = _ist_now()
    started = time.monotonic()
    try:
        req = Request(
            MC_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-IN,en;q=0.9",
                "Referer": "https://www.moneycontrol.com/stocks/fno/marketstats/options/gainers/",
                "Cache-Control": "no-cache",
            },
            method="GET",
        )
        with urlopen(req, timeout=timeout_s) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "status": "SCRAPE_FAILED",
            "model_proof_ready": False,
            "market_top_table": [],
            "error": str(exc)[:240],
            "source": "moneycontrol",
            "data_provenance": "LIVE_SCRAPED",
            "refreshed_at": refreshed_at,
            "url": MC_URL,
            "note": "Moneycontrol scrape failed — Dhan Market Top remains trading truth.",
        }

    parser = _TableParser()
    try:
        parser.feed(html)
    except Exception as exc:
        return {
            "status": "PARSE_FAILED",
            "market_top_table": [],
            "error": str(exc)[:240],
            "source": "moneycontrol",
            "data_provenance": "LIVE_SCRAPED",
            "refreshed_at": refreshed_at,
            "url": MC_URL,
        }

    table = _pick_gainers_table(parser._tables)
    rows: List[Dict[str, Any]] = []
    if table:
        body = table[1:] if table and "symbol" in " ".join(table[0]).lower() else table
        for i, cells in enumerate(body, start=1):
            rec = _row_to_record(cells, i, refreshed_at)
            if rec and rec.get("gain_pct") is not None:
                rows.append(rec)
            if len(rows) >= top_n:
                break

    rows.sort(key=lambda r: float(r.get("gain_pct") or 0), reverse=True)
    for i, rec in enumerate(rows, start=1):
        rec["rank"] = i

    return {
        "status": "ok" if rows else "EMPTY",
        "title": "Moneycontrol All-India Top Option Gainers [% Gain]",
        "market_top_table": rows[:top_n],
        "contracts_scored_total": len(rows),
        "source": "moneycontrol",
        "data_provenance": "LIVE_SCRAPED",
        "stream_mode": "http_scrape",
        "refreshed_at": refreshed_at,
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "url": MC_URL,
        "elapsed_ms": int((time.monotonic() - started) * 1000),
        "note": (
            "REFERENCE ONLY — scraped Moneycontrol All Options Top Gainers. "
            "Not used for live order placement. Paper may watch symbols; Dhan MTM required."
        ),
        "ready_for_live": False,
        "live_trading_enabled": False,
    }
