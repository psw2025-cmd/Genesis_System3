"""Fail-closed validation for exactly-once CE/PE email delivery receipts."""
from __future__ import annotations

from datetime import date, datetime
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit


SCHEMA = "cepe-email-delivery-v1"
TASK_ID = "CEPE-DELIVERY-014"
EXPECTED_RECIPIENT = "warghade2012@gmail.com"
EXPECTED_KEYS = {
    "schema",
    "task_id",
    "lane",
    "report_date_ist",
    "target_open_at",
    "decision_issued_at",
    "decision",
    "reason_codes",
    "source_check",
    "strategy",
    "counts",
    "expected_premium_move_range",
    "uncertainty",
    "previous_issued_forecasts_vs_next_open_actuals",
    "duplicate_guard",
    "recipient",
    "delivery",
    "opening_price_is_executable_fill",
    "fees_slippage_proven",
    "real_money_ready",
    "live_trading_enabled",
    "orders_allowed",
}
REQUIRED_REASONS = {
    "FRESH_OFFICIAL_SESSION_FO_BYTES_NOT_OBTAINED",
    "NO_SOURCE_QUALIFIED_EXACT_CONTRACT_CANDIDATE",
    "NO_STRATEGY_PASSED_FORWARD_GATES",
}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include timezone")
    return parsed


def _sha256(value: Any, field: str) -> str:
    text = str(value).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ValueError(f"Invalid {field}")
    return text


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate one delivery receipt and return its immutable summary."""
    if not isinstance(payload, dict) or set(payload) != EXPECTED_KEYS:
        raise ValueError("Delivery fields do not match the locked schema")
    if payload["schema"] != SCHEMA or payload["task_id"] != TASK_ID:
        raise ValueError("Unsupported delivery schema or task")
    if payload["lane"] != "CEPE_NEXT_OPEN":
        raise ValueError("CE/PE delivery cannot be mixed with another lane")

    try:
        report_day = date.fromisoformat(str(payload["report_date_ist"]))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid report_date_ist") from exc
    decision_at = _instant(payload["decision_issued_at"], "decision_issued_at")
    target_open = _instant(payload["target_open_at"], "target_open_at")
    source = payload["source_check"]
    delivery = payload["delivery"]
    if not isinstance(source, dict) or not isinstance(delivery, dict):
        raise ValueError("Source check and delivery must be objects")
    observed_at = _instant(source.get("observed_at"), "source observed_at")
    sent_at = _instant(delivery.get("sent_at"), "delivery sent_at")
    if decision_at.date() != report_day or observed_at != decision_at:
        raise ValueError("Report date/source cutoff does not match decision time")
    if not observed_at <= sent_at < target_open:
        raise ValueError("Delivery must follow its source check and precede target open")

    if payload["decision"] != "NO_VERIFIED_SIGNAL":
        raise ValueError("Only a fail-closed no-signal delivery is supported")
    reasons = payload["reason_codes"]
    if not isinstance(reasons, list) or set(reasons) != REQUIRED_REASONS:
        raise ValueError("No-signal reason set is incomplete")
    if len(reasons) != len(REQUIRED_REASONS):
        raise ValueError("No-signal reasons are duplicated")

    parsed_url = urlsplit(str(source.get("url", "")))
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "nsearchives.nseindia.com"
        or parsed_url.username
        or parsed_url.password
        or parsed_url.fragment
        or parsed_url.port not in (None, 443)
    ):
        raise ValueError("Source is not the official NSE archive host")
    _sha256(source.get("response_sha256"), "response_sha256")
    if source.get("source_role") != "PRIMARY_FO_SESSION_CLOSE":
        raise ValueError("Invalid source role")
    if source.get("result") != "NOT_OBTAINED" or source.get("absence_proven") is not False:
        raise ValueError("A failed retrieval cannot prove source or contract absence")
    if source.get("http_status") != 404 or source.get("response_bytes") != 3425:
        raise ValueError("Source receipt does not match the observed response")

    strategy = payload["strategy"]
    if not isinstance(strategy, dict):
        raise ValueError("Strategy must be an object")
    if strategy.get("id") != "CEPE-NEXT-008" or strategy.get("version") != "forward-only-v1":
        raise ValueError("Unexpected strategy/version")
    if strategy.get("qualification_gate_passed") is not False:
        raise ValueError("An unqualified strategy cannot be promoted")
    if strategy.get("retuned_after_frozen_test") is not False:
        raise ValueError("Frozen test must not be retuned")
    if strategy.get("evaluated_outcome_days") != 59 or strategy.get("target_outcome_days") != 60:
        raise ValueError("Outcome-day gate changed")

    counts = payload["counts"]
    if not isinstance(counts, dict) or any(value != 0 for value in counts.values()):
        raise ValueError("No-signal delivery must contain zero forecast counts")
    if payload["expected_premium_move_range"] is not None:
        raise ValueError("No-signal delivery cannot contain a premium forecast")
    if payload["uncertainty"] != "NOT_PROVEN":
        raise ValueError("Uncertainty must remain NOT_PROVEN")

    prior = payload["previous_issued_forecasts_vs_next_open_actuals"]
    if (
        not isinstance(prior, dict)
        or prior.get("issued_contract_forecasts") != 0
        or prior.get("scored_next_open_outcomes") != 0
        or prior.get("abstention_counted_as_hit") is not False
    ):
        raise ValueError("Prior abstention cannot be scored as a forecast hit")

    guard = payload["duplicate_guard"]
    if (
        not isinstance(guard, dict)
        or guard.get("gmail_sent_matches_before") != 0
        or guard.get("durable_record_matches_before") != 0
        or guard.get("gmail_sent_matches_after") != 1
    ):
        raise ValueError("Exactly-once duplicate guard failed")
    recipient = payload["recipient"]
    if (
        not isinstance(recipient, dict)
        or recipient.get("address") != EXPECTED_RECIPIENT
        or recipient.get("authenticated_profile_address") != EXPECTED_RECIPIENT
        or recipient.get("verified_own_address") is not True
    ):
        raise ValueError("Recipient is not the verified own address")
    if not re.fullmatch(r"[0-9a-f]{16}", str(delivery.get("gmail_message_id", ""))):
        raise ValueError("Invalid Gmail message ID")
    if delivery.get("gmail_thread_id") != delivery.get("gmail_message_id"):
        raise ValueError("Unexpected Gmail thread binding")
    if delivery.get("sent_label_confirmed") is not True:
        raise ValueError("Gmail Sent confirmation is missing")

    for field in (
        "opening_price_is_executable_fill",
        "fees_slippage_proven",
        "real_money_ready",
        "live_trading_enabled",
        "orders_allowed",
    ):
        if payload[field] is not False:
            raise ValueError(f"Unsafe or dishonest flag: {field}")

    return {
        "task_id": TASK_ID,
        "status": "NO_SIGNAL_EMAIL_DELIVERED_EXACTLY_ONCE",
        "report_date_ist": report_day.isoformat(),
        "gmail_message_id": delivery["gmail_message_id"],
        "receipt_sha256": sha256(_canonical(payload)).hexdigest(),
        "qualified_candidates": 0,
        "issued_contract_forecasts": 0,
        "orders_allowed": False,
    }
