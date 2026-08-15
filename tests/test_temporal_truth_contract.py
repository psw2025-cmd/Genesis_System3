from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.system3_temporal_truth_guard import evaluate_manifest

ROOT = Path(__file__).resolve().parents[1]


class TemporalTruthContractTests(unittest.TestCase):
    def _manifest(self, started: datetime, captured: datetime) -> dict:
        return {
            "evidence_class": "REQUEST_SCOPED_LIVE_BROWSER",
            "capture_started_at_utc": started.isoformat(),
            "captured_at_utc": captured.isoformat(),
            "max_age_seconds": 300,
            "safety": {
                "read_only_capture": True,
                "mutation_endpoints_called": False,
                "order_endpoints_called": False,
                "secret_values_exposed": False,
            },
        }

    def test_fresh_request_scoped_browser_evidence_can_be_current(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        requested = now - timedelta(seconds=60)
        manifest = self._manifest(now - timedelta(seconds=50), now - timedelta(seconds=5))
        verdict = evaluate_manifest(manifest, requested_at=requested, now=now)
        self.assertTrue(verdict["current_live_allowed"])
        self.assertEqual(verdict["state"], "CURRENT_LIVE")

    def test_newest_but_old_artifact_is_not_current(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        manifest = self._manifest(now - timedelta(hours=1), now - timedelta(hours=1))
        verdict = evaluate_manifest(manifest, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("EVIDENCE_TOO_OLD_FOR_CURRENT_VERDICT", verdict["reasons"])

    def test_capture_before_request_cannot_answer_now(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        requested = now - timedelta(seconds=30)
        manifest = self._manifest(now - timedelta(seconds=90), now - timedelta(seconds=20))
        verdict = evaluate_manifest(manifest, requested_at=requested, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("CAPTURE_STARTED_BEFORE_CURRENT_REQUEST", verdict["reasons"])

    def test_reports_latest_name_has_no_temporal_authority(self):
        now = datetime(2026, 8, 15, 21, 10, tzinfo=timezone.utc)
        manifest = {
            "evidence_class": "REPORTS_LATEST",
            "captured_at_utc": now.isoformat(),
            "capture_started_at_utc": now.isoformat(),
            "safety": {},
        }
        verdict = evaluate_manifest(manifest, now=now)
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("EVIDENCE_CLASS_NOT_LIVE", verdict["reasons"])

    def test_missing_capture_time_fails_closed(self):
        verdict = evaluate_manifest({"evidence_class": "REQUEST_SCOPED_LIVE_BROWSER"})
        self.assertFalse(verdict["current_live_allowed"])
        self.assertIn("CAPTURE_TIME_MISSING_OR_INVALID", verdict["reasons"])

    def test_agent_and_governance_entry_points_reference_temporal_policy(self):
        required = [
            ROOT / "AGENTS.md",
            ROOT / "GEMINI.md",
            ROOT / ".cursorrules",
            ROOT / ".github" / "CLAUDE_INSTRUCTIONS.md",
            ROOT / "GOVERNANCE.md",
            ROOT / "docs" / "authority" / "AUTONOMOUS_OPERATIONS_POLICY.md",
            ROOT / "docs" / "project_control" / "SYSTEM3_MASTER_GOAL_LOCK.md",
            ROOT / "docs" / "SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md",
            ROOT / "docs" / "SYSTEM3_CURRENT_BLOCKER_RUNBOOK.md",
            ROOT / "docs" / "runtime" / "AUTHORITATIVE_RUNTIME_AND_DATA_MAP.md",
            ROOT / "docs" / "project_control" / "PRODUCTION_GRADE_BLOCKER_MATRIX.md",
        ]
        for path in required:
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertIn("SYSTEM3_TEMPORAL_TRUTH_V1", text, str(path))
            self.assertIn("TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md", text, str(path))

    def test_live_ui_script_captures_all_canonical_tabs_and_brackets_apis(self):
        text = (ROOT / "scripts" / "gcp_live_ui_snapshot.py").read_text(encoding="utf-8")
        for marker in [
            "from frontend_local_runtime_smoke import Browser, TABS, _wait_tab",
            '"evidence_class": "REQUEST_SCOPED_LIVE_BROWSER"',
            '"api_start": api_start',
            '"api_end": api_end',
            '"tabs_expected": list(TABS)',
            '"new_current_request_requires_new_capture": True',
            '"stored_artifact_becomes_historical_after_capture": True',
        ]:
            self.assertIn(marker, text)

    def test_live_ui_proof_requires_exact_serving_sha_before_and_after_capture(self):
        text = (ROOT / "scripts" / "gcp_live_ui_snapshot.py").read_text(encoding="utf-8")
        for marker in [
            "_wait_for_expected_serving_sha",
            "/api/deploy-info",
            "SYSTEM3_EXPECTED_SERVING_SHA",
            "GITHUB_SHA",
            "EXPECTED_SERVING_SHA_NOT_CONVERGED",
            '"exact_serving_sha_stable": exact_sha_stable',
            '"serving_sha_at_capture_start": start_sha',
            '"serving_sha_at_capture_end": end_sha',
            '"fresh_browser_is_not_enough_without_exact_serving_sha": True',
            "NOT_CURRENT_SERVING_SHA",
        ]:
            self.assertIn(marker, text)
        policy = (ROOT / "docs" / "authority" / "TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md").read_text(encoding="utf-8")
        self.assertIn("Exact-serving-SHA lock", policy)
        self.assertIn("same `main` push", policy)
        self.assertIn("NOT_CURRENT_SERVING_SHA", policy)

    def test_frontend_workflow_runs_temporal_contract_before_live_capture(self):
        text = (ROOT / ".github" / "workflows" / "frontend-runtime-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("tests.test_temporal_truth_contract", text)
        self.assertIn("system3_temporal_truth_guard.py", text)
        self.assertIn("gcp_live_ui_snapshot.py", text)
        self.assertIn("request-scoped read-only live production ui lifecycle proof", text.lower())
        self.assertIn("SYSTEM3_LIVE_PROOF_DEPLOY_WAIT_SECONDS", text)
        self.assertIn("timeout 900s python scripts/gcp_live_ui_snapshot.py", text)

    def test_multi_agent_coordinator_does_not_promote_reports_latest_or_http_200(self):
        text = (ROOT / "tools" / "multi_agent_production_coordinator.py").read_text(encoding="utf-8")
        for marker in [
            "SYSTEM3_TEMPORAL_TRUTH_V1",
            '"evidence_class": "HISTORICAL_EVIDENCE"',
            '"evidence_class": "REQUEST_SCOPED_LIVE_API"',
            '"reports_latest_is_current_truth": False',
            '"http_200_is_semantic_ui_pass": False',
            '"semantic_dashboard_production_grade": False',
            "DEFAULT_GCP_URL",
        ]:
            self.assertIn(marker, text)

    def test_retired_render_and_angel_are_not_current_authority_in_entry_files(self):
        for path in [ROOT / "AGENTS.md", ROOT / "GEMINI.md", ROOT / ".cursorrules"]:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            self.assertIn("dhan", text)
            self.assertIn("retired", text)
            self.assertIn("non-authoritative", text)


if __name__ == "__main__":
    unittest.main()
