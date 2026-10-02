"""Focused authenticated-calendar checks for CE/PE calibration rows.

All rows here are contract fixtures, not forecasts or market-performance proof.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest

from scripts.cepe_forward_calibration import report
from scripts.cepe_forward_decision import CALENDAR_SHA256


IST = timezone(timedelta(hours=5, minutes=30))
AS_OF = datetime(2026, 10, 1, 12, tzinfo=IST)


def row():
    return {
        "prediction_id": "fixture-p1",
        "strategy_id": "fixture-directional-regime",
        "strategy_version": "fixture-v1",
        "event_type": "positive_next_open",
        "probability": 0.8,
        "symbol": "ABC",
        "expiry": "2026-10-29",
        "strike": 100,
        "type": "CE",
        "previous_day": "2026-09-29",
        "following_day": "2026-09-30",
        "issued_at": "2026-09-29T16:00:00+05:30",
        "published_at": "2026-09-29T16:01:00+05:30",
        "cutoff_at": "2026-09-29T18:00:00+05:30",
        "following_open_at": "2026-09-30T09:15:00+05:30",
        "prediction_source_sha256": "a" * 64,
        "publication_receipt_sha256": "c" * 64,
        "session_calendar_sha256": CALENDAR_SHA256,
        "session_calendar_evidence": {
            "segment": "FO",
            "source_url": (
                "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
            ),
            "source_sha256": CALENDAR_SHA256,
            "source_first_observed_at": "2026-09-27T15:47:09Z",
            "source_published_date": "2025-12-12",
            "source_circular": "NSE/FAOP/71777",
            "session_date": "2026-09-30",
            "session_status": "SCHEDULED_REGULAR_SESSION_AS_OF_SOURCE",
            "opening_time_basis": (
                "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL"
            ),
        },
        "outcome_multiple": 1.2,
        "outcome_observed_at": "2026-09-30T09:16:00+05:30",
        "outcome_source_sha256": "b" * 64,
        "forward_issued": True,
        "retrospective": False,
        "source_qualified": True,
        "official_session_verified": True,
        "publication_verified": True,
        "opening_fill_proven": False,
        "orders_allowed": False,
    }


class CalibrationCalendarBindingTests(unittest.TestCase):
    def test_authenticated_fixture_is_accepted_without_readiness_claim(self):
        result = report([row()], as_of=AS_OF)
        self.assertEqual(result["version"], "forward-calibration-v3")
        self.assertEqual(result["matured_outcomes"], 1)
        self.assertFalse(result["real_money_ready"])
        self.assertFalse(result["orders_allowed"])

    def test_boolean_cannot_hide_substituted_calendar_hash(self):
        candidate = row()
        candidate["session_calendar_sha256"] = "d" * 64
        candidate["session_calendar_evidence"]["source_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "source hash changed"):
            report([candidate], as_of=AS_OF)

    def test_calendar_must_be_observed_before_forecast_issue(self):
        candidate = row()
        candidate["session_calendar_evidence"]["source_first_observed_at"] = (
            "2026-09-29T16:00:01+05:30"
        )
        with self.assertRaisesRegex(ValueError, "not known by the decision cutoff"):
            report([candidate], as_of=AS_OF)

    def test_following_day_must_match_exact_next_session_open(self):
        mismatched = row()
        mismatched["following_day"] = "2026-10-01"
        with self.assertRaisesRegex(ValueError, "does not match following_day"):
            report([mismatched], as_of=AS_OF)

        skipped = deepcopy(row())
        skipped["following_day"] = "2026-10-01"
        skipped["following_open_at"] = "2026-10-01T09:15:00+05:30"
        skipped["session_calendar_evidence"]["session_date"] = "2026-10-01"
        skipped["outcome_observed_at"] = "2026-10-01T09:16:00+05:30"
        with self.assertRaisesRegex(ValueError, "next eligible NSE F&O session"):
            report([skipped], as_of=AS_OF)

    def test_forecast_must_be_issued_after_previous_close(self):
        candidate = row()
        candidate["issued_at"] = "2026-09-29T15:29:00+05:30"
        with self.assertRaisesRegex(ValueError, "after the stated previous-session close"):
            report([candidate], as_of=AS_OF)

    def test_schema_rejects_hidden_trade_fields_and_missing_provenance(self):
        hidden = row()
        hidden["trade_action"] = "BUY"
        hidden["recommended_quantity"] = 50
        with self.assertRaisesRegex(ValueError, "schema mismatch.*unknown"):
            report([hidden], as_of=AS_OF)

        missing = row()
        del missing["publication_receipt_sha256"]
        with self.assertRaisesRegex(ValueError, "schema mismatch.*missing"):
            report([missing], as_of=AS_OF)

    def test_previous_day_must_be_an_actual_immediately_preceding_session(self):
        weekend = row()
        weekend.update(
            previous_day="2026-09-27",
            following_day="2026-09-28",
            issued_at="2026-09-27T22:00:00+05:30",
            published_at="2026-09-27T22:01:00+05:30",
            cutoff_at="2026-09-27T23:00:00+05:30",
            following_open_at="2026-09-28T09:15:00+05:30",
            outcome_observed_at="2026-09-28T09:16:00+05:30",
        )
        weekend["session_calendar_evidence"]["session_date"] = "2026-09-28"
        with self.assertRaisesRegex(ValueError, "immediately preceding eligible"):
            report([weekend], as_of=AS_OF)


if __name__ == "__main__":
    unittest.main()
