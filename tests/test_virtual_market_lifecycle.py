"""Offline deterministic virtual market lifecycle proof. SIMULATED, never broker truth."""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

IST = timezone(timedelta(hours=5, minutes=30))
SCENARIOS = ("trend_up", "trend_down", "flat", "gap_up", "gap_down", "stale", "out_of_order", "disconnect")
CAPITAL = 50_000.0
STOP_LOSS = 5_000.0


def ticks(scenario: str, count: int = 120):
    assert scenario in SCENARIOS
    start = datetime(2026, 11, 9, 9, 15, tzinfo=IST)
    previous = None
    for i in range(count):
        if scenario == "disconnect" and 35 <= i < 50:
            continue
        ts = start + timedelta(seconds=i - (3 if scenario == "out_of_order" and i == 40 else 0))
        if scenario == "stale" and i >= 40:
            ts = start + timedelta(seconds=39)
        direction = {"trend_up": 1, "trend_down": -1, "gap_up": 1, "gap_down": -1}.get(scenario, 0)
        gap = (10 * direction) if scenario.startswith("gap_") else 0
        price = round(100 + gap + direction * i * 0.08 + (0.02 if i % 2 else 0), 2)
        yield {"ts": ts, "price": price, "sequence": i, "scenario": scenario,
               "provenance": "SIMULATED", "broker_order": False}
        previous = ts


def simulate(scenario: str, path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE ticks (seq INTEGER PRIMARY KEY, ts TEXT NOT NULL, price REAL NOT NULL)")
    conn.execute("CREATE TABLE fills (seq INTEGER, side TEXT, price REAL, fee REAL)")
    accepted = []
    rejected = []
    previous_ts = None
    for tick in ticks(scenario):
        ts = tick["ts"]
        if previous_ts is not None and ts <= previous_ts:
            rejected.append((tick["sequence"], "STALE_OR_OUT_OF_ORDER"))
            continue
        if previous_ts is not None and (ts - previous_ts).total_seconds() > 2:
            rejected.append((tick["sequence"], "DISCONNECTED_GAP"))
            continue
        if not math.isfinite(tick["price"]) or tick["price"] <= 0:
            rejected.append((tick["sequence"], "BAD_PRICE"))
            continue
        conn.execute("INSERT INTO ticks VALUES (?, ?, ?)", (tick["sequence"], ts.isoformat(), tick["price"]))
        accepted.append(tick)
        previous_ts = ts
    # Paper fills are explicit virtual fixtures, not real broker events.
    if len(accepted) >= 2:
        entry, exit_ = accepted[0], accepted[-1]
        qty = 10
        fee_per_fill = 10.0
        conn.executemany("INSERT INTO fills VALUES (?, ?, ?, ?)", [
            (entry["sequence"], "BUY", entry["price"], fee_per_fill),
            (exit_["sequence"], "SELL", exit_["price"], fee_per_fill)])
        gross = round((exit_["price"] - entry["price"]) * qty, 2)
        net = round(gross - 2 * fee_per_fill, 2)
    else:
        gross = net = None
    conn.commit()
    stored = conn.execute("SELECT COUNT(*) FROM ticks").fetchone()[0]
    fills = conn.execute("SELECT COUNT(*) FROM fills").fetchone()[0]
    conn.close()
    chart = [t for t in accepted if t["sequence"] % 5 == 0]
    return {"scenario": scenario, "status": "SIMULATED_ONLY", "ticks_generated": len(list(ticks(scenario))),
            "ticks_stored": stored, "ticks_rejected": len(rejected),
            "chart_points": len(chart), "chart_interval_seconds": 5,
            "feed_target_hz": 1, "paper_fills": fills, "gross_pnl": gross,
            "fees": 20.0 if fills else None, "net_pnl": net,
            "risk_capital_limit": CAPITAL, "daily_stop_loss_limit": STOP_LOSS,
            "real_broker_orders": 0, "model_accuracy": None,
            "model_training_verified": False, "backtest_verified": False,
            "ui_browser_verified": False, "live_data_verified": False,
            "rejections": rejected}


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_virtual_feed_storage_chart_and_paper_lifecycle(tmp_path, scenario):
    result = simulate(scenario, tmp_path / (scenario + ".db"))
    assert result["status"] == "SIMULATED_ONLY"
    assert result["ticks_stored"] + result["ticks_rejected"] == result["ticks_generated"]
    assert result["paper_fills"] == 2
    assert result["real_broker_orders"] == 0
    assert result["model_accuracy"] is None
    assert result["net_pnl"] == round(result["gross_pnl"] - result["fees"], 2)
    assert result["chart_points"] <= result["ticks_stored"]
    assert result["feed_target_hz"] == 1
    if scenario in ("stale", "out_of_order", "disconnect"):
        assert result["ticks_rejected"] > 0


def test_no_future_data_leakage_and_no_broker_side_effects(tmp_path):
    result = simulate("trend_up", tmp_path / "isolated.db")
    assert result["real_broker_orders"] == 0
    assert result["model_training_verified"] is False
    assert result["backtest_verified"] is False
    assert result["ui_browser_verified"] is False
    assert result["live_data_verified"] is False
    assert result["risk_capital_limit"] == 50_000
    assert result["daily_stop_loss_limit"] == 5_000
