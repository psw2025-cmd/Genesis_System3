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
AS_SENT_TARGET_OPEN_AT = "2026-10-02T09:15:00+05:30"
CORRECTED_TARGET_OPEN_AT = "2026-10-05T09:15:00+05:30"
CALENDAR_URL = "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
CALENDAR_SHA256 = "5a2079cd78b2e6b536ef0d28300e63b645721bed22cc82a91facf5945f3296ea"
EXPECTED_KEYS = {
    "schema",
    "task_id",
    "lane",
    "report_date_ist",
    "target_open_at",
    "target_session_correction",
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
    if payload["target_open_at"] != AS_SENT_TARGET_OPEN_AT:
        raise ValueError("Historical receipt must preserve the as-sent target opening")

    correction = payload["target_session_correction"]
    expected_correction_fields = {
        "identified_at",
        "as_sent_target_open_at",
        "as_sent_target_date_valid",
        "corrected_next_eligible_open_at",
        "calendar_source_url",
        "calendar_source_sha256",
        "calendar_source_first_observed_at",
        "calendar_source_circular",
        "calendar_source_published_date",
        "official_holiday_date",
        "official_holiday_reason",
        "weekend_dates",
        "opening_time_basis",
        "email_content_mutable",
        "correction_email_sent",
        "duplicate_guard_preserved",
    }
    if not isinstance(correction, dict) or set(correction) != expected_correction_fields:
        raise ValueError("Target-session correction is incomplete")
    identified_at = _instant(correction["identified_at"], "correction identified_at")
    corrected_open = _instant(
        correction["corrected_next_eligible_open_at"], "corrected next eligible open"
    )
    calendar_observed = _instant(
        correction["calendar_source_first_observed_at"], "calendar source first observed"
    )
    if correction["as_sent_target_open_at"] != payload["target_open_at"]:
        raise ValueError("Correction is not bound to the as-sent target opening")
    if correction["as_sent_target_date_valid"] is not False:
        raise ValueError("Invalid holiday target was not marked false")
    if correction["corrected_next_eligible_open_at"] != CORRECTED_TARGET_OPEN_AT:
        raise ValueError("Corrected target is not the next eligible NSE F&O session")
    if not calendar_observed < decision_at <= sent_at < identified_at < corrected_open:
        raise ValueError("Calendar correction chronology is invalid")
    calendar_url = str(correction["calendar_source_url"])
    calendar_source = urlsplit(calendar_url)
    if (
        calendar_url != CALENDAR_URL
        or calendar_source.scheme != "https"
        or calendar_source.hostname != "nsearchives.nseindia.com"
        or calendar_source.username
        or calendar_source.password
        or calendar_source.fragment
        or calendar_source.port not in (None, 443)
    ):
        raise ValueError("Calendar correction is not bound to the exact official NSE circular")
    if _sha256(correction["calendar_source_sha256"], "calendar source SHA-256") != CALENDAR_SHA256:
        raise ValueError("Calendar correction source hash changed")
    if (
        correction["calendar_source_circular"] != "NSE/FAOP/71777"
        or correction["calendar_source_published_date"] != "2025-12-12"
    ):
        raise ValueError("Calendar correction circular identity changed")
    if (
        correction["official_holiday_date"] != "2026-10-02"
        or correction["official_holiday_reason"] != "Mahatma Gandhi Jayanti"
    ):
        raise ValueError("Calendar correction holiday evidence changed")
    if correction["weekend_dates"] != ["2026-10-03", "2026-10-04"]:
        raise ValueError("Calendar correction weekend gap changed")
    if correction["opening_time_basis"] != "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL":
        raise ValueError("Corrected opening basis was overstated")
    if correction["email_content_mutable"] is not False:
        raise ValueError("Historical email content cannot be rewritten")
    if correction["correction_email_sent"] is not False:
        raise ValueError("Calendar correction cannot authorize a duplicate email")
    if correction["duplicate_guard_preserved"] is not True:
        raise ValueError("Exactly-once guard was not preserved by the correction")

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
        "status": "NO_SIGNAL_EMAIL_DELIVERED_EXACTLY_ONCE_CALENDAR_CORRECTED",
        "report_date_ist": report_day.isoformat(),
        "as_sent_target_open_at": target_open.isoformat(),
        "corrected_target_open_at": corrected_open.isoformat(),
        "gmail_message_id": delivery["gmail_message_id"],
        "receipt_sha256": sha256(_canonical(payload)).hexdigest(),
        "qualified_candidates": 0,
        "issued_contract_forecasts": 0,
        "orders_allowed": False,
    }
