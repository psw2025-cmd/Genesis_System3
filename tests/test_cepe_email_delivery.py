from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.cepe_email_delivery import validate


RECORD = (
    Path(__file__).parents[1]
    / "research/evidence/cepe/2026-10-01_no_signal_email_delivery.json"
)


def _payload():
    return json.loads(RECORD.read_text(encoding="utf-8"))


class DeliveryReceiptTests(unittest.TestCase):
    def test_committed_delivery_receipt_is_exactly_once_and_fail_closed(self):
        summary = validate(_payload())
        self.assertEqual(summary["status"], "NO_SIGNAL_EMAIL_DELIVERED_EXACTLY_ONCE")
        self.assertEqual(summary["gmail_message_id"], "1a0f7ae95163cc3e")
        self.assertEqual(summary["qualified_candidates"], 0)
        self.assertEqual(summary["issued_contract_forecasts"], 0)
        self.assertFalse(summary["orders_allowed"])

    def test_receipt_rejects_duplicate_hindsight_and_unsafe_mutations(self):
        cases = [
        (("duplicate_guard", "gmail_sent_matches_before"), 1, "duplicate guard"),
        (("source_check", "absence_proven"), True, "cannot prove"),
        (("counts", "qualified_candidates"), 1, "zero forecast counts"),
        (("expected_premium_move_range",), [1.0, 3.0], "premium forecast"),
        (("previous_issued_forecasts_vs_next_open_actuals", "abstention_counted_as_hit"), True, "forecast hit"),
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
                    validate(payload)


if __name__ == "__main__":
    unittest.main()
