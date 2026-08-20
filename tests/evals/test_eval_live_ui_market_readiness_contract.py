from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_frontend_market_hours_is_timezone_safe():
    text = _text("dashboard/frontend/src/utils/marketHours.ts")
    assert "Asia/Kolkata" in text
    assert "Intl.DateTimeFormat" in text
    assert "timeZone: IST_ZONE" in text
    assert "getTimezoneOffset" not in text
    assert "isMarketOpen(now: Date = new Date())" in text


def test_store_does_not_coerce_partial_health_to_market_closed():
    text = _text("dashboard/frontend/src/store.ts")
    assert "marketOpen: isMarketOpen()" in text
    assert "marketOpenFromHealth" in text
    assert "return previous" in text
    assert "Boolean(health?.market?.is_open ?? health?.market_status === 'open')" not in text


def test_backend_ist_market_truth_for_same_utc_instant():
    import sys

    src = str(ROOT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from utils.market_hours import is_market_open

    # 2026-08-20 06:13 UTC == 11:43 IST, Thursday: market must be open.
    open_now, reason = is_market_open(datetime(2026, 8, 20, 6, 13, tzinfo=timezone.utc))
    assert open_now is True, reason

    # 2026-08-20 03:00 UTC == 08:30 IST: before market.
    open_now, _ = is_market_open(datetime(2026, 8, 20, 3, 0, tzinfo=timezone.utc))
    assert open_now is False


def test_semantic_proof_is_not_route_only():
    text = _text("scripts/gcp_live_ui_semantic_proof.py")
    for symbol in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
        assert symbol in text
    for marker in (
        "MARKET CLOSED",
        "AFTER HOURS",
        "WAITING · BROKER",
        "WAITING · 4 CHAINS",
        "WAITING FOR MARKET DATA",
        "NO CONTRACTS RETURNED BY BACKEND",
        "LOADING SIGNALS",
        "LOADING MARKET TOP",
        "TOKEN_EXPIRED_OR_INVALID",
    ):
        assert marker in text
    assert "/api/deploy/info" in text
    assert "/api/broker/status" in text
    assert "live-ui/semantic-proof" in text


def test_post_deploy_workflow_targets_exact_deployed_sha():
    text = _text(".github/workflows/gcp-live-ui-semantic-proof.yml")
    assert 'workflows: ["Cloud Run Auto Deploy"]' in text
    assert "github.event.workflow_run.head_sha" in text
    assert "Checkout exact deployed SHA" in text
    assert "python scripts/gcp_live_ui_semantic_proof.py" in text
