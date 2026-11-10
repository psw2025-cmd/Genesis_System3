"""
NSE equity (stock) F&O universe — OPTSTK underlyings from Dhan security master.

NSE lists ~140 securities with stock options (OPTSTK) vs index options (OPTIDX).
References:
  - https://www.nseindia.com/products/content/derivatives/equities/contract_specifitns.htm
  - Dhan instrument master: SEM_INSTRUMENT_NAME = OPTSTK
"""

from __future__ import annotations

import csv
import hashlib
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set

from core.data.instruments_master import resolve_master_csv

ROOT = Path(__file__).resolve().parents[3]
SECURITY_MASTER = ROOT / "security_id_list.csv"


def resolve_equity_security_master() -> Path:
    """Prefer the official build/startup sync; bundled CSV is emergency-only."""
    return resolve_master_csv() or SECURITY_MASTER

# Liquid F&O names used for live scanner priority (subset of full universe)
PRIORITY_EQUITY_FO = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "ITC",
    "KOTAKBANK",
    "LT",
    "AXISBANK",
    "MARUTI",
    "TATAMOTORS",
    "SUNPHARMA",
    "BAJFINANCE",
    "HINDUNILVR",
    "WIPRO",
    "ADANIENT",
    "TATASTEEL",
    "NTPC",
]

# High-beta / frequent Moneycontrol option-gainer names (rotated into Market Top scan).
# These are present in OPTSTK master but were never scanned when equity_limit=4 of PRIORITY only.
HIGH_MOMENTUM_EQUITY_FO = [
    "DIVISLAB",
    "LTM",
    "PAYTM",
    "JUBLFOOD",
    "TVSMOTOR",
    "SIEMENS",
    "APLAPOLLO",
    "BAJAJFINSV",
    "HYUNDAI",
    "ASHOKLEY",
    "GAIL",
    "ABCAPITAL",
    "GODFRYPHLP",
    "INDIGO",
    "MUTHOOTFIN",
    "SHRIRAMFIN",
    "SHREECEM",
    "BAJFINANCE",
    "TATACONSUM",
    "IRFC",
    "JIOFIN",
    "YESBANK",
    "AMBUJACEM",
    "TECHM",
    "MPHASIS",
]

PAPER_PREDICTION_HORIZONS = (
    ("1_week", 5),
    ("3_weeks", 15),
    ("1_month", 21),
    ("3_months", 63),
    ("6_months", 126),
    ("1_year", 252),
    ("2_years", 504),
)


def _option_underlying(row: Dict[str, str]) -> str:
    """Use the exchange trading prefix; BSE's symbol-name field is an alias."""
    trading = (row.get("SEM_TRADING_SYMBOL") or row.get("TRADING_SYMBOL") or "").strip().upper()
    if "-" in trading:
        return trading.split("-", 1)[0].strip()
    return (row.get("UNDERLYING_SYMBOL") or "").strip().upper()


@lru_cache(maxsize=1)
def load_equity_market_coverage() -> Dict[str, Any]:
    """Account for every NSE/BSE cash and stock-option master row.

    This is a read-only ingestion/scan plan, not a claim that every instrument
    has a fresh quote. Quote snapshots may be batched at 1,000 instruments;
    full option-chain detail remains paced/on-demand at Dhan's 3-second gate.
    """
    master_path = resolve_equity_security_master()
    if not master_path.exists():
        return {
            "source": "missing_security_master",
            "implemented": False,
            "reliance_only": False,
            "cash": {},
            "stock_options": {},
        }

    cash_ids: Dict[str, Set[str]] = {"NSE": set(), "BSE": set()}
    cash_symbols: Dict[str, Set[str]] = {"NSE": set(), "BSE": set()}
    option_names: Dict[str, Set[str]] = {"NSE": set(), "BSE": set()}
    option_sides: Dict[str, Dict[str, int]] = {
        "NSE": {"CE": 0, "PE": 0},
        "BSE": {"CE": 0, "PE": 0},
    }
    sides_by_underlying: Dict[str, Set[str]] = {}

    with master_path.open(encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            exchange = (row.get("SEM_EXM_EXCH_ID") or row.get("EXCH_ID") or "").strip().upper()
            if exchange not in cash_ids:
                continue
            instrument = (row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").strip().upper()
            if instrument == "EQUITY":
                security_id = (row.get("SEM_SMST_SECURITY_ID") or row.get("SECURITY_ID") or "").strip()
                symbol = (
                    row.get("SEM_TRADING_SYMBOL")
                    or row.get("TRADING_SYMBOL")
                    or row.get("SYMBOL_NAME")
                    or ""
                ).strip().upper()
                if security_id:
                    cash_ids[exchange].add(security_id)
                if symbol:
                    cash_symbols[exchange].add(symbol)
            elif instrument == "OPTSTK":
                underlying = _option_underlying(row)
                side = (row.get("SEM_OPTION_TYPE") or row.get("OPTION_TYPE") or "").strip().upper()
                if underlying:
                    option_names[exchange].add(underlying)
                    if side in {"CE", "PE"}:
                        sides_by_underlying.setdefault(underlying, set()).add(side)
                if side in option_sides[exchange]:
                    option_sides[exchange][side] += 1

    union_names = option_names["NSE"] | option_names["BSE"]
    missing_sides = sorted(name for name in union_names if sides_by_underlying.get(name) != {"CE", "PE"})
    cash = {
        exchange: {
            "instrument_count": len(cash_ids[exchange]),
            "symbol_count": len(cash_symbols[exchange]),
            "quote_batches": math.ceil(len(cash_ids[exchange]) / 1000),
            "segment": f"{exchange}_EQ",
        }
        for exchange in ("NSE", "BSE")
    }
    stock_options: Dict[str, Any] = {
        exchange: {
            "underlying_count": len(option_names[exchange]),
            "contract_count": option_sides[exchange]["CE"] + option_sides[exchange]["PE"],
            "ce_contracts": option_sides[exchange]["CE"],
            "pe_contracts": option_sides[exchange]["PE"],
            "segment": f"{exchange}_FNO",
        }
        for exchange in ("NSE", "BSE")
    }
    stock_options.update(
        {
            "union_underlying_count": len(union_names),
            "overlap_underlying_count": len(option_names["NSE"] & option_names["BSE"]),
            "underlyings_missing_ce_or_pe": missing_sides,
        }
    )
    digest = hashlib.sha256(master_path.read_bytes()).hexdigest()
    return {
        "schema_version": "system3.dhan-equity-coverage.v1",
        "source": master_path.name,
        "source_path": str(master_path),
        "source_mode": "OFFICIAL_SYNC" if master_path != SECURITY_MASTER else "BUNDLED_FALLBACK",
        "source_sha256": digest,
        "implemented": bool(union_names and cash_ids["NSE"] and cash_ids["BSE"]),
        "reliance_only": union_names == {"RELIANCE"},
        "cash": cash,
        "stock_options": stock_options,
        "scan_plan": {
            "quote_batch_size": 1000,
            "quote_rate_limit_per_second": 1,
            "option_chain_min_gap_seconds": 3.0,
            "unbounded_simultaneous_chain_fetch": False,
            "cash_mode": "BOUNDED_MARKET_QUOTE_BATCHES",
            "option_ranking_mode": "BOUNDED_MARKET_QUOTE_BATCHES_THEN_PACED_CHAIN_DETAIL",
        },
        "prediction_horizons": [
            {
                "id": horizon_id,
                "trading_days": days,
                "mode": "PAPER_RESEARCH_ONLY",
                "outcome_required": True,
            }
            for horizon_id, days in PAPER_PREDICTION_HORIZONS
        ],
        "learning_contract": {
            "mode": "BOUNDED_CHALLENGER_RETRAINING_RECALIBRATION",
            "in_place_champion_mutation": False,
            "automatic_live_promotion": False,
            "paper_outcome_reconciliation_required": True,
        },
        "read_only": True,
        "live_trading_enabled": False,
    }


@lru_cache(maxsize=1)
def load_equity_fo_universe() -> Dict[str, Any]:
    """Load the union of NSE/BSE stock-option underlyings from Dhan master."""
    underlyings: Set[str] = set()
    contract_count = 0
    sample_contracts: List[Dict[str, Any]] = []

    master_path = resolve_equity_security_master()
    if not master_path.exists():
        return {
            "source": "missing_security_master",
            "underlying_count": 0,
            "contract_count": 0,
            "underlyings": [],
            "priority_underlyings": PRIORITY_EQUITY_FO,
            "implemented": False,
        }

    with master_path.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exch = (row.get("SEM_EXM_EXCH_ID") or row.get("EXCH_ID") or "").strip().upper()
            inst = (row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").strip().upper()
            seg = (row.get("SEM_SEGMENT") or row.get("SEGMENT") or "").strip().upper()
            if exch not in {"NSE", "BSE"} or inst != "OPTSTK":
                continue
            if seg and seg not in ("D", "DERIVATIVES"):
                continue
            name = _option_underlying(row)
            if not name:
                continue
            underlyings.add(name)
            contract_count += 1
            if len(sample_contracts) < 5:
                sample_contracts.append(
                    {
                        "underlying": name,
                        "trading_symbol": row.get("SEM_TRADING_SYMBOL") or row.get("SEM_CUSTOM_SYMBOL"),
                        "strike": row.get("SEM_STRIKE_PRICE"),
                        "option_type": row.get("SEM_OPTION_TYPE"),
                        "expiry_date": (row.get("SEM_EXPIRY_DATE") or "")[:10],
                        "lot_size": row.get("SEM_LOT_UNITS"),
                        "security_id": row.get("SEM_SMST_SECURITY_ID"),
                    }
                )

    sorted_names = sorted(underlyings)
    priority = [s for s in PRIORITY_EQUITY_FO if s in underlyings]
    momentum = [s for s in HIGH_MOMENTUM_EQUITY_FO if s in underlyings]
    # Momentum first for Moneycontrol-parity scanning, then classic liquid names.
    scan_priority: List[str] = []
    for name in momentum + priority:
        if name not in scan_priority:
            scan_priority.append(name)
    return {
        "source": master_path.name,
        "source_mode": "OFFICIAL_SYNC" if master_path != SECURITY_MASTER else "BUNDLED_FALLBACK",
        "underlying_count": len(sorted_names),
        "contract_count": contract_count,
        "underlyings": sorted_names,
        "priority_underlyings": scan_priority or priority,
        "momentum_underlyings": momentum,
        "sample_contracts": sample_contracts,
        "implemented": len(sorted_names) > 0,
        "instrument_type": "OPTSTK",
        "exchange": "NSE_FNO+BSE_FNO",
        "exchange_coverage": ["BSE_FNO", "NSE_FNO"],
        "market_coverage": load_equity_market_coverage(),
    }


def is_equity_fo_symbol(symbol: str) -> bool:
    sym = (symbol or "").strip().upper()
    if not sym:
        return False
    universe = load_equity_fo_universe()
    return sym in set(universe.get("underlyings") or [])


INDEX_FO_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}


def is_tradeable_fo_symbol(symbol: str) -> bool:
    """True for index F&O or NSE equity F&O underlyings; blocks cash-only movers."""
    sym = (symbol or "").strip().upper()
    if not sym:
        return False
    if sym in INDEX_FO_SYMBOLS:
        return True
    return is_equity_fo_symbol(sym)
