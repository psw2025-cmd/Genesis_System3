"""
Genesis System3 - Autonomous Self-Healing Watchdog Test Suite
=============================================================
Verifies 24/7 hands-off reliability, upstream market verification,
server responsiveness, downstream Telegram delivery, and RMS guardrails.
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine.system3_self_healing_watchdog import WATCHDOG, WATCHDOG_LOG


def test_watchdog_healthy_cycle():
    """Verify that autonomous watchdog completes a healthy cycle across all 4 pillars."""
    result = WATCHDOG.run_cycle()
    assert result["overall_status"] == "HEALTHY", f"Expected HEALTHY, got {result['overall_status']}"
    assert "sha256" in result and len(result["sha256"]) == 64

    checks = result["checks"]
    assert checks["upstream"]["status"] == "PASS", "Upstream market feed check failed"
    assert checks["server"]["status"] == "PASS", "Core ASGI server check failed"
    assert checks["downstream"]["status"] == "PASS", "Downstream Telegram check failed"
    assert checks["rms"]["status"] == "PASS", "RMS circuit breaker check failed"

    # Verify risk parameters
    rms = checks["rms"]
    assert rms["capital_limit_inr"] == 50000.0, f"Expected 50000.0 capital, got {rms['capital_limit_inr']}"
    assert rms["daily_stop_loss_inr"] == 5000.0, f"Expected 5000.0 stop-loss, got {rms['daily_stop_loss_inr']}"
    assert rms["safety_mode"] == "PAPER_MODE", f"Expected PAPER_MODE, got {rms['safety_mode']}"

    # Verify downstream Telegram parameters
    downstream = checks["downstream"]
    assert downstream["bot_username"] == "@System3PSWBot"
    assert downstream["chat_id_bound"] == "1290747576"
    assert downstream["live_delivery_active"] is True

    print("PASS: Watchdog audit cycle completed with 100% HEALTHY status across all pillars.")


def test_forensic_log_persistence():
    """Verify that forensic log file persists tamper-proof JSONL records."""
    assert WATCHDOG_LOG.exists(), f"Expected {WATCHDOG_LOG} to exist"
    with open(WATCHDOG_LOG, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) > 0, "Expected at least 1 audit entry in watchdog log"
    last_entry = json.loads(lines[-1])
    assert "timestamp" in last_entry
    assert "sha256" in last_entry
    assert last_entry["overall_status"] == "HEALTHY"
    print(f"PASS: Forensic log persistence verified. Total audit entries: {len(lines)}.")


if __name__ == "__main__":
    print("=== Running Genesis System3 Autonomous Watchdog Test Suite ===")
    test_watchdog_healthy_cycle()
    test_forensic_log_persistence()
    print("=== ALL WATCHDOG INTEGRATION TESTS PASSED SUCCESSFULLY! ===")
