"""Focused calendar guards for new CE/PE forward decisions.

These are contract fixtures only.  They are not market observations, forecasts,
or performance evidence.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.cepe_forward_decision import validate


DECISION_PATH = Path(
    "research/forward/cepe/2026-09-30_no_verified_signal.json"
)


class ForwardSessionCalendarTests(unittest.TestCase):
    def legacy(self):
        return json.loads(DECISION_PATH.read_text())

    def v2(self):
        record = deepcopy(self.legacy())
        record.update(
            {
                "schema": "cepe-forward-decision-v2",
                "task_id": "CEPE-NEXT-019",
                "session_date": "2026-10-05",
                "following_open_at": "2026-10-05T09:15:00+05:30",
                "issued_at": "2026-10-01T20:30:00+05:30",
                "source_cutoff_at": "2026-10-01T20:30:00+05:30",
            }
        )
        record["source_checks"][0]["url"] = (
            "https://nsearchives.nseindia.com/content/fo/"
            "BhavCopy_NSE_FO_0_0_0_20261001_F_0000.csv.zip"
        )
        record["source_checks"][1]["latest_fo_observation_date"] = "2026-10-01"
        record["session_calendar_evidence"] = {
            "segment": "FO",
            "source_url": (
                "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
            ),
            "source_sha256": (
                "5a2079cd78b2e6b536ef0d28300e63b645721bed22cc82a91facf5945f3296ea"
            ),
            "source_first_observed_at": "2026-09-27T15:47:09Z",
            "source_published_date": "2025-12-12",
            "source_circular": "NSE/FAOP/71777",
            "session_date": "2026-10-05",
            "session_status": "SCHEDULED_REGULAR_SESSION_AS_OF_SOURCE",
            "opening_time_basis": (
                "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL"
            ),
        }
        return record

    def set_session(self, record, day):
        record["session_date"] = day
        record["following_open_at"] = f"{day}T09:15:00+05:30"
        record["session_calendar_evidence"]["session_date"] = day

    def test_exact_historical_v1_remains_valid_and_immutable(self):
        result = validate(self.legacy())
        self.assertEqual(result["status"], "FORWARD_NO_SIGNAL_SEALED")
        self.assertEqual(result["session_calendar_status"], "LEGACY_EXACT_PAYLOAD")

        changed = self.legacy()
        changed["source_checks"][0]["note"] += " "
        with self.assertRaisesRegex(ValueError, "exact sealed historical payload"):
            validate(changed)

    def test_v2_binds_official_calendar_before_decision_cutoff(self):
        result = validate(self.v2())
        self.assertEqual(result["status"], "FORWARD_NO_SIGNAL_CALENDAR_SEALED")
        self.assertEqual(
            result["session_calendar_status"],
            "OFFICIAL_2026_FO_CALENDAR_BOUND",
        )
        self.assertFalse(result["orders_allowed"])

    def test_v2_rejects_official_holiday_and_weekend_targets(self):
        holiday = self.v2()
        self.set_session(holiday, "2026-10-02")
        with self.assertRaisesRegex(ValueError, "official NSE F&O holiday"):
            validate(holiday)

        weekend = self.v2()
        self.set_session(weekend, "2026-10-03")
        with self.assertRaisesRegex(ValueError, "weekend"):
            validate(weekend)

        skipped = self.v2()
        self.set_session(skipped, "2026-10-06")
        with self.assertRaisesRegex(ValueError, "next eligible NSE F&O session"):
            validate(skipped)

    def test_v2_rejects_substituted_or_late_calendar_evidence(self):
        wrong_hash = self.v2()
        wrong_hash["session_calendar_evidence"]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash changed"):
            validate(wrong_hash)

        late = self.v2()
        late["session_calendar_evidence"]["source_first_observed_at"] = (
            "2026-10-01T20:31:00+05:30"
        )
        with self.assertRaisesRegex(ValueError, "not known by the decision cutoff"):
            validate(late)

    def test_v2_rejects_mismatched_date_and_overstated_opening(self):
        mismatch = self.v2()
        mismatch["session_calendar_evidence"]["session_date"] = "2026-10-06"
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate(mismatch)

        fill_claim = self.v2()
        fill_claim["session_calendar_evidence"]["opening_time_basis"] = (
            "EXECUTABLE_OPENING_FILL"
        )
        with self.assertRaisesRegex(ValueError, "overstated"):
            validate(fill_claim)

        wrong_time = self.v2()
        wrong_time["following_open_at"] = "2026-10-05T09:16:00+05:30"
        with self.assertRaisesRegex(ValueError, "regular NSE session time"):
            validate(wrong_time)

    def test_v2_rejects_incomplete_calendar_evidence(self):
        record = self.v2()
        record["session_calendar_evidence"].pop("source_sha256")
        with self.assertRaisesRegex(ValueError, "evidence is incomplete"):
            validate(record)


if __name__ == "__main__":
    unittest.main()
