from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.cepe_delivery_source import validate


ROOT = Path(__file__).parents[1]
RECORD = ROOT / "research/evidence/cepe/2026-10-07_cepe_delivery_source.json"
RAW = ROOT / "research/evidence/cepe/raw/fo_20261007.zip"


def _payload():
    return json.loads(RECORD.read_text(encoding="utf-8"))


class DeliverySourceTests(unittest.TestCase):
    def test_committed_receipt_replays_exact_retained_source(self):
        result = validate(_payload(), repo_root=ROOT)
        self.assertEqual(
            result["status"], "OFFICIAL_PRE_DELIVERY_SOURCE_RETAINED_AND_REPLAYED"
        )
        self.assertEqual(result["source_rows"], 35206)
        self.assertEqual(result["option_rows"], 34553)
        self.assertEqual(result["mechanically_screened_observations"], 5122)
        self.assertEqual(result["qualified_candidates"], 0)
        self.assertEqual(result["issued_contract_forecasts"], 0)
        self.assertEqual(result["matured_forward_outcomes"], 0)
        self.assertEqual(result["target_open_at"], "2026-10-08T09:15:00+05:30")
        self.assertEqual(
            result["zip_sha256"],
            "676932c7a62c953cd1a82c277a4bb040ace5cd593c661dac4b9030a49c1801df",
        )
        self.assertFalse(result["second_email_allowed"])
        self.assertFalse(result["orders_allowed"])

    def test_rejects_chronology_provenance_forecast_and_safety_mutations(self):
        cases = [
            (("target_open_at",), "2026-10-09T09:15:00+05:30", "Source or target session"),
            (("target_session", "calendar_source_url"), "https://example.com/calendar.pdf", "exact official NSE circular"),
            (("target_session", "intervening_official_holidays"), ["2026-10-08"], "chronology or basis"),
            (("delivery_lock", "sent_history_count_exact"), 2, "Exactly-once delivery lock"),
            (("delivery_lock", "source_observed_before_send"), False, "Exactly-once delivery lock"),
            (("delivery_lock", "second_email_allowed"), True, "Exactly-once delivery lock"),
            (("retrievals", 0, "observed_at"), "2026-10-07T20:08:00+05:30", "Source/delivery/repeat chronology"),
            (("retrievals", 2, "response_sha256"), "0" * 64, "Retrieval identity or byte proof"),
            (("official_archive", "url"), "https://nsearchives.nseindia.com/content/fo/wrong.zip", "exact official NSE source"),
            (("official_archive", "exchange_publication_time"), "2026-10-07T18:34:02+05:30", "cannot invent"),
            (("official_archive", "header_time_is_exchange_dissemination_time"), True, "promoted to dissemination"),
            (("official_archive", "member"), "wrong.csv", "Archive measurement changed"),
            (("official_archive", "source_rows"), 35207, "Archive measurement changed"),
            (("mechanical_universe", "option_rows"), 34554, "Mechanical universe measurement"),
            (("mechanical_universe", "screen_is_prediction"), True, "promoted to a forecast"),
            (("feature_registry", 11, "missing_count"), 0, "silently imputed"),
            (("feature_registry", 0, "version"), "cepe-delivery-source-v2", "Feature version changed"),
            (("forward_state", "issued_contract_forecasts"), 1, "fabricate a forward forecast"),
            (("forward_state", "expected_premium_move_range"), [1.0, 3.0], "premium range"),
            (("forward_state", "source_backfilled_into_prior_decision"), True, "backfilled or promoted"),
            (("gate_status", "minimum_oos_days"), 1, "Project gate thresholds"),
            (("gate_status", "frozen_q2_baseline", "directional_accuracy"), 0.9, "baseline or numerical gap"),
            (("gate_status", "strategy_promoted"), True, "promoted or retuned"),
            (("interpretation",), "FORECAST_ISSUED", "interpretation changed"),
            (("orders_allowed",), True, "Unsafe or dishonest"),
        ]
        for path, value, message in cases:
            with self.subTest(path=path):
                payload = deepcopy(_payload())
                target = payload
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate(payload, repo_root=ROOT)

    def test_rejects_replaced_retained_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "research/evidence/cepe/raw/fo_20261007.zip"
            target.parent.mkdir(parents=True)
            shutil.copyfile(RAW, target)
            validate(_payload(), repo_root=root)

            raw = bytearray(target.read_bytes())
            raw[0] ^= 1
            target.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "Retained ZIP SHA-256 changed"):
                validate(_payload(), repo_root=root)

    def test_rejects_unsafe_raw_path_and_undeclared_fields(self):
        unsafe = _payload()
        unsafe["official_archive"]["raw_zip_path"] = "../fo_20261007.zip"
        with self.assertRaisesRegex(ValueError, "locked safe repository path"):
            validate(unsafe, repo_root=ROOT)

        extra = _payload()
        extra["future_result"] = {"multiple": 30}
        with self.assertRaisesRegex(ValueError, "locked schema"):
            validate(extra, repo_root=ROOT)


if __name__ == "__main__":
    unittest.main()
