from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "system3_actions_storage_forensic.py"
spec = importlib.util.spec_from_file_location("system3_actions_storage_forensic", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


class ActionsStorageForensicTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 19, tzinfo=timezone.utc)

    def artifact(self, artifact_id, *, created, digest="sha256:abc", name="proof", size=100, head_sha="old", expired=False):
        return {
            "id": artifact_id,
            "name": name,
            "size_in_bytes": size,
            "expired": expired,
            "created_at": created,
            "expires_at": "2026-09-01T00:00:00Z",
            "digest": digest,
            "workflow_run_id": artifact_id + 1000,
            "head_branch": "main",
            "head_sha": head_sha,
        }

    def test_old_exact_digest_duplicate_is_delete_proven_only_on_main(self):
        rows = [
            self.artifact(2, created="2026-08-18T00:00:00Z", head_sha="new"),
            self.artifact(1, created="2026-08-01T00:00:00Z", head_sha="old"),
        ]
        main = mod.classify_duplicate_groups(
            rows, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(main["delete_proven"][0]["id"], 1)
        self.assertEqual(main["delete_proven"][0]["retained_artifact"]["id"], 2)

        pr = mod.classify_duplicate_groups(
            rows, now=self.now, current_sha="current", main_authority=False, min_age_days=7
        )
        self.assertEqual(pr["delete_proven"], [])
        self.assertIn("not_main_authority_run", pr["report_only_duplicates"][0]["blockers"])

    def test_current_main_artifact_is_never_delete_proven(self):
        rows = [
            self.artifact(2, created="2026-08-18T00:00:00Z", head_sha="new"),
            self.artifact(1, created="2026-08-01T00:00:00Z", head_sha="current"),
        ]
        result = mod.classify_duplicate_groups(
            rows, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(result["delete_proven"], [])
        self.assertIn("current_main_evidence", result["report_only_duplicates"][0]["blockers"])

    def test_missing_digest_or_size_inconsistency_fails_closed(self):
        no_digest = [
            self.artifact(2, created="2026-08-18T00:00:00Z", digest=None),
            self.artifact(1, created="2026-08-01T00:00:00Z", digest=None),
        ]
        result = mod.classify_duplicate_groups(
            no_digest, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(result["delete_proven"], [])
        self.assertEqual(result["digest_missing_count"], 2)

        inconsistent = [
            self.artifact(2, created="2026-08-18T00:00:00Z", size=100),
            self.artifact(1, created="2026-08-01T00:00:00Z", size=99),
        ]
        result = mod.classify_duplicate_groups(
            inconsistent, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(result["delete_proven"], [])
        self.assertIn("digest_size_inconsistency", result["report_only_duplicates"][0]["blockers"])

    def test_recent_or_expired_artifact_fails_closed(self):
        recent = [
            self.artifact(2, created="2026-08-18T12:00:00Z"),
            self.artifact(1, created="2026-08-17T00:00:00Z"),
        ]
        result = mod.classify_duplicate_groups(
            recent, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(result["delete_proven"], [])
        self.assertIn("younger_than_7_days", result["report_only_duplicates"][0]["blockers"])

        expired = [
            self.artifact(2, created="2026-08-18T00:00:00Z"),
            self.artifact(1, created="2026-08-01T00:00:00Z", expired=True),
        ]
        result = mod.classify_duplicate_groups(
            expired, now=self.now, current_sha="current", main_authority=True, min_age_days=7
        )
        self.assertEqual(result["delete_proven"], [])
        self.assertIn("already_expired_or_expiring_server_side", result["report_only_duplicates"][0]["blockers"])

    def test_cache_policy_preserves_main_and_recent(self):
        caches = [
            {"id": 1, "key": "old-pr", "ref": "refs/pull/1/merge", "size_in_bytes": 50, "created_at": "2026-07-01T00:00:00Z", "last_accessed_at": "2026-07-15T00:00:00Z"},
            {"id": 2, "key": "main", "ref": "refs/heads/main", "size_in_bytes": 50, "created_at": "2026-07-01T00:00:00Z", "last_accessed_at": "2026-07-15T00:00:00Z"},
            {"id": 3, "key": "recent-pr", "ref": "refs/pull/2/merge", "size_in_bytes": 50, "created_at": "2026-08-18T00:00:00Z", "last_accessed_at": "2026-08-18T00:00:00Z"},
        ]
        rows = {row["id"]: row for row in mod.classify_stale_caches(caches, self.now, stale_days=14)}
        self.assertEqual(rows[1]["decision"], "CACHE_RECLAIM_CANDIDATE")
        self.assertEqual(rows[2]["decision"], "CACHE_KEEP")
        self.assertEqual(rows[3]["decision"], "CACHE_KEEP")


if __name__ == "__main__":
    unittest.main()
