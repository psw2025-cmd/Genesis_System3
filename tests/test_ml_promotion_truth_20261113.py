"""Regression checks for ML readiness truth, isolated from runtime credentials."""
from __future__ import annotations

import ast
import json
import tempfile
import types
import unittest
from pathlib import Path
from typing import Any, Dict

SOURCE = Path(__file__).resolve().parents[1] / "dashboard/backend/app.py"


def isolated_function(name: str, env: dict):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(funcs) == 1, name
    code = compile(ast.Module(body=funcs, type_ignores=[]), str(SOURCE), "exec")
    namespace = dict(env)
    exec(code, namespace)
    return namespace[name]


class MLPromotionGuardTests(unittest.TestCase):
    def test_matured_proof_required(self):
        gate = isolated_function("_ml_promotion_allowed", {"Any": Any})
        self.assertFalse(gate(True, False, 0))
        self.assertFalse(gate(True, True, 0))
        self.assertFalse(gate(False, True, 2))
        self.assertFalse(gate(True, True, "not-a-number"))
        self.assertFalse(gate("true", True, 2))
        self.assertFalse(gate(True, "true", 2))
        self.assertTrue(gate(True, True, 2))

    def test_accuracy_report_blocked_even_if_historical_validation_passes(self):
        func = isolated_function("_ml_accuracy_report_record", {
            "Path": Path, "Dict": Dict, "Any": Any, "json": json,
            "ml_router": types.SimpleNamespace(_check_real_validations=lambda: (True, "historical PASS")),
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model_accuracy_report.json"
            path.write_text(json.dumps({
                "summary": {"proof_pass_count": 0, "blocked_count": 1,
                            "direction_hit_rate": 0.8, "rows": 1},
                "rows": [{"blocker_reason": "NO_PREDICTION_SOURCE_FOUND"}],
            }), encoding="utf-8")
            record = func(path)
        self.assertFalse(record["model_proof_ready"])
        self.assertFalse(record["ready_for_live"])

    def test_phantom_option_model_cannot_claim_live_readiness(self):
        func = isolated_function("_ml_options_training_record", {
            "Path": Path, "Dict": Dict, "Any": Any, "json": json,
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "options_ml_training_summary.json"
            path.write_text(json.dumps({
                "status": "PASS", "best_model": "CatBoost-Challenger-v4",
                "proof_pass_count": 0, "dataset_rows": 0, "results": {},
            }), encoding="utf-8")
            record = func(path)
        self.assertFalse(record["model_proof_ready"])
        self.assertFalse(record["ready_for_live"])
        self.assertEqual(record["blocker_reason"], "PHANTOM_FAMILY_NO_WEIGHTS")

    def test_api_uses_guard_for_root_readiness(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('performance["ready_for_live"] = _ml_promotion_allowed(', source)
        self.assertIn('"ready_for_live": performance["ready_for_live"],', source)


if __name__ == "__main__":
    unittest.main()
