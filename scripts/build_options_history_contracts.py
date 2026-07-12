"""
Build CE/PE historical contract list from Dhan instrument master.

Output:
  state/options_history/contracts.csv

This is the missing bridge between Dhan instrument master and the CE/PE
historical training pipeline. It writes only real Dhan security_id rows from the
local synced instrument master; it never invents contracts.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.data.instruments_master import dataframe_from_dhan_csv, resolve_master_csv

OUT_DIR = ROOT / "state" / "options_history"
OUT_CSV = OUT_DIR / "contracts.csv"
REPORT_DIR = ROOT / "reports" / "latest" / "options_contract_builder"

DEFAULT_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]


def _write_report(status: str, reason: str, extra: dict | None = None) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "reason": reason,
        "output_csv": str(OUT_CSV),
        "live_trading_enabled": False,
        "broker_order_endpoints_called": False,
        "synthetic_contracts_allowed": False,
    }
    if extra:
        payload.update(extra)
    (REPORT_DIR / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# CE/PE Contract Builder Proof",
        "",
        f"- Generated UTC: `{payload['generated_at']}`",
        f"- Status: **{status}**",
        f"- Reason: {reason}",
        f"- Output CSV: `{OUT_CSV}`",
        "- Live trading: `OFF`",
        "- Broker order endpoints called: `false`",
        "- Synthetic contracts allowed: `false`",
    ]
    if extra:
        lines.append("")
        lines.append("## Details")
        for k, v in extra.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                lines.append(f"- {k}: `{v}`")
    (REPORT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_seg(exch_seg: str) -> str:
    s = str(exch_seg).upper()
    if s in ("NFO", "NSE_FNO"):
        return "NSE_FNO"
    if s in ("BFO", "BSE_FNO"):
        return "BSE_FNO"
    return s


def _is_option(symbol: str, instrument_type: str) -> bool:
    combo = f"{symbol} {instrument_type}".upper()
    return "CE" in combo or "PE" in combo or "OPT" in combo


def _option_type(symbol: str, instrument_type: str) -> str:
    combo = f"{symbol} {instrument_type}".upper()
    if "PE" in combo:
        return "PE"
    if "CE" in combo:
        return "CE"
    return ""


def _clean_underlying(name: str, symbol: str) -> str:
    n = str(name or "").upper().replace(" ", "")
    s = str(symbol or "").upper().replace(" ", "")
    for u in ["BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTY"]:
        if n == u or s.startswith(u):
            return u
    return n


def build_contracts(underlyings: List[str], max_expiries: int, strikes_each_side: int, max_rows: int) -> int:
    master = resolve_master_csv()
    if not master:
        _write_report("BLOCKED", "Dhan instrument master CSV not found. Run sync_dhan_instruments_master.py first.")
        return 0
    raw = pd.read_csv(master, low_memory=False)
    df = dataframe_from_dhan_csv(raw, derivatives_only=True)
    if df.empty:
        _write_report("BLOCKED", "Dhan instrument master parsed zero derivative rows", {"master_csv": str(master)})
        return 0

    wanted = {u.upper() for u in underlyings}
    df["underlying_clean"] = [_clean_underlying(n, s) for n, s in zip(df.get("name", ""), df.get("symbol", ""))]
    df = df[df["underlying_clean"].isin(wanted)].copy()
    df = df[df.apply(lambda r: _is_option(r.get("symbol", ""), r.get("instrumenttype", "")), axis=1)].copy()
    df["option_type"] = df.apply(lambda r: _option_type(r.get("symbol", ""), r.get("instrumenttype", "")), axis=1)
    df = df[df["option_type"].isin(["CE", "PE"])].copy()
    df["expiry"] = df["expiry"].astype(str).str[:10]
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df = df.dropna(subset=["strike"])
    if df.empty:
        _write_report("BLOCKED", "No CE/PE rows found after filtering Dhan master", {"master_csv": str(master)})
        return 0

    rows = []
    today = date.today().isoformat()
    for u in sorted(wanted):
        part = df[df["underlying_clean"] == u].copy()
        future_expiries = sorted([x for x in part["expiry"].dropna().astype(str).unique() if x >= today])
        selected_expiries = future_expiries[:max_expiries] if future_expiries else sorted(part["expiry"].dropna().astype(str).unique())[:max_expiries]
        for exp in selected_expiries:
            exp_df = part[part["expiry"] == exp].copy()
            strikes = sorted(exp_df["strike"].dropna().unique())
            if not strikes:
                continue
            mid_idx = len(strikes) // 2
            lo = max(0, mid_idx - strikes_each_side)
            hi = min(len(strikes), mid_idx + strikes_each_side + 1)
            selected_strikes = set(strikes[lo:hi])
            final = exp_df[exp_df["strike"].isin(selected_strikes)].copy()
            for _, r in final.iterrows():
                rows.append({
                    "underlying": u,
                    "expiry": str(r["expiry"]),
                    "strike": float(r["strike"]),
                    "option_type": r["option_type"],
                    "security_id": str(r["token"]),
                    "exchange_segment": _normalize_seg(r.get("exch_seg", "NSE_FNO")),
                    "instrument": "OPTIDX",
                })
                if len(rows) >= max_rows:
                    break
            if len(rows) >= max_rows:
                break
        if len(rows) >= max_rows:
            break

    if not rows:
        _write_report("BLOCKED", "No CE/PE contract rows selected", {"master_csv": str(master)})
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        cols = ["underlying", "expiry", "strike", "option_type", "security_id", "exchange_segment", "instrument"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    _write_report("PASS", "CE/PE historical contract list built from real Dhan instrument master", {
        "master_csv": str(master),
        "contracts": len(rows),
        "underlyings": ",".join(sorted(wanted)),
        "max_expiries": max_expiries,
        "strikes_each_side": strikes_each_side,
    })
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--underlyings", default=",".join(DEFAULT_UNDERLYINGS))
    ap.add_argument("--max-expiries", type=int, default=2)
    ap.add_argument("--strikes-each-side", type=int, default=8)
    ap.add_argument("--max-rows", type=int, default=160)
    args = ap.parse_args()
    underlyings = [x.strip().upper() for x in args.underlyings.split(",") if x.strip()]
    build_contracts(underlyings, args.max_expiries, args.strikes_each_side, args.max_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
