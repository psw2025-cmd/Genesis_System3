"""
Genesis System3 — Costed Walk-Forward Backtest Proof
=====================================================
Runs a walk-forward simulation on available bhavcopy data with realistic
brokerage + slippage + spread costs. Proves the backtest pipeline works.

Uses NSE FO bhavcopy files in storage/bhavcopy/ (NIFTY options only).
Does NOT require broker connection or pandas/numpy (pure stdlib).

Writes proof to:
  reports/latest/recent_backtest_walkforward_proof/costed_walkforward_proof.json

Safety: LIVE_TRADING_ENABLED must be 0 (always checked).
"""

import csv
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "reports" / "latest" / "recent_backtest_walkforward_proof"
OUT.mkdir(parents=True, exist_ok=True)

BHAVCOPY_DIR = ROOT / "storage" / "bhavcopy"

# Safety gate
if os.environ.get("LIVE_TRADING_ENABLED", "0") not in ("0", "false", "False", ""):
    print("LIVE_TRADING_ENABLED is truthy — aborting.")
    sys.exit(1)

# Realistic NSE Options cost model (Dhan flat fee plan)
BROKERAGE_PER_SIDE = 20.0  # ₹20 flat per order (Dhan)
STT_RATE = 0.000625  # 0.0625% on sell-side premium
EXCHANGE_TXN_CHARGE = 0.0005  # 0.05% of premium
GST_ON_BROKERAGE = 0.18  # 18% GST on brokerage+charges
SEBI_RATE = 0.000001  # ₹10 per crore traded
SLIPPAGE_PCT = 0.001  # 0.1% slippage on entry + exit
MIN_FORWARD_SESSIONS = 30

INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}
LOT_SIZES = {"NIFTY": 75, "BANKNIFTY": 30, "FINNIFTY": 40, "MIDCPNIFTY": 75}


def assess_costed_walkforward(trading_sessions: int, trades: list[dict]) -> dict:
    """Fail closed unless both the minimum chronology and execution evidence exist.

    Daily bhavcopy OHLC/OI rows do not contain spread or execution latency and
    cannot prove fills. A cost estimate alone is diagnostic, never a PASS.
    """
    blockers = []
    if trading_sessions < MIN_FORWARD_SESSIONS:
        blockers.append(f"NEED_AT_LEAST_{MIN_FORWARD_SESSIONS}_TRADING_SESSIONS")
    if not trades:
        blockers.append("NO_WALK_FORWARD_TRADES")
    required = ("spread_bps", "latency_ms", "fill_timestamp", "fill_source",
                "fee_schedule_version")
    required_costs = ("brokerage", "exchange_charge", "stt", "gst", "sebi",
                      "slippage", "spread_cost", "latency_cost")
    for index, trade in enumerate(trades):
        evidence = trade.get("execution_evidence") if isinstance(trade, dict) else None
        costs = trade.get("cost_model") if isinstance(trade, dict) else None
        if (not isinstance(evidence, dict) or any(evidence.get(field) is None for field in required)
                or not isinstance(costs, dict) or costs.get("evidence_status") != "VERIFIED"
                or any(costs.get(field) is None for field in required_costs)):
            blockers.append(f"TRADE_{index + 1}_MISSING_EXECUTION_EVIDENCE")
            break
        try:
            numeric = [evidence["spread_bps"], evidence["latency_ms"]]
            numeric.extend(costs[field] for field in required_costs)
            if any(isinstance(value, bool) or not math.isfinite(float(value)) or float(value) < 0
                   for value in numeric):
                raise ValueError
        except (TypeError, ValueError):
            blockers.append(f"TRADE_{index + 1}_INVALID_EXECUTION_EVIDENCE")
            break
    return {"pass": not blockers, "status": "PASS" if not blockers else "BLOCKED",
            "blockers": blockers, "minimum_trading_sessions": MIN_FORWARD_SESSIONS,
            "trading_sessions": trading_sessions}


def compute_cost(entry_price: float, exit_price: float, symbol: str, qty: int) -> dict:
    lot_size = LOT_SIZES.get(symbol, 50)
    lots = max(1, qty // lot_size)
    contracts = lots * lot_size

    entry_value = entry_price * contracts
    exit_value = exit_price * contracts

    # Slippage
    entry_slip = entry_value * SLIPPAGE_PCT
    exit_slip = exit_value * SLIPPAGE_PCT

    # Gross P&L before costs
    gross_pnl = (exit_price - entry_price) * contracts

    # Brokerage (both sides)
    brokerage = BROKERAGE_PER_SIDE * 2

    # STT on sell side (exit)
    stt = exit_value * STT_RATE

    # Exchange transaction charge (both sides)
    exc = (entry_value + exit_value) * EXCHANGE_TXN_CHARGE

    # GST on (brokerage + exc)
    gst = (brokerage + exc) * GST_ON_BROKERAGE

    # SEBI fee
    sebi = (entry_value + exit_value) * SEBI_RATE

    total_costs = brokerage + stt + exc + gst + sebi + entry_slip + exit_slip
    net_pnl = gross_pnl - total_costs

    return {
        "lots": lots,
        "contracts": contracts,
        "entry_value": round(entry_value, 2),
        "exit_value": round(exit_value, 2),
        "gross_pnl": round(gross_pnl, 2),
        "brokerage": round(brokerage, 2),
        "stt": round(stt, 4),
        "exchange_charge": round(exc, 4),
        "gst": round(gst, 4),
        "sebi": round(sebi, 6),
        "slippage": round(entry_slip + exit_slip, 2),
        "total_costs": round(total_costs, 2),
        "net_pnl": round(net_pnl, 2),
        "cost_pct_of_entry": round(total_costs / max(entry_value, 1) * 100, 3),
    }


def load_bhavcopy(csv_path: Path) -> list[dict]:
    rows = []
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            # Detect format: UDiFF (has TckrSymb) vs old (has Symbol)
            sym_col = "TckrSymb" if "TckrSymb" in headers else "Symbol" if "Symbol" in headers else None
            close_col = "ClsPric" if "ClsPric" in headers else "Close" if "Close" in headers else None
            oi_col = "OpnIntrst" if "OpnIntrst" in headers else "OI" if "OI" in headers else None
            oi_chg_col = "ChngInOpnIntrst" if "ChngInOpnIntrst" in headers else None

            if not sym_col or not close_col:
                return rows

            for row in reader:
                sym = (row.get(sym_col) or "").strip()
                if sym not in INDEX_SYMBOLS:
                    continue
                try:
                    close = float(row.get(close_col) or 0)
                    oi = float(row.get(oi_col) or 0)
                    oi_chg = float(row.get(oi_chg_col) or 0) if oi_chg_col else 0.0
                    rows.append(
                        {
                            "symbol": sym,
                            "close": close,
                            "oi": oi,
                            "oi_chg": oi_chg,
                            "option_type": (row.get("OptTp") or row.get("OptionType") or "CE").strip(),
                            "strike": float(row.get("StrkPric") or row.get("Strike") or 0),
                            "expiry": (row.get("XpryDt") or row.get("Expiry") or "").strip(),
                        }
                    )
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"  [load_bhavcopy] Error reading {csv_path.name}: {e}")
    return rows


def select_atm_option(rows: list[dict], symbol: str, spot_proxy: float) -> dict | None:
    candidates = [r for r in rows if r["symbol"] == symbol and r["option_type"] == "CE" and r["close"] > 5]
    if not candidates:
        return None
    # Pick nearest strike to spot
    candidates.sort(key=lambda r: abs(r["strike"] - spot_proxy))
    return candidates[0]


def run_proof() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    proof_id = f"WALKFORWARD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"[WalkForwardProof] Starting {proof_id}")

    # Load all available bhavcopy files (sorted by date)
    bhavcopy_files = sorted(BHAVCOPY_DIR.glob("*_fo_bhavcopy.csv"))
    if not bhavcopy_files:
        result = {
            "proof_id": proof_id,
            "started": started,
            "status": "FAIL",
            "pass": False,
            "reason": "No bhavcopy files found in storage/bhavcopy/",
            "hint": "Run scripts/bhavcopy_downloader.py first",
        }
        (OUT / "costed_walkforward_proof.json").write_text(json.dumps(result, indent=2))
        return result

    print(f"  Found {len(bhavcopy_files)} bhavcopy files: {[f.name for f in bhavcopy_files]}")

    # Walk-forward: use day N signal → day N+1 exit
    daily_data = []
    seen_sessions = set()
    input_warnings = []
    for f in bhavcopy_files:
        rows = load_bhavcopy(f)
        date_str = f.stem[:8]  # e.g. "20260612"
        try:
            datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            input_warnings.append(f"INVALID_SESSION_DATE:{f.name}")
            continue
        if date_str in seen_sessions:
            input_warnings.append(f"DUPLICATE_SESSION_DATE:{date_str}")
            continue
        seen_sessions.add(date_str)
        if not rows:
            input_warnings.append(f"EMPTY_SESSION_DATA:{date_str}")
            continue
        daily_data.append({"date": date_str, "rows": rows, "file": f.name})
        print(f"  {date_str}: {len(rows)} NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY rows")

    if len(daily_data) < 2:
        result = {
            "proof_id": proof_id,
            "started": started,
            "status": "FAIL",
            "pass": False,
            "reason": "Need at least 2 bhavcopy days for walk-forward proof",
            "days_available": len(daily_data),
        }
        (OUT / "costed_walkforward_proof.json").write_text(json.dumps(result, indent=2))
        return result

    # Walk-forward simulation: use day N's closing price as entry, day N+1 closing as exit
    trades = []
    total_gross_pnl = 0.0
    total_net_pnl = 0.0
    total_costs = 0.0
    walk_pairs = 0

    for i in range(len(daily_data) - 1):
        day0 = daily_data[i]
        day1 = daily_data[i + 1]

        for symbol in ["NIFTY", "BANKNIFTY"]:
            # Best ATM CE signal from day 0
            # Find highest OI+OI-change CE row as "signal"
            ce_rows_d0 = [
                r for r in day0["rows"] if r["symbol"] == symbol and r["option_type"] == "CE" and r["close"] > 10
            ]
            pe_rows_d0 = [
                r for r in day0["rows"] if r["symbol"] == symbol and r["option_type"] == "PE" and r["close"] > 10
            ]

            if not ce_rows_d0:
                continue

            # Sort by OI_chg descending to get most-active build-up option
            ce_rows_d0.sort(key=lambda r: r["oi_chg"], reverse=True)
            signal = ce_rows_d0[0]

            # Find same option (same strike, expiry) on day 1
            matching_d1 = [
                r
                for r in day1["rows"]
                if r["symbol"] == symbol
                and r["option_type"] == "CE"
                and abs(r["strike"] - signal["strike"]) < 0.01
                and r["expiry"] == signal["expiry"]
            ]

            if not matching_d1:
                continue

            exit_row = matching_d1[0]
            entry_price = signal["close"]
            exit_price = exit_row["close"]

            if entry_price <= 0:
                continue

            cost_detail = compute_cost(entry_price, exit_price, symbol, lot_size := LOT_SIZES.get(symbol, 50))
            trade = {
                "symbol": symbol,
                "strike": signal["strike"],
                "expiry": signal["expiry"],
                "option_type": "CE",
                "entry_date": day0["date"],
                "exit_date": day1["date"],
                "entry_price": round(entry_price, 2),
                "exit_price": round(exit_price, 2),
                "oi_at_entry": signal["oi"],
                "oi_chg_at_entry": signal["oi_chg"],
                "cost_model": cost_detail,
            }
            trades.append(trade)
            total_gross_pnl += cost_detail["gross_pnl"]
            total_net_pnl += cost_detail["net_pnl"]
            total_costs += cost_detail["total_costs"]
            walk_pairs += 1

    if not trades:
        result = {
            "proof_id": proof_id,
            "started": started,
            "status": "FAIL",
            "pass": False,
            "reason": "Walk-forward produced 0 matched option trades across bhavcopy days",
            "days_loaded": len(daily_data),
        }
        (OUT / "costed_walkforward_proof.json").write_text(json.dumps(result, indent=2))
        return result

    win_trades = [t for t in trades if t["cost_model"]["net_pnl"] > 0]
    loss_trades = [t for t in trades if t["cost_model"]["net_pnl"] <= 0]
    win_rate = len(win_trades) / len(trades) * 100

    acceptance = assess_costed_walkforward(len(daily_data), trades)
    net_wins = sum(t["cost_model"]["net_pnl"] for t in win_trades)
    net_losses = abs(sum(t["cost_model"]["net_pnl"] for t in loss_trades))
    net_by_session = {str(day["date"]): 0.0 for day in daily_data}
    exposure_by_session = {str(day["date"]): 0.0 for day in daily_data}
    for trade in trades:
        session = str(trade["exit_date"])
        net_by_session[session] = net_by_session.get(session, 0.0) + trade["cost_model"]["net_pnl"]
        exposure_by_session[session] = exposure_by_session.get(session, 0.0) + trade["cost_model"]["entry_value"]
    returns = [net_by_session[session] / max(exposure_by_session[session], 1.0)
               for session in sorted(net_by_session)]
    equity = 50_000.0
    peak = equity
    max_drawdown = 0.0
    for trade in trades:
        equity += trade["cost_model"]["net_pnl"]
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak * 100.0)
    mean_return = sum(returns) / len(returns)
    variance = sum((value - mean_return) ** 2 for value in returns) / len(returns)
    sharpe = (mean_return / variance ** 0.5 * 252 ** 0.5) if variance > 0 else None
    proof = {
        "proof_id": proof_id,
        "started": started,
        "completed": datetime.now(timezone.utc).isoformat(),
        "pass": acceptance["pass"],
        "status": acceptance["status"],
        "reason": ";".join(acceptance["blockers"]) if acceptance["blockers"] else None,
        "recent_costed_walkforward_proven": acceptance["pass"],
        "costs_slippage_included_proven": acceptance["pass"],
        "acceptance": acceptance,
        "walk_pairs": walk_pairs,
        "trade_count": len(trades),
        "win_trades": len(win_trades),
        "loss_trades": len(loss_trades),
        "win_rate_pct": round(win_rate, 1),
        "total_gross_pnl": round(total_gross_pnl, 2),
        "total_costs": round(total_costs, 2),
        "total_net_pnl": round(total_net_pnl, 2),
        "avg_net_pnl_per_trade": round(total_net_pnl / len(trades), 2),
        "diagnostic_metrics_only": {
            "sharpe_ratio": round(sharpe, 4) if sharpe is not None else None,
            "profit_factor": round(net_wins / net_losses, 4) if net_losses > 0 else None,
            "win_rate_pct": round(win_rate, 2),
            "max_drawdown_pct": round(max_drawdown, 4),
            "expectancy_per_trade": round(total_net_pnl / len(trades), 2),
            "net_return_pct_on_entry_notional": round(total_net_pnl / max(sum(t["cost_model"]["entry_value"] for t in trades), 1.0) * 100.0, 4),
            "label": "ESTIMATED_DAILY_BHAVCOPY_DIAGNOSTIC_NOT_ACCEPTANCE_EVIDENCE",
        },
        "bhavcopy_days_used": [d["date"] for d in daily_data],
        "input_warnings": input_warnings,
        "cost_model": {
            "brokerage_per_side": BROKERAGE_PER_SIDE,
            "stt_rate": STT_RATE,
            "exchange_txn_charge": EXCHANGE_TXN_CHARGE,
            "slippage_pct": SLIPPAGE_PCT,
            "description": "ESTIMATE ONLY; daily bhavcopy does not prove observed spread, latency, or fills",
            "status": "ASSUMED_NOT_VERIFIED",
            "spread_included": False,
            "latency_included": False,
        },
        "symbols_tested": ["NIFTY", "BANKNIFTY"],
        "strategy": "OI-change-ranked ATM CE next-day exit — walk-forward proof only, not trading signal",
        "live_trading_enabled": False,
        "note": "Walk-forward proof validates cost model and pipeline correctness. Not a performance claim.",
        "trades": trades[:20],  # first 20 for inspection
    }

    (OUT / "costed_walkforward_proof.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")

    print(f"\n[WalkForwardProof] {proof['status']}")
    print(f"  Trades: {len(trades)} | Win rate: {win_rate:.1f}%")
    print(f"  Gross P&L: ₹{total_gross_pnl:.0f} | Total costs: ₹{total_costs:.0f} | Net P&L: ₹{total_net_pnl:.0f}")
    print(f"  Report: {OUT / 'costed_walkforward_proof.json'}")
    return proof


if __name__ == "__main__":
    result = run_proof()
    sys.exit(0 if result.get("pass") else 1)
