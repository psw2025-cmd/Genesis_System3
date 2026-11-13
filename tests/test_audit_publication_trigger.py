"""Prevent a false green audit publisher that skips publication on code changes."""
import pathlib
import unittest

WORKFLOW = pathlib.Path(__file__).resolve().parents[1] / ".github/workflows/cloud-verify.yml"


class TriggerContractTests(unittest.TestCase):
    def test_publisher_gate_detects_changed_paths_without_fragile_regex(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('changes="$(git diff --name-only HEAD^ HEAD -- audit_results/ scripts/cloud_audit_publish.py .github/workflows/cloud-verify.yml)"', content)
        self.assertIn('if [[ -n "$changes" ]]; then', content)
        self.assertNotIn("grep -Eq", content)
        self.assertIn("AUDIT_PUBLICATION_SKIPPED=no_audit_or_publisher_changes", content)

    def test_immutable_publisher_is_main_only_and_not_deployment(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: github.event_name == 'push' && github.ref == 'refs/heads/main'", content)
        self.assertIn("scripts/cloud_audit_publish.py --repo-root . --publication-sha", content)
        job = content.split("  immutable-audit-publication:", 1)[1]
        self.assertNotIn("gcloud run deploy", job)
        self.assertNotIn("gcloud run services update-traffic", job)
        self.assertNotIn("broker POST", job)


if __name__ == "__main__":
    unittest.main()
