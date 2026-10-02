"""Validate immutable CE/PE forward decision records.

The first supported decision is ``NO_VERIFIED_SIGNAL``.  It is a real
point-in-time research decision, not a forecast and not a trading instruction.
The contract deliberately rejects hidden recommendations, non-zero candidate
counts, stale-source promotion and claims that an inaccessible source is absent.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit


LEGACY_SCHEMA = "cepe-forward-decision-v1"
SCHEMA = "cepe-forward-decision-v2"
TASK_ID = "CEPE-NEXT-009"
LEGACY_CANONICAL_SHA256 = (
    "0f2dabcc1f60c2891c216bd1314079f0870af8c2c70f4d3a88e60b0ddc84cc54"
)
CALENDAR_URL = "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
CALENDAR_SHA256 = (
    "5a2079cd78b2e6b536ef0d28300e63b645721bed22cc82a91facf5945f3296ea"
)
CALENDAR_CIRCULAR = "NSE/FAOP/71777"
CALENDAR_PUBLISHED_DATE = "2025-12-12"
NSE_IST = timezone(timedelta(hours=5, minutes=30))
NSE_FO_2026_WEEKDAY_HOLIDAYS = {
    date(2026, 1, 26),
    date(2026, 3, 3),
    date(2026, 3, 26),
    date(2026, 3, 31),
    date(2026, 4, 3),
    date(2026, 4, 14),
    date(2026, 5, 1),
    date(2026, 5, 28),
    date(2026, 6, 26),
    date(2026, 9, 14),
    date(2026, 10, 2),
    date(2026, 10, 20),
    date(2026, 11, 10),
    date(2026, 11, 24),
    date(2026, 12, 25),
}
GITHUB_OWNER = "psw2025-cmd"
GITHUB_REPOSITORY = "Genesis_System3"
GITHUB_PR_NUMBER = 472
GITHUB_APP_SLUG = "chatgpt-codex-connector"
EXPECTED_KEYS = {
    "schema",
    "task_id",
    "evidence_class",
    "session_date",
    "following_open_at",
    "issued_at",
    "source_cutoff_at",
    "decision",
    "reason_codes",
    "source_checks",
    "candidate_count",
    "prediction_count",
    "expected_premium_move_range",
    "highest_gap_up_contract",
    "forecast_issued",
    "forward_decision_issued",
    "retrospective",
    "opening_price_is_executable_fill",
    "verified_forecast_accuracy",
    "real_money_ready",
    "live_trading_enabled",
    "orders_allowed",
}
V2_EXPECTED_KEYS = EXPECTED_KEYS | {"session_calendar_evidence"}
CALENDAR_EXPECTED_KEYS = {
    "segment",
    "source_url",
    "source_sha256",
    "source_first_observed_at",
    "source_published_date",
    "source_circular",
    "session_date",
    "session_status",
    "opening_time_basis",
}
REQUIRED_REASONS = {
    "FRESH_OFFICIAL_PREVIOUS_SESSION_FO_BYTES_NOT_OBTAINED",
    "NO_SOURCE_QUALIFIED_EXACT_CONTRACT_CANDIDATE",
    "NO_CALIBRATED_FORWARD_PROBABILITY",
}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include timezone")
    return parsed


def _day(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc


def _sha(value: Any, field: str) -> str:
    text = str(value).lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"Invalid {field}")
    return text


def _git_sha(value: Any, field: str) -> str:
    text = str(value).lower()
    if len(text) != 40 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"Invalid {field}")
    return text


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate publication receipt key: {key}")
        result[key] = value
    return result


def _json_object(raw: bytes, field: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{field} must be a JSON object")
    return parsed


def _official_url(value: Any, field: str) -> str:
    text = str(value)
    parsed = urlsplit(text)
    if (
        parsed.scheme != "https"
        or parsed.hostname
        not in {"nseindia.com", "www.nseindia.com", "nsearchives.nseindia.com"}
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise ValueError(f"Invalid {field}")
    return text


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _is_regular_fo_session(day: date) -> bool:
    return day.weekday() < 5 and day not in NSE_FO_2026_WEEKDAY_HOLIDAYS


def _next_regular_open_after(issued: datetime) -> datetime:
    issued_ist = issued.astimezone(NSE_IST)
    candidate = issued_ist.date()
    opening = datetime.combine(candidate, time(9, 15), tzinfo=NSE_IST)
    if issued_ist >= opening:
        candidate += timedelta(days=1)
    while not _is_regular_fo_session(candidate):
        candidate += timedelta(days=1)
    return datetime.combine(candidate, time(9, 15), tzinfo=NSE_IST)


def validate(
    payload: dict[str, Any], *, externally_published_at: datetime | None = None
) -> dict[str, Any]:
    """Return a compact proof summary or fail closed on any hidden claim."""
    if not isinstance(payload, dict):
        raise ValueError("Decision record fields do not match the locked schema")
    schema = payload.get("schema")
    expected_keys = (
        EXPECTED_KEYS
        if schema == LEGACY_SCHEMA
        else V2_EXPECTED_KEYS
        if schema == SCHEMA
        else None
    )
    if expected_keys is None or set(payload) != expected_keys:
        raise ValueError("Decision record fields do not match the locked schema")
    if schema == LEGACY_SCHEMA and payload["task_id"] != TASK_ID:
        raise ValueError("Unsupported decision schema or task")
    if schema == SCHEMA and not re.fullmatch(
        r"CEPE-NEXT-[0-9]{3,}", str(payload["task_id"])
    ):
        raise ValueError("Unsupported decision schema or task")
    if payload["evidence_class"] != "FORWARD_NO_SIGNAL_DECISION":
        raise ValueError("Invalid evidence class")

    session_day = _day(payload["session_date"], "session_date")
    following_open = _instant(payload["following_open_at"], "following_open_at")
    issued = _instant(payload["issued_at"], "issued_at")
    source_cutoff = _instant(payload["source_cutoff_at"], "source_cutoff_at")
    if following_open.date() != session_day:
        raise ValueError("Following opening date does not match session_date")
    if not source_cutoff <= issued < following_open:
        raise ValueError("Decision must be issued after its source cutoff and before opening")

    calendar_status = "LEGACY_EXACT_PAYLOAD"
    if schema == SCHEMA:
        calendar = payload["session_calendar_evidence"]
        if not isinstance(calendar, dict) or set(calendar) != CALENDAR_EXPECTED_KEYS:
            raise ValueError("Session-calendar evidence is incomplete")
        if calendar["segment"] != "FO":
            raise ValueError("Session calendar is not for NSE F&O")
        calendar_url = _official_url(calendar["source_url"], "calendar source URL")
        if calendar_url != CALENDAR_URL:
            raise ValueError("Session calendar is not bound to the exact official circular")
        if _sha(calendar["source_sha256"], "calendar source SHA-256") != CALENDAR_SHA256:
            raise ValueError("Session calendar source hash changed")
        if (
            calendar["source_circular"] != CALENDAR_CIRCULAR
            or calendar["source_published_date"] != CALENDAR_PUBLISHED_DATE
        ):
            raise ValueError("Session calendar circular identity changed")
        calendar_observed = _instant(
            calendar["source_first_observed_at"],
            "calendar source_first_observed_at",
        )
        calendar_published = _day(
            calendar["source_published_date"], "calendar source_published_date"
        )
        calendar_session = _day(calendar["session_date"], "calendar session_date")
        if not calendar_published <= calendar_observed.date():
            raise ValueError("Session calendar was observed before publication")
        if not calendar_observed <= source_cutoff:
            raise ValueError("Session calendar was not known by the decision cutoff")
        if calendar_session != session_day:
            raise ValueError("Session calendar date does not match the declared opening")
        if session_day.year != 2026:
            raise ValueError("Official calendar source does not cover the session year")
        if session_day.weekday() >= 5:
            raise ValueError("Declared following opening is on a weekend")
        if session_day in NSE_FO_2026_WEEKDAY_HOLIDAYS:
            raise ValueError("Declared following opening is an official NSE F&O holiday")
        if calendar["session_status"] != "SCHEDULED_REGULAR_SESSION_AS_OF_SOURCE":
            raise ValueError("Session calendar status is not fail-closed")
        if (
            calendar["opening_time_basis"]
            != "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL"
        ):
            raise ValueError("Following opening basis was overstated")
        if (
            following_open.utcoffset() != timedelta(hours=5, minutes=30)
            or following_open.hour != 9
            or following_open.minute != 15
            or following_open.second != 0
            or following_open.microsecond != 0
        ):
            raise ValueError("Following opening is not the declared regular NSE session time")
        if following_open != _next_regular_open_after(issued):
            raise ValueError("Following opening is not the next eligible NSE F&O session")
        calendar_status = "OFFICIAL_2026_FO_CALENDAR_BOUND"

    if payload["decision"] != "NO_VERIFIED_SIGNAL":
        raise ValueError("Only the fail-closed no-signal decision is supported")
    reasons = payload["reason_codes"]
    if (
        not isinstance(reasons, list)
        or len(reasons) != len(set(reasons))
        or set(reasons) != REQUIRED_REASONS
    ):
        raise ValueError("No-signal reasons are incomplete or duplicated")

    checks = payload["source_checks"]
    if not isinstance(checks, list) or len(checks) != 3:
        raise ValueError("Exactly three source roles are required")
    by_role: dict[str, dict[str, Any]] = {}
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Source check must be an object")
        role = str(check.get("source_role", ""))
        if not role or role in by_role:
            raise ValueError("Missing or duplicate source role")
        by_role[role] = check

    primary = by_role.get("PRIMARY_FO_PREVIOUS_SESSION")
    cached = by_role.get("CACHED_HISTORICAL_CHECKPOINT")
    secondary = by_role.get("SECONDARY_DISCOVERY_ONLY")
    if not all((primary, cached, secondary)):
        raise ValueError("Required source role missing")
    _official_url(primary.get("url"), "primary source URL")
    if primary.get("result") != "NOT_OBTAINED" or primary.get("interpretation") != "NOT_PROVEN":
        raise ValueError("Unobtainable primary bytes cannot be promoted to an absence claim")
    if "not evidence" not in str(primary.get("note", "")).lower():
        raise ValueError("Primary-source limitation must remain explicit")

    _sha(cached.get("archive_sha256"), "archive_sha256")
    _sha(cached.get("latest_fo_csv_sha256"), "latest_fo_csv_sha256")
    _sha(cached.get("latest_fo_zip_sha256"), "latest_fo_zip_sha256")
    if _day(cached.get("latest_fo_observation_date"), "latest_fo_observation_date") >= session_day:
        raise ValueError("Cached evidence is not stale for the stated session")
    if cached.get("result") != "HISTORICAL_ONLY_STALE_FOR_SESSION":
        raise ValueError("Cached evidence must remain historical-only")

    if secondary.get("result") != "ACCESS_DENIED_NOT_USED":
        raise ValueError("Secondary source access state changed")
    if secondary.get("interpretation") != "NOT_A_PRIMARY_CONTRACT_SOURCE":
        raise ValueError("Secondary discovery cannot qualify a contract")

    null_fields = (
        "expected_premium_move_range",
        "highest_gap_up_contract",
        "verified_forecast_accuracy",
    )
    if any(payload[field] is not None for field in null_fields):
        raise ValueError("No-signal decision cannot contain forecast or performance values")
    if payload["candidate_count"] != 0 or payload["prediction_count"] != 0:
        raise ValueError("No-signal decision must have zero candidates and predictions")
    if payload["forecast_issued"] is not False or payload["forward_decision_issued"] is not True:
        raise ValueError("Decision/forecast state is inconsistent")
    for field in (
        "retrospective",
        "opening_price_is_executable_fill",
        "real_money_ready",
        "live_trading_enabled",
        "orders_allowed",
    ):
        if payload[field] is not False:
            raise ValueError(f"Unsafe or dishonest flag: {field}")

    if (
        schema == LEGACY_SCHEMA
        and sha256(_canonical(payload)).hexdigest() != LEGACY_CANONICAL_SHA256
    ):
        raise ValueError("Legacy v1 is restricted to the exact sealed historical payload")

    published_before_open = None
    if externally_published_at is not None:
        if externally_published_at.tzinfo is None or externally_published_at.utcoffset() is None:
            raise ValueError("externally_published_at must include timezone")
        if not issued <= externally_published_at < following_open:
            raise ValueError("External publication did not occur between issue and opening")
        published_before_open = True

    return {
        "task_id": payload["task_id"],
        "status": (
            "FORWARD_NO_SIGNAL_SEALED"
            if schema == LEGACY_SCHEMA
            else "FORWARD_NO_SIGNAL_CALENDAR_SEALED"
        ),
        "session_date": session_day.isoformat(),
        "session_calendar_status": calendar_status,
        "decision_record_sha256": sha256(_canonical(payload)).hexdigest(),
        "candidate_count": 0,
        "prediction_count": 0,
        "published_before_open": published_before_open,
        "real_money_ready": False,
        "orders_allowed": False,
    }


def validate_github_publication(
    payload: dict[str, Any],
    *,
    decision_bytes: bytes,
    publication_receipt_bytes: bytes,
    expected_commit_sha: str,
) -> dict[str, Any]:
    """Bind a decision to an unedited GitHub API comment receipt.

    The receipt is stored as the exact API response bytes.  This validates its
    repository/PR identity, GitHub server timestamp window, author/app identity,
    and body bindings to the exact decision bytes and original decision commit.
    It does not turn a no-signal decision into a forecast or performance claim.
    """
    summary = validate(payload)
    stored_decision = _json_object(decision_bytes, "decision bytes")
    if stored_decision != payload:
        raise ValueError("Decision bytes do not match the validated payload")

    decision_sha = sha256(decision_bytes).hexdigest()
    commit_sha = _git_sha(expected_commit_sha, "expected_commit_sha")
    receipt = _json_object(publication_receipt_bytes, "publication receipt")

    comment_id = receipt.get("id")
    if type(comment_id) is not int or comment_id <= 0:
        raise ValueError("Invalid publication comment id")
    api_base = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPOSITORY}"
    )
    expected_locations = {
        "url": f"{api_base}/issues/comments/{comment_id}",
        "issue_url": f"{api_base}/issues/{GITHUB_PR_NUMBER}",
        "html_url": (
            f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/pull/"
            f"{GITHUB_PR_NUMBER}#issuecomment-{comment_id}"
        ),
    }
    if any(receipt.get(key) != value for key, value in expected_locations.items()):
        raise ValueError("Publication receipt does not identify the locked PR comment")

    user = receipt.get("user")
    app = receipt.get("performed_via_github_app")
    if not isinstance(user, dict) or user.get("login") != GITHUB_OWNER:
        raise ValueError("Publication receipt owner does not match")
    if receipt.get("author_association") != "OWNER":
        raise ValueError("Publication receipt is not owner-authored")
    if not isinstance(app, dict) or app.get("slug") != GITHUB_APP_SLUG:
        raise ValueError("Publication receipt app does not match")

    created = _instant(receipt.get("created_at"), "publication created_at")
    updated = _instant(receipt.get("updated_at"), "publication updated_at")
    if updated != created:
        raise ValueError("Publication receipt was modified after creation")
    issued = _instant(payload["issued_at"], "issued_at")
    following_open = _instant(payload["following_open_at"], "following_open_at")
    if not issued <= created < following_open:
        raise ValueError("GitHub publication did not occur between issue and opening")

    body = receipt.get("body")
    required_bindings = (
        f"`{commit_sha}`",
        f"`{decision_sha}`",
        "qualified candidates **0**; forecasts **0**; outcomes **0**",
        "Decision: **NO VERIFIED SIGNAL**",
    )
    if not isinstance(body, str) or any(item not in body for item in required_bindings):
        raise ValueError("Publication receipt body does not bind the decision proof")

    summary.update(
        {
            "published_before_open": True,
            "publication_status": "GITHUB_SERVER_TIMESTAMP_RECEIPT_VERIFIED",
            "publication_comment_id": comment_id,
            "published_at": created.isoformat(),
            "publication_receipt_sha256": sha256(
                publication_receipt_bytes
            ).hexdigest(),
            "decision_file_sha256": decision_sha,
            "publication_commit_sha": commit_sha,
        }
    )
    return summary
