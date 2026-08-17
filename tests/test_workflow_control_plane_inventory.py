from __future__ import annotations

import unittest

from scripts.github_workflow_control_plane import (
    is_terminal_failure,
    run_scope,
    summarize_failed_steps,
)


class WorkflowControlPlaneTests(unittest.TestCase):
    def test_current_main_and_superseded_are_never_mixed(self):
        current = "a" * 40
        self.assertEqual(run_scope({"head_sha": current}, current), "CURRENT_MAIN")
        self.assertEqual(run_scope({"head_sha": "b" * 40}, current), "SUPERSEDED")

    def test_failure_taxonomy_is_fail_closed(self):
        for value in ("failure", "cancelled", "timed_out", "action_required", "startup_failure"):
            self.assertTrue(is_terminal_failure(value), value)
        for value in (None, "", "success", "skipped", "neutral"):
            self.assertFalse(is_terminal_failure(value), value)

    def test_failed_job_and_step_evidence_is_preserved(self):
        jobs = {
            "jobs": [
                {
                    "id": 10,
                    "name": "deploy",
                    "status": "completed",
                    "conclusion": "failure",
                    "steps": [
                        {"name": "build", "number": 1, "conclusion": "success"},
                        {"name": "runtime proof", "number": 2, "conclusion": "failure"},
                    ],
                },
                {
                    "id": 11,
                    "name": "clean",
                    "status": "completed",
                    "conclusion": "success",
                    "steps": [],
                },
            ]
        }
        evidence = summarize_failed_steps(jobs)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["job_id"], 10)
        self.assertEqual(evidence[0]["failed_steps"][0]["name"], "runtime proof")


if __name__ == "__main__":
    unittest.main()
