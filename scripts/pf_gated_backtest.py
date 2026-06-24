"""
Genesis System3 - Costed Walk-Forward Backtest with PROFIT-FACTOR GATE
=======================================================================
B2 FIX: Unlike the original proof (which PASSed on pipeline correctness alone),
this version applies a real profitability gate (PF >= 1.20 after costs) and a
phantom-premium data guard, so the result is an HONEST trade-readiness signal.

Key improvements over costed_walkforward_proof.py:
  1. Phantom-premium guard: drops corrupt bhavcopy rows (extrinsic > cap)
  2. Near-ATM strike filter: only trades strikes within 3% of spot
  3. Profit Factor gate: PASS only if PF >= 1.20 (gross profit / gross loss)
  4. Per-trade risk cap: skips trades exceeding MAX_RISK_PER_TRADE_RUPEES
  5. Honest verdict: backtest_pass != pipeline_pass

Writes: reports/latest/recent_backtest_walkforward_proof/pf_gated_backtest.json
Safety: LIVE_TRADING_ENABLED must be 0.
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

if os.environ.get("LIVE_TRADING_ENABLED", "0") not in ("0", "false", "False", ""):
    print("LIVE_TRADING_ENABLED is truthy - aborting.")
    sys.exit(1)

# Cost model (Dhan flat-fee plan)
BROKERAGE_PER_SIDE = 20.0
STT_RATE = 0.000625
EXCHANGE_TXN_CHARGE = 0.0005
GST_ON_BROKERAGE = 0.18
SEBI_RATE = 0.000001
SLIPPAGE_PCT = 0.001

INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"}
LOT_SIZES = {"NIFTY": 75, "BANKNIFTY": 30, "FINNIFTY": 40, "MIDCPNIFTY": 75}

# B2 gates
PF_GATE = 1.20
MAX_RISK_PER_TRADE_RUPEES = 2000.0
NEAR_ATM_PCT = 3.0           # only trade strikes within 3% of spot
PHANTOM_EXTRINSIC_PCT = 0.05  # extrinsic > 5% of spot = phantom (3% if far OTM)
MIN_PREMIUM = 10.0


def is_phantom(close, strike, spot, opt_type):
    """True if option premium is implausible (data error)."""
    if close <= 0 or spot <= 0 or strike <= 0:
        return True
    intrinsic = max(0.0, spot - strike) if opt_type == "CE" else max(0.0, strike - spot)
    extrinsic = close - intrinsic
    moneyness_pct = abs(spot - strike) / spot * 100.0
    cap = PHANTOM_EXTRINSIC_PCT * spot
    if intrinsic == 0 and moneyness_pct > 2.0:
        cap = 0.03 * spot
    return extrinsic > cap


def compute_cost(entry_price, exit_price, symbol, qty):
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
        "lots": lots, "contracts": contracts,
        "entry_value": round(entry_value, 2), "exit_value": round(exit_value, 2),
        "gross_pnl": round(gross_pnl, 2), "total_costs": round(total_costs, 2),
        "net_pnl": round(net_pnl, 2),
    }


def load_bhavcopy(csv_path):
    """Load bhavcopy with spot price for ATM detection. Returns list of dicts."""
    rows = []
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            udiff = "TckrSymb" in cols
            sym_c = "TckrSymb" if udiff else "SYMBOL"
            type_c = "OptnTp" if udiff else "OPTION_TYP"
            strike_c = "StrkPric" if udiff else "STRIKE_PR"
            close_c = "ClsPric" if udiff else "CLOSE"
            oi_c = "OpnIntrst" if udiff else "OPEN_INT"
            chg_c = "ChngInOpnIntrst" if udiff else "CHG_IN_OI"
            exp_c = "XpryDt" if udiff else "EXPIRY_DT"
            und_c = "UndrlygPric" if udiff else None
            for r in reader:
                sym = str(r.get(sym_c, "")).strip().upper()
                if sym not in INDEX_SYMBOLS:
                    continue
                ot = str(r.get(type_c, "")).strip().upper()
                if ot not in ("CE", "PE"):
                    continue
                try:
                    rows.append({
                        "symbol": sym, "option_type": ot,
                        "strike": float(r.get(strike_c, 0) or 0),
                        "close": float(r.get(close_c, 0) or 0),
                        "oi": int(float(r.get(oi_c, 0) or 0)),
                        "oi_chg": int(float(r.get(chg_c, 0) or 0)),
                        "expiry": str(r.get(exp_c, "")).strip(),
                        "spot": float(r.get(und_c, 0) or 0) if und_c else 0.0,
                    })
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"  [load] {csv_path.name} error: {e}")
    return rows


def estimate_spot(rows, symbol):
    """Estimate spot from rows if UndrlygPric missing: use strike with min |CE-PE|."""
    spots = [r["spot"] for r in rows if r["symbol"] == symbol and r["spot"] > 0]
    if spots:
        return spots[0]
    # Fallback: ATM = strike where CE and PE prices are closest
    ce = {r["strike"]: r["close"] for r in rows if r["symbol"] == symbol and r["option_type"] == "CE"}
    pe = {r["strike"]: r["close"] for r in rows if r["symbol"] == symbol and r["option_type"] == "PE"}
    common = set(ce) & set(pe)
    if not common:
        return 0.0
    atm = min(common, key=lambda k: abs(ce[k] - pe[k]))
    return atm


def run():
    started = datetime.now(timezone.utc).isoformat()
    proof_id = f"PF_GATED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    files = sorted(BHAVCOPY_DIR.glob("*_fo_bhavcopy.csv"))
    if len(files) < 2:
        result = {"proof_id": proof_id, "status": "FAIL", "pass": False,
                  "reason": f"Need >=2 bhavcopy files, found {len(files)}",
                  "hint": "Run scripts/bhavcopy_downloader.py on laptop first"}
        (OUT / "pf_gated_backtest.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return result

    daily = []
    for f in files:
        rows = load_bhavcopy(f)
        daily.append({"date": f.stem[:8], "rows": rows})

    trades = []
    dropped_phantom = 0
    skipped_far = 0
    skipped_risk = 0

    for i in range(len(daily) - 1):
        d0, d1 = daily[i], daily[i + 1]
        for symbol in INDEX_SYMBOLS:
            spot = estimate_spot(d0["rows"], symbol)
            if spot <= 0:
                continue
            # Candidate CE rows: near-ATM, non-phantom, liquid
            cands = []
            for r in d0["rows"]:
                if r["symbol"] != symbol or r["option_type"] != "CE":
                    continue
                if r["close"] < MIN_PREMIUM:
                    continue
                if is_phantom(r["close"], r["strike"], spot, "CE"):
                    dropped_phantom += 1
                    continue
                mny = abs(spot - r["strike"]) / spot * 100.0
                if mny > NEAR_ATM_PCT:
                    skipped_far += 1
                    continue
                cands.append(r)
            if not cands:
                continue
            cands.sort(key=lambda r: r["oi_chg"], reverse=True)
            signal = cands[0]
            # Risk cap check
            lot = LOT_SIZES.get(symbol, 50)
            risk = signal["close"] * lot
            if risk > MAX_RISK_PER_TRADE_RUPEES:
                skipped_risk += 1
                continue
            # Match on day 1
            m = [r for r in d1["rows"] if r["symbol"] == symbol and r["option_type"] == "CE"
                 and abs(r["strike"] - signal["strike"]) < 0.01 and r["expiry"] == signal["expiry"]]
            if not m:
                continue
            exit_row = m[0]
            if exit_row["close"] <= 0 or signal["close"] <= 0:
                continue
            cd = compute_cost(signal["close"], exit_row["close"], symbol, lot)
            trades.append({
                "symbol": symbol, "strike": signal["strike"], "expiry": signal["expiry"],
                "entry_date": d0["date"], "exit_date": d1["date"],
                "entry_price": round(signal["close"], 2), "exit_price": round(exit_row["close"], 2),
                "spot_at_entry": round(spot, 1),
                "gross_pnl": cd["gross_pnl"], "net_pnl": cd["net_pnl"],
            })

    if not trades:
        result = {"proof_id": proof_id, "status": "FAIL", "pass": False,
                  "reason": "0 trades after near-ATM + phantom + risk filters",
                  "dropped_phantom": dropped_phantom, "skipped_far_otm": skipped_far,
                  "skipped_over_risk": skipped_risk}
        (OUT / "pf_gated_backtest.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return result

    wins = [t for t in trades if t["net_pnl"] > 0]
    losses = [t for t in trades if t["net_pnl"] <= 0]
    gross_profit = sum(t["net_pnl"] for t in wins)
    gross_loss = abs(sum(t["net_pnl"] for t in losses))
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    net = sum(t["net_pnl"] for t in trades)
    win_rate = len(wins) / len(trades) * 100

    backtest_pass = pf >= PF_GATE and net > 0

    proof = {
        "proof_id": proof_id, "started": started,
        "completed": datetime.now(timezone.utc).isoformat(),
        "backtest_pass": backtest_pass,
        "pass": backtest_pass,
        "verdict": "PROFITABLE_AFTER_COSTS" if backtest_pass else "NOT_PROFITABLE_BLOCKED",
        "profit_factor": round(pf, 3) if pf != float("inf") else 999.0,
        "pf_gate": PF_GATE,
        "trade_count": len(trades),
        "win_count": len(wins), "loss_count": len(losses),
        "win_rate_pct": round(win_rate, 1),
        "total_net_pnl": round(net, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "avg_net_per_trade": round(net / len(trades), 2),
        "data_quality": {
            "dropped_phantom_rows": dropped_phantom,
            "skipped_far_otm": skipped_far,
            "skipped_over_risk_cap": skipped_risk,
        },
        "filters": {
            "near_atm_pct": NEAR_ATM_PCT,
            "max_risk_per_trade": MAX_RISK_PER_TRADE_RUPEES,
            "phantom_guard": "extrinsic > 5% spot (3% far-OTM)",
        },
        "bhavcopy_days": [d["date"] for d in daily],
        "live_trading_enabled": False,
        "strategy": "near-ATM CE, OI-change ranked, next-day exit (B2 PF-gated honest backtest)",
        "note": ("backtest_pass=True requires PF>=1.20 AND net>0 after full costs. "
                 "This is a real profitability gate, NOT a pipeline-correctness check."),
        "trades": trades[:30],
    }
    (OUT / "pf_gated_backtest.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(f"[PF-Gated Backtest] {'PASS' if backtest_pass else 'FAIL/BLOCKED'}")
    print(f"  PF={pf:.2f} (gate {PF_GATE}) | net=Rs{net:.0f} | win_rate={win_rate:.1f}% | trades={len(trades)}")
    print(f"  Dropped phantom rows: {dropped_phantom}")
    return proof


if __name__ == "__main__":
    r = run()
    sys.exit(0 if r.get("pass") else 1)
