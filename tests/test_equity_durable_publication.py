import sys
import unittest
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

# Add scratch to sys.path
# Standard test imports

import scripts.equity_durable_publication as pub

class TestEquityDurablePublication(unittest.TestCase):

    def setUp(self):
        self.repo = "psw2025-cmd/Genesis_System3"
        self.sha = "730e149c22c40428df93417c02b105e1c4ba7540"
        self.pred_id = "EQ7D-2026-10-15-RELIANCE-V1"
        self.pred_bytes = b'{"symbol":"RELIANCE","predicted_return_pct":5.2}'
        self.proj_bytes = b'{"symbol":"RELIANCE","target_price":2800.0}'
        self.manifest_event = {
            "prediction_id": self.pred_id,
            "entry_session_date": "2026-10-15",
            "registered_at": "2026-10-15T10:00:00Z",
            "due_at": "2026-10-22T10:00:00Z",
            "event_hash": "a" * 64,
            "prediction_event_hash": "b" * 64,
            "projection_hash": "c" * 64,
            "prediction_uri": "research/forward/equity/2026-10-15/pred.json",
            "projection_uri": "research/forward/equity/2026-10-15/proj.json",
            "prediction_size_bytes": len(self.pred_bytes),
            "prediction_file_sha256": sha256(self.pred_bytes).hexdigest(),
            "projection_size_bytes": len(self.proj_bytes),
            "projection_file_sha256": sha256(self.proj_bytes).hexdigest(),
            "pre_maturity_registered": True,
        }

    # 1. Uncommitted or missing artifacts
    def test_01_uncommitted_or_missing_artifacts_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository=self.repo,
                commit_sha=self.sha,
                relative_path="research/forward/equity/pred.json",
                expected_bytes=self.pred_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes) + 10,  # size mismatch
            )

    # 2. Wrong repository or invalid commit SHA
    def test_02_wrong_repository_or_invalid_commit_sha_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository="wrong/repo",
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=self.pred_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes),
            )
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_artifact_commit_sha("HEAD")

    # 3. Unsafe paths or symlink escapes
    def test_03_unsafe_paths_or_symlink_escapes_rejected(self):
        for bad in ["../secret.json", "/etc/passwd", "foo/../../bar"]:
            with self.assertRaises(pub.MaturityObservationError):
                pub.verify_remote_artifact_bytes(
                    repository=self.repo,
                    commit_sha=self.sha,
                    relative_path=bad,
                    expected_bytes=self.pred_bytes,
                    expected_sha256=sha256(self.pred_bytes).hexdigest(),
                    expected_size=len(self.pred_bytes),
                )

    # 4. Equivalent JSON different bytes rejected
    def test_04_equivalent_json_different_bytes_rejected(self):
        alt_bytes = b'{\n  "symbol": "RELIANCE",\n  "predicted_return_pct": 5.2\n}'
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository=self.repo,
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=alt_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes),
            )

    # 5. Identity or semantic mismatch
    def test_05_identity_or_semantic_mismatch_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.validate_prediction_identity_durability("EQ7D-2026-10-15-ABC-V1", "2026-10-16")

    # 6. Issuer publication bypass
    def test_06_issuer_publication_bypass_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_prepared_publication_bundle(
                repository=self.repo,
                artifact_commit_sha="invalid-sha",
                manifest_event=self.manifest_event,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                evidence_root=Path("."),
            )

    # 7. Attestation v1 and v2 collision scanning
    def test_07_attestation_v1_and_v2_collision_scanning(self):
        body_v2 = pub.publication_v2_comment_body(
            self.manifest_event,
            artifact_commit_sha=self.sha,
            prediction_raw=self.pred_bytes,
            projection_raw=self.proj_bytes,
        )
        self.assertTrue(body_v2.startswith(pub.PUBLICATION_V2_BODY_PREFIX))
        parsed = pub.parse_publication_v2_attestation(body_v2)
        self.assertEqual(parsed["prediction_id"], self.pred_id)
        self.assertEqual(parsed["artifact_commit_sha"], self.sha)

    # 8. Receipt replay and eligibility
    def test_08_receipt_replay_and_eligibility(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "receipt.ndjson"
            res = pub.publish_durable_equity_attestation(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                github_token="token",
                evidence_root=Path(tmp),
                receipt_ledger_path=p,
                first_observed_at=datetime(2026, 10, 15, 12, tzinfo=timezone.utc),
            )
            self.assertTrue(res["forward_oos_eligible"])
            self.assertEqual(res["artifact_commit_sha"], self.sha)

    # 9. Permanently rejected orphan identity
    def test_09_permanently_rejected_orphan_identity(self):
        with self.assertRaises(pub.MaturityObservationError) as ctx:
            pub.validate_prediction_identity_durability("EQ7D-2026-10-14-MVELECTRO-V1", "2026-10-14")
        self.assertIn("ORPHAN_PREDICTION_ID_REJECTED", str(ctx.exception))

    # 10. Concurrent publishers serialized by identity
    def test_10_concurrent_publishers_serialized_by_identity(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "receipt.ndjson"
            post_called = 0
            def mock_post(b):
                nonlocal post_called
                post_called += 1
                return {
                    "id": 12345,
                    "created_at": "2026-10-15T10:05:00Z",
                    "updated_at": "2026-10-15T10:05:00Z",
                    "body": b,
                    "user": {"login": "psw2025-cmd", "type": "User", "id": 1},
                    "author_association": "OWNER",
                }
            r1 = pub.publish_durable_equity_attestation(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                github_token="token",
                evidence_root=Path(tmp),
                receipt_ledger_path=p,
                post_fn=mock_post,
            )
            self.assertEqual(post_called, 1)

    # 11. Crash recovery at boundaries
    def test_11_crash_recovery_at_boundaries(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "receipt.ndjson"
            expected_body = pub.publication_v2_comment_body(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
            )
            existing_c = {
                "id": 999111,
                "created_at": "2026-10-15T10:05:00Z",
                "updated_at": "2026-10-15T10:05:00Z",
                "body": expected_body,
                "user": {"login": "psw2025-cmd", "type": "User", "id": 1},
                "author_association": "OWNER",
            }
            res = pub.publish_durable_equity_attestation(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                github_token="token",
                evidence_root=Path(tmp),
                receipt_ledger_path=p,
                get_fn=lambda pid: [existing_c],
            )
            self.assertEqual(res["comment_id"], 999111)

    # 12. Unknown POST reconciliation
    def test_12_unknown_post_reconciliation(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "receipt.ndjson"
            expected_body = pub.publication_v2_comment_body(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
            )
            existing_c = {
                "id": 888222,
                "created_at": "2026-10-15T10:05:00Z",
                "updated_at": "2026-10-15T10:05:00Z",
                "body": expected_body,
                "user": {"login": "psw2025-cmd", "type": "User", "id": 1},
                "author_association": "OWNER",
            }
            def failing_post(b):
                raise TimeoutError("GitHub timeout")
            res = pub.publish_durable_equity_attestation(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                github_token="token",
                evidence_root=Path(tmp),
                receipt_ledger_path=p,
                post_fn=failing_post,
                get_fn=lambda pid: [existing_c],
            )
            self.assertEqual(res["comment_id"], 888222)

    # 13. Changed exact comment refetch rejected
    def test_13_changed_exact_comment_refetch_rejected(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "receipt.ndjson"
            def tampered_post(b):
                return {
                    "id": 777333,
                    "created_at": "2026-10-15T10:05:00Z",
                    "updated_at": "2026-10-15T10:05:00Z",
                    "body": "tampered body",
                    "user": {"login": "psw2025-cmd", "type": "User", "id": 1},
                    "author_association": "OWNER",
                }
            with self.assertRaises(pub.MaturityObservationError):
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    github_token="token",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=p,
                    post_fn=tampered_post,
                )

    # 14. Receipt persistence failure keeps eligibility disabled
    def test_14_receipt_persistence_failure_keeps_eligibility_disabled(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "non_existent_subdir" / "cannot_write" / "receipt.ndjson"
            # Make dir impossible to write by passing bad path
            with self.assertRaises(pub.MaturityObservationError):
                # Pass a file as directory to force OSError
                blocking_file = Path(tmp) / "blocker"
                blocking_file.write_text("x")
                bad_path = blocking_file / "receipt.ndjson"
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    github_token="token",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=bad_path,
                )

    # 15. Stale or backdated session ID rejected
    def test_15_stale_or_backdated_session_id_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.validate_prediction_identity_durability("EQ7D-2026-10-10-RELIANCE-V1", "2026-10-15")


if __name__ == "__main__":
    unittest.main()
