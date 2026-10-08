from datetime import date
import json
from pathlib import Path
import unittest

from scripts.cepe_regularized_regime_candidate import (
    FEATURE_ORDER,
    HEADS,
    SELECTION_COUNT,
    _percentile_ranks,
    rank,
)


HEADER = (
    "TradDt,TckrSymb,XpryDt,StrkPric,OptnTp,OpnPric,HghPric,LwPric,ClsPric,"
    "PrvsClsgPric,UndrlygPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,"
    "TtlNbOfTxsExctd,NewBrdLotQty\n"
)


def snapshot(day: str, *, close_shift: float = 0, duplicate: bool = False) -> bytes:
    rows = []
    for index in range(30):
        close = 12 + index / 5 + close_shift
        row = (
            f"{day},A{index:02d},2026-06-25,{80 + index},"
            f"{'CE' if index % 2 == 0 else 'PE'},10,25,5,{close},"
            f"{11 + index / 10},{100 + index / 2},2000,{index - 10},"
            f"{2000 + index * 20},{200000 + index * 10},{100 + index},50\n"
        )
        rows.append(row)
    if duplicate:
        rows.append(rows[0])
    return (HEADER + "".join(rows)).encode()


class RegularizedRegimeCandidateTest(unittest.TestCase):
    def test_frozen_registry_and_code_coefficients_match_exactly(self):
        registry = json.loads(
            Path("research/experiments/cepe_regularized_regime_v3.json").read_text()
        )
        self.assertEqual(tuple(registry["feature_order"]), FEATURE_ORDER)
        self.assertEqual(registry["selection_count_per_session"], SELECTION_COUNT)
        self.assertEqual(registry["frozen_heads"], HEADS)

    def test_percentile_ties_are_average_ranked(self):
        self.assertEqual(_percentile_ranks([1, 1, 3, 2]), [0.375, 0.375, 1.0, 0.75])

    def test_rank_is_prior_only_and_returns_separate_fixed_heads(self):
        result = rank(
            snapshot("2026-03-27"),
            snapshot("2026-03-30", close_shift=1),
            date(2026, 3, 27),
            date(2026, 3, 30),
            date(2026, 3, 31),
        )
        self.assertEqual(len(result["eligible"]), 30)
        self.assertEqual(set(result["selected"]), {"directional", "rare_tail"})
        self.assertTrue(all(len(values) == 10 for values in result["selected"].values()))
        self.assertIsNone(result["expected_range"])
        self.assertFalse(result["forward_issued"])
        self.assertFalse(result["orders_allowed"])

    def test_current_snapshot_changes_ranking_but_no_future_snapshot_is_accepted(self):
        base = rank(
            snapshot("2026-03-27"),
            snapshot("2026-03-30"),
            date(2026, 3, 27),
            date(2026, 3, 30),
            date(2026, 3, 31),
        )
        changed = rank(
            snapshot("2026-03-27"),
            snapshot("2026-03-30", close_shift=2),
            date(2026, 3, 27),
            date(2026, 3, 30),
            date(2026, 3, 31),
        )
        self.assertNotEqual(base["current_sha256"], changed["current_sha256"])
        self.assertNotIn("following_sha256", base)
        self.assertTrue(all("next_open" not in item for item in base["eligible"]))

    def test_duplicate_contract_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Duplicate contract row"):
            rank(
                snapshot("2026-03-27"),
                snapshot("2026-03-30", duplicate=True),
                date(2026, 3, 27),
                date(2026, 3, 30),
                date(2026, 3, 31),
            )


if __name__ == "__main__":
    unittest.main()
