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


def virtual_session_date(session_index: int):
    """Weekday-only synthetic calendar, not an NSE holiday-calendar claim."""
    if session_index < 0:
        raise ValueError("negative session index")
    day = datetime(2026, 11, 9, 9, 15, tzinfo=IST)
    while session_index:
        day += timedelta(days=1)
        if day.weekday() < 5:
            session_index -= 1
    return day


def virtual_order_allowed(*, price: float, quantity: int, realized_pnl: float) -> bool:
    """Offline PAPER entry gate. No live execution authority."""
    return (math.isfinite(price) and price > 0
            and isinstance(quantity, int) and not isinstance(quantity, bool)
            and quantity > 0 and math.isfinite(realized_pnl)
            and price * quantity <= CAPITAL and realized_pnl > -STOP_LOSS)


def ticks(scenario: str, count: int = 120, *, day_offset: int = 0):
    assert scenario in SCENARIOS
    start = virtual_session_date(day_offset)
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


def simulate(scenario: str, path, *, day_offset: int = 0):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE ticks (seq INTEGER PRIMARY KEY, ts TEXT NOT NULL, price REAL NOT NULL)")
    conn.execute("CREATE TABLE fills (seq INTEGER, side TEXT, price REAL, fee REAL)")
    accepted = []
    rejected = []
    previous_ts = None
    for tick in ticks(scenario, day_offset=day_offset):
        ts = tick["ts"]
        if previous_ts is not None and ts <= previous_ts:
            rejected.append((tick["sequence"], "STALE_OR_OUT_OF_ORDER"))
            continue
        if previous_ts is not None and (ts - previous_ts).total_seconds() > 2:
            rejected.append((tick["sequence"], "DISCONNECTED_GAP"))
            # Re-establish the time baseline after detecting a dropped interval.
            # The first reconnect tick is quarantined; subsequent fresh ticks resume.
            previous_ts = ts
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
        assert virtual_order_allowed(price=entry["price"], quantity=qty, realized_pnl=0.0)
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
    return {"scenario": scenario, "status": "SIMULATED_ONLY", "ticks_generated": len(list(ticks(scenario, day_offset=day_offset))),
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


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_thirty_day_virtual_paper_market_and_storage_recovery(tmp_path, scenario):
    """30 independent daily sessions; no synthetic result may be called real."""
    sessions = [simulate(scenario, tmp_path / f"{scenario}-{day:02d}.db", day_offset=day)
                for day in range(30)]
    assert len(sessions) == 30
    assert sum(x["paper_fills"] for x in sessions) == 60
    assert all(x["status"] == "SIMULATED_ONLY" for x in sessions)
    assert all(x["real_broker_orders"] == 0 for x in sessions)
    assert all(x["model_accuracy"] is None for x in sessions)
    assert all(x["ticks_generated"] == x["ticks_stored"] + x["ticks_rejected"] for x in sessions)
    for day, result in enumerate(sessions):
        with sqlite3.connect(tmp_path / f"{scenario}-{day:02d}.db") as conn:
            rows = conn.execute("SELECT seq, ts, price FROM ticks ORDER BY seq").fetchall()
            fills = conn.execute("SELECT side, fee FROM fills ORDER BY seq").fetchall()
        assert len(rows) == result["ticks_stored"]
        assert [side for side, _ in fills] == ["BUY", "SELL"]
        assert sum(fee for _, fee in fills) == result["fees"]
        assert all(price > 0 and math.isfinite(price) for _, _, price in rows)
        assert all(datetime.fromisoformat(ts).date() ==
                   virtual_session_date(day).date()
                   for _, ts, _ in rows)
    if scenario == "disconnect":
        assert all(x["ticks_stored"] >= 100 for x in sessions), "Reconnect must recover instead of freezing feed"
    if scenario == "stale":
        assert all(x["ticks_rejected"] >= 80 for x in sessions)


def test_weekends_never_generate_virtual_market_sessions():
    dates = [virtual_session_date(i).date() for i in range(30)]
    assert len(set(dates)) == 30
    assert all(date.weekday() < 5 for date in dates)
    assert dates[0].isoformat() == "2026-11-09"
    assert dates[5].isoformat() == "2026-11-16"


@pytest.mark.parametrize("price,quantity,pnl", [
    (50001.0, 1, 0.0), (100.0, 501, 0.0),
    (100.0, 1, -5000.0), (100.0, 1, -5001.0),
    (float("nan"), 1, 0.0), (float("inf"), 1, 0.0),
    (100.0, 0, 0.0), (100.0, -1, 0.0),
    (100.0, True, 0.0), (100.0, 1, float("nan")),
])
def test_virtual_entry_rejects_risk_violations(price, quantity, pnl):
    assert not virtual_order_allowed(price=price, quantity=quantity, realized_pnl=pnl)


def test_virtual_entry_accepts_only_within_limits():
    assert virtual_order_allowed(price=100.0, quantity=500, realized_pnl=-4999.0)



def test_automatic_paper_engine_gap_entry_exit_and_restart(tmp_path, monkeypatch):
    """Prove automatic tick -> simulated entry -> exit -> master recovery."""
    from dashboard.backend import cloud_paper_engine as engine_module

    ist = timezone(timedelta(hours=5, minutes=30))
    observed = [datetime(2026, 11, 9, 9, 30, tzinfo=ist)]
    monkeypatch.setattr(engine_module, "_now_ist", lambda: observed[0])
    engine = engine_module.CloudPaperEngine(tmp_path)

    chain = {
        "underlying": "NIFTY", "spot": 25000.0,
        "session_open_price": 25200.0,
        "previous_session_close": 25000.0,
        "session_open_timestamp_ist": observed[0].isoformat(),
        "opening_price_source": "SESSION_OPEN",
        "contracts": [{"strike": 25000, "option_type": "CE", "ltp": 100.0,
                       "previous_close_price": 70.0, "volume": 500, "oi_change": 100}],
    }
    engine.step([chain])
    assert len(engine.open_positions) == 1
    assert engine.master_ledger.snapshot()["gaps"]["NIFTY"]["direction"] == "GAP_UP"
    assert engine.open_positions[0]["opening_gap_status"] == "GAP_UP"

    # An exact restart reloads the hash-chain, not potentially stale UI JSON.
    restarted = engine_module.CloudPaperEngine(tmp_path)
    assert len(restarted.open_positions) == 1
    assert restarted.open_positions[0]["position_id"] == engine.open_positions[0]["position_id"]

    observed[0] = observed[0] + timedelta(minutes=1)
    chain["contracts"][0]["ltp"] = 120.0
    restarted.step([chain])
    assert len(restarted.closed_positions) >= 1
    closed = restarted.closed_positions[0]
    assert closed["exit_reason"] == "TARGET"
    assert closed["pnl_verification_status"] == "COSTED_SIMULATION_NOT_BROKER_VERIFIED"
    assert closed["realized_pnl"] < (120.0 - 100.0) * closed["qty"]
    recovered = engine_module.CloudPaperEngine(tmp_path)
    assert recovered.closed_positions[0]["position_id"] == closed["position_id"]


def test_paper_engine_never_fabricates_missing_quote_eod_exit(tmp_path, monkeypatch):
    from dashboard.backend import cloud_paper_engine as engine_module

    ist = timezone(timedelta(hours=5, minutes=30))
    observed = [datetime(2026, 11, 9, 9, 30, tzinfo=ist)]
    monkeypatch.setattr(engine_module, "_now_ist", lambda: observed[0])
    engine = engine_module.CloudPaperEngine(tmp_path)
    chain = {"underlying": "NIFTY", "spot": 25000, "contracts": [
        {"strike": 25000, "option_type": "CE", "ltp": 100.0,
         "previous_close_price": 70.0, "volume": 10}]}
    engine.step([chain])
    observed[0] = datetime(2026, 11, 9, 15, 16, tzinfo=ist)
    engine.step([{"underlying": "NIFTY", "spot": 25000, "contracts": []}])
    assert len(engine.open_positions) == 1
    assert not engine.closed_positions
    assert engine.open_positions[0]["paper_quote_status"] == "BLOCKED_NO_CURRENT_QUOTE"
    restarted = engine_module.CloudPaperEngine(tmp_path)
    assert restarted.open_positions[0]["paper_quote_status"] == "BLOCKED_NO_CURRENT_QUOTE"
    assert restarted.master_ledger.snapshot()["verified_hash_chain"] is True
