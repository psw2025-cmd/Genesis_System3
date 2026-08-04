"""
Genesis System3 — Costed Walk-Forward Backtest Proof
=====================================================
Runs a walk-forward simulation on available bhavcopy data with realistic
brokerage + slippage + spread costs.

Data-quality guards (prevent corrupt bhavcopy rows from poisoning results):
  - Phantom-premium guard: drops rows whose extrinsic value is implausible
  - Near-ATM filter: only trades strikes within NEAR_ATM_PCT % of spot
  - Per-trade risk cap: skips trades exceeding MAX_RISK_PER_TRADE_RUPEES
  - Directional signal: uses PCR (put-call ratio) to choose CE vs PE

Profit-factor gate (honest trade-readiness signal):
  - PASS only when PF >= PF_GATE AND net_pnl > 0
  - pipeline_pass (cost model works) is separate from backtest_pass (profitable)

Writes proof to:
  reports/latest/recent_backtest_walkforward_proof/costed_walkforward_proof.json

Safety: LIVE_TRADING_ENABLED must be 0 (always checked).
"""

import csv
import json
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

INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}
LOT_SIZES = {"NIFTY": 75, "BANKNIFTY": 30, "FINNIFTY": 40, "MIDCPNIFTY": 75}

# Data-quality and risk gates
NEAR_ATM_PCT = 3.0            # only trade strikes within 3% of spot
PHANTOM_EXTRINSIC_PCT = 0.05  # extrinsic > 5% of spot = phantom premium
PHANTOM_FAR_OTM_PCT = 0.03   # tighter cap (3%) when strike is far OTM
PF_GATE = 1.20                # profit-factor threshold for backtest_pass=True
MAX_RISK_PER_TRADE_RUPEES = 5000.0  # skip trades with premium × lot > this
MIN_PREMIUM = 10.0            # skip options priced below ₹10 (illiquid)


def is_phantom(close: float, strike: float, spot: float, opt_type: str) -> bool:
    """True if option premium is implausible given spot/strike (data corruption guard)."""
    if close <= 0 or spot <= 0 or strike <= 0:
        return True
    intrinsic = max(0.0, spot - strike) if opt_type == "CE" else max(0.0, strike - spot)
    extrinsic = close - intrinsic
    moneyness_pct = abs(spot - strike) / spot * 100.0
    cap = PHANTOM_EXTRINSIC_PCT * spot
    # Tighter cap for far-OTM (no intrinsic): extrinsic alone must be < 3% of spot
    if intrinsic == 0 and moneyness_pct > 2.0:
        cap = PHANTOM_FAR_OTM_PCT * spot
    return extrinsic > cap


def compute_cost(entry_price: float, exit_price: float, symbol: str, qty: int) -> dict:
    lot_size = LOT_SIZES.get(symbol, 50)
    lots = max(1, qty // lot_size)
    contracts = lots * lot_size

    entry_value = entry_price * contracts
    exit_value = exit_price * contracts

    entry_slip = entry_value * SLIPPAGE_PCT
    exit_slip = exit_value * SLIPPAGE_PCT
    gross_pnl = (exit_price - entry_price) * contracts
    brokerage = BROKERAGE_PER_SIDE * 2
    stt = exit_value * STT_RATE
    exc = (entry_value + exit_value) * EXCHANGE_TXN_CHARGE
    gst = (brokerage + exc) * GST_ON_BROKERAGE
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
    """Load bhavcopy rows for index option symbols. Handles UDiFF and legacy formats."""
    rows = []
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            udiff = "TckrSymb" in headers
            sym_col = "TckrSymb" if udiff else ("Symbol" if "Symbol" in headers else None)
            close_col = "ClsPric" if udiff else ("Close" if "Close" in headers else None)
            oi_col = "OpnIntrst" if udiff else ("OI" if "OI" in headers else None)
            oi_chg_col = "ChngInOpnIntrst" if udiff else None
            type_col = "OptnTp" if udiff else ("OptTp" if "OptTp" in headers else "OptionType")
            strike_col = "StrkPric" if udiff else ("Strike" if "Strike" in headers else "StrkPric")
            expiry_col = "XpryDt" if udiff else ("Expiry" if "Expiry" in headers else "XpryDt")
            und_col = "UndrlygPric" if "UndrlygPric" in headers else None

            if not sym_col or not close_col:
                return rows

            for row in reader:
                sym = (row.get(sym_col) or "").strip().upper()
                if sym not in INDEX_SYMBOLS:
                    continue
                ot = (row.get(type_col) or "").strip().upper()
                if ot not in ("CE", "PE"):
                    continue
                try:
                    rows.append({
                        "symbol": sym,
                        "option_type": ot,
                        "strike": float(row.get(strike_col) or 0),
                        "close": float(row.get(close_col) or 0),
                        "oi": float(row.get(oi_col) or 0),
                        "oi_chg": float(row.get(oi_chg_col) or 0) if oi_chg_col else 0.0,
                        "expiry": str(row.get(expiry_col) or "").strip(),
                        "spot": float(row.get(und_col) or 0) if und_col else 0.0,
                    })
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"  [load_bhavcopy] Error reading {csv_path.name}: {e}")
    return rows


def estimate_spot(rows: list[dict], symbol: str) -> float:
    """
    Estimate spot from UndrlygPric if present; otherwise use CE/PE parity
    (strike where |CE_price - PE_price| is minimal = ATM = spot proxy).
    """
    spots = [r["spot"] for r in rows if r["symbol"] == symbol and r["spot"] > 0]
    if spots:
        return spots[0]
    # Parity fallback
    ce = {r["strike"]: r["close"] for r in rows if r["symbol"] == symbol and r["option_type"] == "CE"}
    pe = {r["strike"]: r["close"] for r in rows if r["symbol"] == symbol and r["option_type"] == "PE"}
    common = set(ce) & set(pe)
    if not common:
        return 0.0
    atm_strike = min(common, key=lambda k: abs(ce[k] - pe[k]))
    return float(atm_strike)


def estimate_pcr(rows: list[dict], symbol: str, spot: float) -> float:
    """Compute put-call ratio from OI of near-ATM options (within 2× NEAR_ATM_PCT)."""
    band = spot * (NEAR_ATM_PCT * 2 / 100.0)
    ce_oi = sum(r["oi"] for r in rows if r["symbol"] == symbol and r["option_type"] == "CE"
                and abs(r["strike"] - spot) <= band)
    pe_oi = sum(r["oi"] for r in rows if r["symbol"] == symbol and r["option_type"] == "PE"
                and abs(r["strike"] - spot) <= band)
    return pe_oi / ce_oi if ce_oi > 0 else 1.0


def run_proof() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    proof_id = f"WALKFORWARD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"[WalkForwardProof] Starting {proof_id}")

    bhavcopy_files = sorted(BHAVCOPY_DIR.glob("*_fo_bhavcopy.csv"))
    if len(bhavcopy_files) < 2:
        result = {
            "proof_id": proof_id,
            "started": started,
            "status": "FAIL",
            "pass": False,
            "backtest_pass": False,
            "pipeline_pass": False,
            "recent_costed_walkforward_proven": False,
            "reason": f"Need ≥2 bhavcopy files, found {len(bhavcopy_files)}",
            "hint": "Run scripts/bhavcopy_downloader.py --backfill 90 first",
        }
        (OUT / "costed_walkforward_proof.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return result

    print(f"  Found {len(bhavcopy_files)} bhavcopy files")

    daily_data = []
    for f in bhavcopy_files:
        rows = load_bhavcopy(f)
        date_str = f.stem[:8]
        daily_data.append({"date": date_str, "rows": rows})
        print(f"  {date_str}: {len(rows)} index option rows")

    trades = []
    dropped_phantom = 0
    skipped_far = 0
    skipped_risk = 0
    walk_pairs = 0

    for i in range(len(daily_data) - 1):
        d0, d1 = daily_data[i], daily_data[i + 1]

        for symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
            spot = estimate_spot(d0["rows"], symbol)
            if spot <= 0:
                continue

            # PCR-based direction: PCR > 1.2 → bearish → buy PE; else → buy CE
            pcr = estimate_pcr(d0["rows"], symbol, spot)
            direction = "PE" if pcr > 1.2 else "CE"

            # Candidate rows for the chosen direction
            cands = []
            for r in d0["rows"]:
                if r["symbol"] != symbol or r["option_type"] != direction:
                    continue
                if r["close"] < MIN_PREMIUM:
                    continue
                if is_phantom(r["close"], r["strike"], spot, direction):
                    dropped_phantom += 1
                    continue
                mny_pct = abs(spot - r["strike"]) / spot * 100.0
                if mny_pct > NEAR_ATM_PCT:
                    skipped_far += 1
                    continue
                cands.append(r)

            if not cands:
                continue

            # Rank by OI change (highest buildup = strongest conviction)
            cands.sort(key=lambda r: r["oi_chg"], reverse=True)
            signal = cands[0]

            # Risk cap: premium × lot_size must be within budget
            lot = LOT_SIZES.get(symbol, 50)
            risk = signal["close"] * lot
            if risk > MAX_RISK_PER_TRADE_RUPEES:
                skipped_risk += 1
                continue

            # Match on exit day
            matches = [
                r for r in d1["rows"]
                if r["symbol"] == symbol
                and r["option_type"] == direction
                and abs(r["strike"] - signal["strike"]) < 0.01
                and r["expiry"] == signal["expiry"]
            ]
            if not matches:
                continue

            exit_row = matches[0]
            if exit_row["close"] <= 0:
                continue

            cd = compute_cost(signal["close"], exit_row["close"], symbol, lot)
            trades.append({
                "symbol": symbol,
                "strike": signal["strike"],
                "expiry": signal["expiry"],
                "option_type": direction,
                "direction_basis": f"PCR={pcr:.2f}",
                "entry_date": d0["date"],
                "exit_date": d1["date"],
                "entry_price": round(signal["close"], 2),
                "exit_price": round(exit_row["close"], 2),
                "spot_at_entry": round(spot, 1),
                "pcr_at_entry": round(pcr, 3),
                "oi_at_entry": signal["oi"],
                "oi_chg_at_entry": signal["oi_chg"],
                "cost_model": cd,
            })
            walk_pairs += 1

    if not trades:
        result = {
            "proof_id": proof_id,
            "started": started,
            "status": "FAIL",
            "pass": False,
            "backtest_pass": False,
            "pipeline_pass": False,
            "recent_costed_walkforward_proven": False,
            "reason": "0 trades after near-ATM + phantom + risk filters",
            "data_quality": {
                "dropped_phantom_rows": dropped_phantom,
                "skipped_far_otm": skipped_far,
                "skipped_over_risk_cap": skipped_risk,
            },
        }
        (OUT / "costed_walkforward_proof.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return result

    wins = [t for t in trades if t["cost_model"]["net_pnl"] > 0]
    losses = [t for t in trades if t["cost_model"]["net_pnl"] <= 0]
    gross_profit = sum(t["cost_model"]["net_pnl"] for t in wins)
    gross_loss = abs(sum(t["cost_model"]["net_pnl"] for t in losses))
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    net = sum(t["cost_model"]["net_pnl"] for t in trades)
    total_costs_sum = sum(t["cost_model"]["total_costs"] for t in trades)
    total_gross = sum(t["cost_model"]["gross_pnl"] for t in trades)
    win_rate = len(wins) / len(trades) * 100

    # pipeline_pass: pipeline ran, trades generated, costs applied — regardless of profit
    pipeline_pass = True
    # backtest_pass: requires real profitability — PF >= gate AND net > 0
    backtest_pass = pf >= PF_GATE and net > 0
    # recent_costed_walkforward_proven: pipeline is always proven if pipeline ran
    recent_proven = pipeline_pass

    proof = {
        "proof_id": proof_id,
        "started": started,
        "completed": datetime.now(timezone.utc).isoformat(),
        "pass": recent_proven,
        "pipeline_pass": pipeline_pass,
        "backtest_pass": backtest_pass,
        "status": "PASS" if recent_proven else "FAIL",
        "verdict": "PROFITABLE_AFTER_COSTS" if backtest_pass else "NOT_PROFITABLE",
        "recent_costed_walkforward_proven": recent_proven,
        "costs_slippage_included_proven": True,
        "profit_factor": round(pf, 3) if pf != float("inf") else 999.0,
        "pf_gate": PF_GATE,
        "walk_pairs": walk_pairs,
        "trade_count": len(trades),
        "win_trades": len(wins),
        "loss_trades": len(losses),
        "win_rate_pct": round(win_rate, 1),
        "total_gross_pnl": round(total_gross, 2),
        "total_costs": round(total_costs_sum, 2),
        "total_net_pnl": round(net, 2),
        "avg_net_pnl_per_trade": round(net / len(trades), 2),
        "bhavcopy_days_used": [d["date"] for d in daily_data],
        "cost_model": {
            "brokerage_per_side": BROKERAGE_PER_SIDE,
            "stt_rate": STT_RATE,
            "exchange_txn_charge": EXCHANGE_TXN_CHARGE,
            "slippage_pct": SLIPPAGE_PCT,
            "description": "Dhan flat-fee plan: ₹20/side + STT + exc charge + 18% GST + SEBI",
        },
        "data_quality": {
            "dropped_phantom_rows": dropped_phantom,
            "skipped_far_otm": skipped_far,
            "skipped_over_risk_cap": skipped_risk,
        },
        "filters": {
            "near_atm_pct": NEAR_ATM_PCT,
            "max_risk_per_trade_rupees": MAX_RISK_PER_TRADE_RUPEES,
            "phantom_guard": "extrinsic > 5% spot (3% far-OTM)",
            "direction": "PCR>1.2 → PE (bearish), else CE (bullish)",
        },
        "symbols_tested": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
        "strategy": "PCR-directional near-ATM OI-ranked next-day exit with full cost model",
        "live_trading_enabled": False,
        "note": (
            "pipeline_pass=True means costs+pipeline work correctly. "
            "backtest_pass=True requires PF≥1.20 AND net>0 after costs. "
            "Collect ≥60 trading days of bhavcopy for statistical significance."
        ),
        "trades": trades[:30],
    }

    (OUT / "costed_walkforward_proof.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")

    status_str = "BACKTEST_PASS" if backtest_pass else "PIPELINE_PASS_BACKTEST_PENDING"
    print(f"\n[WalkForwardProof] {status_str}")
    print(f"  Trades={len(trades)} | WinRate={win_rate:.1f}% | PF={pf:.2f} (gate {PF_GATE})")
    print(f"  Net=₹{net:.0f} | Costs=₹{total_costs_sum:.0f} | Phantom dropped={dropped_phantom}")
    print(f"  Report: {OUT / 'costed_walkforward_proof.json'}")
    return proof


if __name__ == "__main__":
    result = run_proof()
    # Exit 0 if pipeline ran (even if not profitable yet); exit 1 only on error
    sys.exit(0 if result.get("pipeline_pass") else 1)
