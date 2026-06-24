"""
Cloud Paper Trading Loop — Genesis System3
===========================================
Runs INSIDE the dashboard backend as a background task during market hours.
Generates realistic single-lot paper trades from the LIVE option chain so the
Paper tab shows activity when the market is open.

SAFETY:
  - PAPER ONLY. No broker order calls. LIVE_TRADING_ENABLED never checked True.
  - Respects B1 phantom guard (skips implausible premiums)
  - Single lot per trade, realistic entry/exit with slippage
  - Writes positions_live.json, pnl_live.json, paper_trades_live.csv

This is a SIMULATION for monitoring/validation, not a profitability claim.
"""

from __future__ import annotations
import csv
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

IST = timezone(timedelta(hours=5, minutes=30))

LOT_SIZES = {"NIFTY": 75, "BANKNIFTY": 30, "FINNIFTY": 40, "MIDCPNIFTY": 75, "SENSEX": 20}
BROKERAGE_PER_SIDE = 20.0
STT_RATE = 0.000625
EXCHANGE_TXN_CHARGE = 0.0005
GST_ON_BROKERAGE = 0.18
SLIPPAGE_PCT = 0.001

# Paper SL/TP (matches Phase C protection settings)
SL_PCT = 12.0
TARGET_PCT = 18.0
NEAR_ATM_PCT = 3.0


def _now_ist() -> datetime:
    return datetime.now(IST)


def _ist_str(dt: Optional[datetime] = None) -> str:
    dt = dt or _now_ist()
    return dt.strftime("%Y-%m-%d %H:%M:%S IST")


def _is_phantom(ltp: float, strike: float, spot: float, opt_type: str) -> bool:
    if ltp <= 0 or spot <= 0 or strike <= 0:
        return True
    intrinsic = max(0.0, spot - strike) if opt_type == "CE" else max(0.0, strike - spot)
    extrinsic = ltp - intrinsic
    mny = abs(spot - strike) / spot * 100.0
    cap = 0.05 * spot
    if intrinsic == 0 and mny > 2.0:
        cap = 0.03 * spot
    return extrinsic > cap


def _compute_net_pnl(entry: float, exit_p: float, symbol: str) -> float:
    lot = LOT_SIZES.get(symbol, 50)
    gross = (exit_p - entry) * lot
    ev, xv = entry * lot, exit_p * lot
    brokerage = BROKERAGE_PER_SIDE * 2
    stt = xv * STT_RATE
    exc = (ev + xv) * EXCHANGE_TXN_CHARGE
    gst = (brokerage + exc) * GST_ON_BROKERAGE
    slip = (ev + xv) * SLIPPAGE_PCT
    return round(gross - (brokerage + stt + exc + gst + slip), 2)


class CloudPaperEngine:
    """Lightweight in-process paper trading. State persisted to JSON/CSV."""

    def __init__(self, outputs_dir: Path):
        self.out = outputs_dir
        self.positions_file = outputs_dir / "positions_live.json"
        self.pnl_file = outputs_dir / "pnl_live.json"
        self.trades_csv = outputs_dir / "paper_trades_live.csv"
        self.state_file = outputs_dir / "paper_engine_state.json"
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                s = json.loads(self.state_file.read_text())
                self.open_positions = s.get("open_positions", [])
                self.closed_positions = s.get("closed_positions", [])
                self.seq = s.get("seq", 0)
                self.session_date = s.get("session_date", "")
                return
            except Exception:
                pass
        self.open_positions = []
        self.closed_positions = []
        self.seq = 0
        self.session_date = ""

    def _save_state(self):
        try:
            self.state_file.write_text(json.dumps({
                "open_positions": self.open_positions,
                "closed_positions": self.closed_positions,
                "seq": self.seq,
                "session_date": self.session_date,
            }, indent=2))
        except Exception:
            pass

    def _reset_if_new_day(self):
        today = _now_ist().strftime("%Y-%m-%d")
        if self.session_date != today:
            self.session_date = today
            self.open_positions = []
            self.closed_positions = []
            self.seq = 0

    def _pick_signal(self, chain: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Pick one near-ATM contract by highest OI change. Phantom-guarded."""
        contracts = chain.get("contracts", [])
        spot = float(chain.get("spot", 0) or 0)
        underlying = chain.get("underlying", "NIFTY")
        if spot <= 0 or not contracts:
            return None
        cands = []
        for c in contracts:
            strike = float(c.get("strike", 0) or 0)
            for ot in ("CE", "PE"):
                ltp = float(c.get(f"{ot.lower()}_ltp", c.get("ltp", 0)) or 0)
                if ltp < 10:
                    continue
                if _is_phantom(ltp, strike, spot, ot):
                    continue
                mny = abs(spot - strike) / spot * 100.0
                if mny > NEAR_ATM_PCT:
                    continue
                oi_chg = abs(float(c.get(f"{ot.lower()}_oi_change", c.get("oi_change", 0)) or 0))
                cands.append({"underlying": underlying, "strike": strike,
                              "option_type": ot, "ltp": ltp, "oi_chg": oi_chg})
        if not cands:
            return None
        cands.sort(key=lambda x: x["oi_chg"], reverse=True)
        return cands[0]

    def step(self, chains: List[Dict[str, Any]], max_open: int = 3):
        """One engine tick: update open positions, maybe open a new one."""
        self._reset_if_new_day()
        now = _now_ist()

        # 1. Update open positions — check SL/TP using current chain LTP
        chain_by_key = {}
        for ch in chains:
            for c in ch.get("contracts", []):
                strike = float(c.get("strike", 0) or 0)
                for ot in ("CE", "PE"):
                    ltp = float(c.get(f"{ot.lower()}_ltp", c.get("ltp", 0)) or 0)
                    if ltp > 0:
                        chain_by_key[(ch.get("underlying"), strike, ot)] = ltp

        still_open = []
        for pos in self.open_positions:
            key = (pos["underlying"], pos["strike"], pos["option_type"])
            cur = chain_by_key.get(key, pos["entry_price"])
            entry = pos["entry_price"]
            chg_pct = (cur - entry) / entry * 100.0 if entry > 0 else 0.0
            exit_reason = None
            if chg_pct <= -SL_PCT:
                exit_reason = "STOP_LOSS"
            elif chg_pct >= TARGET_PCT:
                exit_reason = "TARGET"
            elif now.strftime("%H:%M") >= "15:15":
                exit_reason = "EOD_SQUAREOFF"
            if exit_reason:
                net = _compute_net_pnl(entry, cur, pos["underlying"])
                closed = {**pos, "action": "CLOSE", "exit_price": round(cur, 2),
                          "exit_reason": exit_reason, "realized_pnl": net,
                          "realized_pnl_pct": round(chg_pct, 2),
                          "time_ist": _ist_str(now)}
                self.closed_positions.append(closed)
                self._append_trade_csv(closed, "CLOSE")
            else:
                pos["current_price"] = round(cur, 2)
                pos["unrealized_pnl"] = _compute_net_pnl(entry, cur, pos["underlying"])
                still_open.append(pos)
        self.open_positions = still_open

        # 2. Maybe open a new position (one per tick, respect max_open)
        if len(self.open_positions) < max_open:
            best = None
            for ch in chains:
                sig = self._pick_signal(ch)
                if sig and (best is None or sig["oi_chg"] > best["oi_chg"]):
                    best = sig
            if best:
                # Avoid duplicate open on same contract
                dup = any(p["underlying"] == best["underlying"] and p["strike"] == best["strike"]
                          and p["option_type"] == best["option_type"] for p in self.open_positions)
                if not dup:
                    self.seq += 1
                    pos = {
                        "position_id": f"POS_{self.seq:04d}",
                        "action": "OPEN",
                        "underlying": best["underlying"],
                        "strike": best["strike"],
                        "option_type": best["option_type"],
                        "entry_price": round(best["ltp"], 2),
                        "current_price": round(best["ltp"], 2),
                        "qty": LOT_SIZES.get(best["underlying"], 50),
                        "strategy": f"BUY_{best['option_type']}",
                        "unrealized_pnl": 0.0,
                        "timestamp": now.isoformat(),
                        "time_ist": _ist_str(now),
                    }
                    self.open_positions.append(pos)
                    self._append_trade_csv(pos, "OPEN")

        self._write_outputs()
        self._save_state()

    def _append_trade_csv(self, pos: Dict[str, Any], action: str):
        header = ["position_id", "action", "timestamp", "time_ist", "underlying",
                  "strike", "option_type", "price", "qty", "strategy", "exit_reason",
                  "realized_pnl", "realized_pnl_pct", "entry_price", "exit_price"]
        exists = self.trades_csv.exists()
        try:
            with open(self.trades_csv, "a", newline="") as f:
                w = csv.writer(f)
                if not exists:
                    w.writerow(header)
                w.writerow([
                    pos.get("position_id"), action, pos.get("timestamp", _now_ist().isoformat()),
                    pos.get("time_ist"), pos.get("underlying"), pos.get("strike"),
                    pos.get("option_type"),
                    pos.get("exit_price" if action == "CLOSE" else "entry_price"),
                    pos.get("qty"), pos.get("strategy", ""),
                    pos.get("exit_reason", ""), pos.get("realized_pnl", ""),
                    pos.get("realized_pnl_pct", ""), pos.get("entry_price", ""),
                    pos.get("exit_price", ""),
                ])
        except Exception:
            pass

    def _write_outputs(self):
        total_realized = sum(p.get("realized_pnl", 0) for p in self.closed_positions)
        total_unreal = sum(p.get("unrealized_pnl", 0) for p in self.open_positions)
        wins = [p for p in self.closed_positions if p.get("realized_pnl", 0) > 0]
        ts = _ist_str()
        positions_out = {
            "timestamp_ist": ts,
            "open_positions": self.open_positions,
            "summary": {
                "open_count": len(self.open_positions),
                "closed_count": len(self.closed_positions),
                "total_unrealized_pnl": round(total_unreal, 2),
                "total_realized_pnl": round(total_realized, 2),
                "total_pnl": round(total_realized + total_unreal, 2),
                "open_positions": self.open_positions,
                "closed_positions": self.closed_positions,
            },
        }
        pnl_out = {
            "timestamp": _now_ist().isoformat(),
            "timestamp_ist": ts,
            "total_trades": len(self.closed_positions),
            "winning_trades": len(wins),
            "losing_trades": len(self.closed_positions) - len(wins),
            "win_rate": round(len(wins) / len(self.closed_positions) * 100, 2) if self.closed_positions else 0.0,
            "total_realized_pnl": round(total_realized, 2),
            "total_unrealized_pnl": round(total_unreal, 2),
            "total_pnl": round(total_realized + total_unreal, 2),
            "avg_pnl_per_trade": round(total_realized / len(self.closed_positions), 2) if self.closed_positions else 0.0,
            "open_positions": len(self.open_positions),
            "mode": "PAPER_CLOUD_SIM",
            "live_trading_enabled": False,
        }
        try:
            self.positions_file.write_text(json.dumps(positions_out, indent=2))
            self.pnl_file.write_text(json.dumps(pnl_out, indent=2))
        except Exception:
            pass


_engine: Optional[CloudPaperEngine] = None


def get_paper_engine(outputs_dir: Path) -> CloudPaperEngine:
    global _engine
    if _engine is None:
        _engine = CloudPaperEngine(outputs_dir)
    return _engine
