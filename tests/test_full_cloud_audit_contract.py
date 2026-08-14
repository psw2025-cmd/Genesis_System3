from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOUD = ROOT / "scripts" / "gcp_full_cloud_audit.py"
EXACT = ROOT / "scripts" / "fetch_exact_security_audit.py"
AI = ROOT / "scripts" / "multi_ai_audit_consensus.py"
WF = ROOT / ".github" / "workflows" / "full-cloud-audit.yml"
GUARD = ROOT / ".github" / "scripts" / "workflow_priority_guard.py"
POLICY = ROOT / "docs" / "SYSTEM3_WORKFLOW_PRIORITY_POLICY.md"


class FullCloudAuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cloud = CLOUD.read_text(encoding="utf-8")
        cls.exact = EXACT.read_text(encoding="utf-8")
        cls.ai = AI.read_text(encoding="utf-8")
        cls.wf = WF.read_text(encoding="utf-8")
        cls.guard = GUARD.read_text(encoding="utf-8")
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_cloud_audit_contains_required_read_only_evidence(self):
        for marker in (
            'roles/run.invoker',
            'allUsers',
            '/api/health',
            '/api/broker/status',
            'ssl.create_default_context',
            'http_429',
            'rate_limit_text',
            'firestore_permission',
            'gcloud", "logging", "read',
            'gcloud", "logging", "sinks", "list',
            'gcloud", "run", "jobs", "executions", "list',
            'payload_accessed": False,
            'order_actions_performed": False,
        ):
            self.assertIn(marker, self.cloud)

    def test_cloud_audit_has_no_gcp_mutation_commands(self):
        forbidden = (
            '"create"', '"update"', '"delete"', '"deploy"',
            '"add-iam-policy-binding"', '"remove-iam-policy-binding"',
            '"execute"',
        )
        gcloud_lines = [line for line in self.cloud.splitlines() if '"gcloud"' in line]
        for line in gcloud_lines:
            for token in forbidden:
                self.assertNotIn(token, line, msg=f"mutating gcloud token in: {line}")

    def test_cloud_audit_never_reads_secret_payloads(self):
        lowered = self.cloud.lower()
        self.assertNotIn("access-secret-version", lowered)
        self.assertNotIn('secrets", "versions", "access', lowered)
        self.assertIn('"payload_accessed": False', self.cloud)
        self.assertIn('"secret_payloads_accessed": False', self.cloud)

    def test_workflow_is_read_only_and_live_off(self):
        self.assertIn("contents: read", self.wf)
        self.assertIn("actions: read", self.wf)
        self.assertIn("id-token: write", self.wf)
        self.assertNotIn("contents: write", self.wf)
        self.assertNotIn("deployments: write", self.wf)
        self.assertNotRegex(self.wf, re.compile(r"\bgcloud\s+run\s+(deploy|services\s+update|jobs\s+deploy|jobs\s+execute)\b"))
        self.assertIn('LIVE_TRADING_ENABLED: "0"', self.wf)
        self.assertIn('SYSTEM3_LIVE_TRADING_ALLOWED: "0"', self.wf)
        self.assertIn('AUTO_EXECUTE_TRADES: "0"', self.wf)
        self.assertIn("persist-credentials: false", self.wf)

    def test_exact_security_fetch_rejects_stale_evidence(self):
        self.assertIn("head_sha", self.exact)
        self.assertIn("r.get(\"head_sha\") == SHA", self.exact)
        self.assertIn("stale_evidence_accepted", self.exact)
        self.assertIn("BLOCKED_EXACT_SECURITY_RUN_TIMEOUT", self.exact)

    def test_ai_consensus_cannot_override_deterministic_failure(self):
        self.assertIn('OPENAI_MODEL = os.getenv("OPENAI_AUDIT_MODEL", "gpt-4o")', self.ai)
        self.assertIn('ANTHROPIC_MODEL = os.getenv("ANTHROPIC_AUDIT_MODEL", "claude-sonnet-4-20250514")', self.ai)
        self.assertIn("security.get(\"state\") == \"PASS\"", self.ai)
        self.assertIn("cloud.get(\"state\") == \"PASS\"", self.ai)
        self.assertIn('"ai_can_override_deterministic_failure": False', self.ai)
        self.assertIn("BLOCKED_MISSING_API_KEY", self.ai)
        self.assertIn("BLOCKED_EXTERNAL_AI", self.ai)
        self.assertIn("context_1m_proven", self.ai)

    def test_full_cloud_workflow_registered_in_governance(self):
        self.assertIn('"full-cloud-audit.yml"', self.guard)
        self.assertIn('"Full Cloud Audit and Forensic Consensus"', self.guard)
        self.assertIn("`full-cloud-audit.yml`", self.policy)
        self.assertNotIn("schedule:", self.wf)

    def test_unified_verdict_requires_all_deterministic_and_ai_gates(self):
        for marker in (
            "cloud_audit_pass",
            "cloud_safety_pass",
            "exact_security_evidence",
            "security_audit_pass",
            "ai_consensus_pass",
            "all(conditions.values())",
        ):
            self.assertIn(marker, self.wf)


if __name__ == "__main__":
    unittest.main()
