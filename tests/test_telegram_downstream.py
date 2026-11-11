"""
Genesis System3 - Telegram Downstream Integration & Verification Suite
=======================================================================
Verifies the end-to-end downstream alert, signal dispatch, and risk circuit breaker
integration for System3boat (@System3PSWBot).
"""

import sys
import os
import json
import urllib.request
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine.telegram_notifier import TelegramNotifier, default_telegram_notifier
from core.engine.dhan_full_market_scanner import SCANNER


def test_telegram_notifier_identity():
    """Verify bot identity matches the owner's Telegram configuration (@System3PSWBot)."""
    notifier = default_telegram_notifier
    assert notifier.bot_username == "@System3PSWBot", f"Expected @System3PSWBot, got {notifier.bot_username}"
    assert notifier.bot_name == "System3boat", f"Expected System3boat, got {notifier.bot_name}"
    assert notifier.paper_mode is True, "Expected paper_mode=True"
    print("PASS: TelegramNotifier identity and paper mode verified.")


def test_signal_and_risk_formatting():
    """Verify high-precision message formatting for trade signals and RMS circuit breakers."""
    notifier = default_telegram_notifier

    # 1. Trade Signal formatting
    sig_msg = notifier.format_trade_signal(
        symbol="NIFTY",
        signal_type="BUY",
        side="BUY",
        entry_price=150.20,
        target_price=185.00,
        stop_loss=135.00,
        spot_price=25447.86,
        strike=25500,
        option_type="CE",
        expiry="27-Nov-2026",
        confidence=0.89,
        tag="#BURST #PreSangam"
    )
    assert "NIFTY 25500 CE" in sig_msg
    assert "25,447.86" in sig_msg
    assert "#BURST #PreSangam" in sig_msg
    assert "@System3PSWBot" in sig_msg

    # 2. RMS Circuit Breaker formatting
    rms_msg = notifier.format_rms_circuit_breaker(
        event_type="CIRCUIT_BREAKER_WARNING",
        current_loss_inr=4200.0,
        daily_loss_limit_inr=5000.0,
        capital_allocated_inr=50000.0,
        tripped=False
    )
    assert "5,000.00" in rms_msg
    assert "50,000.00" in rms_msg
    assert "CIRCUIT BREAKER" in rms_msg

    # 3. Paper Fill Receipt formatting
    fill_msg = notifier.format_paper_fill_receipt(
        order_id="ORD-DHAN-PAPER-9901",
        symbol="NIFTY 25500 CE",
        side="BUY",
        qty=100,
        fill_price=150.35,
        slippage_pts=0.15,
        brokerage_inr=20.0,
        stt_inr=1.88
    )
    assert "ORD-DHAN-PAPER-9901" in fill_msg
    assert "150.35" in fill_msg
    assert "+0.15 pts" in fill_msg
    assert "21.88" in fill_msg

    print("PASS: Formatting engine accurately renders signals, RMS alerts, and paper receipts.")


def test_dispatch_and_outbox_persistence():
    """Verify that dispatching persists structured JSONL entries with SHA-256 integrity."""
    notifier = default_telegram_notifier
    test_text = "🟢 Unit Test Signal: NIFTY 25500 CE BUY"

    res = notifier.dispatch(text=test_text, category="UNIT_TEST")
    assert res["success"] is True
    assert "hash" in res
    assert len(res["hash"]) == 64
    assert res["bot"] == "@System3PSWBot"

    # Verify that outbox file exists and contains the dispatched entry
    outbox = notifier.get_recent_outbox(limit=5)
    assert len(outbox) > 0
    latest = outbox[-1]
    assert latest["text"] == test_text
    assert latest["category"] == "UNIT_TEST"
    assert latest["bot_username"] == "@System3PSWBot"
    print(f"PASS: Outbox persistence verified. Total entries logged: {len(outbox)}.")


def test_command_handling():
    """Verify simulated and webhook slash commands (/status, /pnl, /risk, /chains)."""
    notifier = default_telegram_notifier

    status_reply = notifier.handle_command("/status")
    assert "@System3PSWBot" in status_reply
    assert "ONLINE" in status_reply

    risk_reply = notifier.handle_command("/risk")
    assert "50,000.00" in risk_reply
    assert "5,000.00" in risk_reply
    assert "ARMED_HEALTHY" in risk_reply

    pnl_reply = notifier.handle_command("/pnl")
    assert "Net P&L" in pnl_reply

    chains_reply = notifier.handle_command("/chains")
    assert "NIFTY Spot" in chains_reply
    print("PASS: Inbound command processor (/status, /risk, /pnl, /chains) verified.")


def test_scanner_order_bind_auto_dispatch():
    """Verify that simulated order execution in DhanFullMarketScanner automatically dispatches to Telegram."""
    init_outbox_count = len(default_telegram_notifier.get_recent_outbox(limit=10000))

    # Execute simulated paper order
    res = SCANNER.bind_order_execution(
        underlying="NIFTY",
        strike=25500,
        option_type="CE",
        transaction_type="BUY",
        quantity=50,
        price=150.0
    )
    assert res["status"] == "SUCCESS"
    assert res["execution_mode"] == "PAPER"
    assert "ORD-DHAN-PAPER-" in res["order_id"]

    # Verify that outbox received the execution fill receipt
    after_outbox = default_telegram_notifier.get_recent_outbox(limit=10000)
    assert len(after_outbox) >= init_outbox_count + 1
    new_entry = after_outbox[-1]
    assert new_entry["category"] == "PAPER_EXECUTION"
    assert res["order_id"] in new_entry["text"]
    print("PASS: Scanner order bind auto-dispatch to Telegram outbox verified.")


def test_live_asgi_telegram_endpoints():
    """Verify that all live ASGI REST endpoints for Telegram return HTTP 200 OK."""
    base = "http://127.0.0.1:8008"

    # 1. /api/telegram/status
    with urllib.request.urlopen(f"{base}/api/telegram/status", timeout=15) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["data"]["bot_username"] == "@System3PSWBot"
        assert data["data"]["health"] == "ONLINE"

    # 2. /api/telegram/test-alert
    req_alert = urllib.request.Request(f"{base}/api/telegram/test-alert", method="POST")
    with urllib.request.urlopen(req_alert, timeout=15) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["data"]["success"] is True

    # 3. /api/telegram/outbox
    with urllib.request.urlopen(f"{base}/api/telegram/outbox", timeout=15) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert data["data"]["count"] > 0

    # 4. /api/telegram/command
    req_cmd = urllib.request.Request(f"{base}/api/telegram/command?command=/risk", method="POST")
    with urllib.request.urlopen(req_cmd, timeout=15) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "50,000.00" in data["data"]["reply"]

    print("PASS: Live ASGI Telegram REST endpoints verified with HTTP 200 OK.")


if __name__ == "__main__":
    print("=== Running Genesis System3 Telegram Downstream Test Suite ===")
    test_telegram_notifier_identity()
    test_signal_and_risk_formatting()
    test_dispatch_and_outbox_persistence()
    test_command_handling()
    test_scanner_order_bind_auto_dispatch()
    test_live_asgi_telegram_endpoints()
    print("=== ALL 6 TELEGRAM DOWNSTREAM TESTS PASSED SUCCESSFULLY! ===")
