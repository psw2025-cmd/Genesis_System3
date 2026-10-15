"""Tests for EQ-DURABILITY-041: Immutable commit-pinned equity publication bundles."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.error import URLError

# Standard test imports
import scripts.equity_durable_publication as pub


class TestEquityDurablePublication(unittest.TestCase):

    def setUp(self):
        self.repo = "psw2025-cmd/Genesis_System3"
        self.sha = "730e149c22c40428df93417c02b105e1c4ba7540"
        self.pred_id = "EQ7D-2026-10-15-RELIANCE-V1"
        self.pred_bytes = b'{"prediction_id":"EQ7D-2026-10-15-RELIANCE-V1","symbol":"RELIANCE","event_hash":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}'
        self.proj_bytes = b'{"prediction_id":"EQ7D-2026-10-15-RELIANCE-V1","symbol":"RELIANCE","projection_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"}'
        self.manifest_event = {
            "prediction_id": self.pred_id,
            "registered_at": "2026-10-15T10:00:00Z",
            "due_at": "2026-10-22T10:00:00Z",
            "event_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "prediction_event_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "projection_hash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "prediction_uri": "research/forward/equity/2026-10-15/pred.json",
            "projection_uri": "research/forward/equity/2026-10-15/proj.json",
            "prediction_size_bytes": len(self.pred_bytes),
            "prediction_file_sha256": sha256(self.pred_bytes).hexdigest(),
            "projection_size_bytes": len(self.proj_bytes),
            "projection_file_sha256": sha256(self.proj_bytes).hexdigest(),
            "pre_maturity_registered": True,
        }
        self.manifest_uri = "research/forward/equity/2026-10-15/manifest.ndjson"
        self.manifest_bytes = json.dumps(self.manifest_event, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"

    def _good_fetcher(self, repo, sha, rel_path):
        if rel_path == self.manifest_uri:
            return self.manifest_bytes
        elif rel_path == self.manifest_event["prediction_uri"]:
            return self.pred_bytes
        elif rel_path == self.manifest_event["projection_uri"]:
            return self.proj_bytes
        raise KeyError(f"Unknown path {rel_path}")

    def _comment(
        self,
        body,
        *,
        comment_id=555001,
        created_at="2026-10-15T10:05:00Z",
        updated_at=None,
        login="psw2025-cmd",
        author_association="OWNER",
    ):
        return {
            "id": comment_id,
            "url": (
                "https://api.github.com/repos/psw2025-cmd/"
                f"Genesis_System3/issues/comments/{comment_id}"
            ),
            "issue_url": (
                "https://api.github.com/repos/psw2025-cmd/"
                "Genesis_System3/issues/471"
            ),
            "html_url": (
                "https://github.com/psw2025-cmd/Genesis_System3/"
                f"pull/471#issuecomment-{comment_id}"
            ),
            "created_at": created_at,
            "updated_at": updated_at or created_at,
            "body": body,
            "user": {"login": login, "type": "User", "id": 1},
            "author_association": author_association,
        }

    # 1. No remote fetch adapter fails closed
    def test_01_no_remote_fetch_adapter_rejected(self):
        with self.assertRaises(pub.MaturityObservationError) as ctx:
            pub.verify_remote_artifact_bytes(
                repository=self.repo,
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=self.pred_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes),
                fetch_fn=None,  # No fetcher
            )
        self.assertIn("REMOTE_ARTIFACT_FETCHER_REQUIRED", str(ctx.exception))

    # 2. Remote byte or size mismatch rejected
    def test_02_remote_byte_or_size_mismatch_rejected(self):
        def bad_fetcher(r, s, p):
            return b"corrupted bytes"
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository=self.repo,
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=self.pred_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes),
                fetch_fn=bad_fetcher,
            )

    # 3. Wrong repository or invalid commit SHA rejected
    def test_03_wrong_repository_or_invalid_commit_sha_rejected(self):
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository="other-user/Genesis_System3",
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=self.pred_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(self.pred_bytes),
                fetch_fn=self._good_fetcher,
            )
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_artifact_commit_sha("HEAD")

    # 4. Unsafe paths or symlink escapes rejected
    def test_04_unsafe_paths_or_symlink_escapes_rejected(self):
        for bad in ["../secret.json", "/etc/passwd", "foo/../../bar"]:
            with self.assertRaises(pub.MaturityObservationError):
                pub.verify_remote_artifact_bytes(
                    repository=self.repo,
                    commit_sha=self.sha,
                    relative_path=bad,
                    expected_bytes=self.pred_bytes,
                    expected_sha256=sha256(self.pred_bytes).hexdigest(),
                    expected_size=len(self.pred_bytes),
                    fetch_fn=self._good_fetcher,
                )

    # 5. Equivalent JSON different bytes rejected
    def test_05_equivalent_json_different_bytes_rejected(self):
        alt_bytes = b'{\n  "symbol": "RELIANCE",\n  "predicted_return_pct": 5.2\n}'
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_remote_artifact_bytes(
                repository=self.repo,
                commit_sha=self.sha,
                relative_path="research/pred.json",
                expected_bytes=alt_bytes,
                expected_sha256=sha256(self.pred_bytes).hexdigest(),
                expected_size=len(alt_bytes),
                fetch_fn=self._good_fetcher,
            )

    # 6. Exact manifest bytes and semantic replay enforced
    def test_06_exact_manifest_bytes_and_semantic_replay_enforced(self):
        # Mismatched prediction hash inside manifest event
        bad_manifest_event = dict(self.manifest_event)
        bad_manifest_event["prediction_event_hash"] = "0" * 64
        with self.assertRaises(pub.MaturityObservationError):
            pub.verify_prepared_publication_bundle(
                repository=self.repo,
                artifact_commit_sha=self.sha,
                manifest_event=bad_manifest_event,
                manifest_uri=self.manifest_uri,
                manifest_raw=self.manifest_bytes,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                session_date="2026-10-15",
                evidence_root=Path("."),
                fetch_fn=self._good_fetcher,
            )

    # 7. No posting adapter fails before writes
    def test_07_no_posting_adapter_fails_before_writes(self):
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "receipts.ndjson"
            with self.assertRaises(pub.MaturityObservationError) as ctx:
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    manifest_uri=self.manifest_uri,
                    manifest_raw=self.manifest_bytes,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    session_date="2026-10-15",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=ledger_path,
                    fetch_fn=self._good_fetcher,
                    post_fn=None,  # No posting adapter
                    get_fn=lambda pid: [],
                )
            self.assertIn("PUBLICATION_POST_ADAPTER_REQUIRED", str(ctx.exception))
            self.assertFalse(ledger_path.exists())

    # 8. Two independent concurrent publishers serialized by identity
    def test_08_two_independent_concurrent_publishers_serialized(self):
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "receipts.ndjson"
            posted_comments = []
            
            def thread_safe_post(b):
                c = self._comment(b)
                posted_comments.append(c)
                return c

            def thread_safe_get(pid):
                return list(posted_comments)

            def worker():
                return pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    manifest_uri=self.manifest_uri,
                    manifest_raw=self.manifest_bytes,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    session_date="2026-10-15",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=ledger_path,
                    fetch_fn=self._good_fetcher,
                    post_fn=thread_safe_post,
                    get_fn=thread_safe_get,
                )

            with ThreadPoolExecutor(max_workers=2) as ex:
                f1 = ex.submit(worker)
                f2 = ex.submit(worker)
                r1 = f1.result()
                r2 = f2.result()

            self.assertEqual(len(posted_comments), 1)  # Only 1 comment posted!
            self.assertEqual(r1["comment_id"], 555001)
            self.assertEqual(r2["comment_id"], 555001)
            # Verify ledger has exactly 1 entry
            with open(ledger_path, "r", encoding="utf-8") as f:
                lines = [line for line in f if line.strip()]
            self.assertEqual(len(lines), 1)

    # 9. Unknown-POST timeout occurring after remote server acceptance reconciled
    def test_09_unknown_post_timeout_after_server_acceptance_reconciled(self):
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "receipts.ndjson"
            server_comments = []
            expected_body = pub.publication_v2_comment_body(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
            )

            def failing_post(b):
                # Server accepted comment, but network timed out before response reached client
                server_comments.append(
                    self._comment(b, comment_id=999333)
                )
                raise TimeoutError("GitHub connection timed out after write")

            res = pub.publish_durable_equity_attestation(
                self.manifest_event,
                manifest_uri=self.manifest_uri,
                manifest_raw=self.manifest_bytes,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
                session_date="2026-10-15",
                evidence_root=Path(tmp),
                receipt_ledger_path=ledger_path,
                fetch_fn=self._good_fetcher,
                post_fn=failing_post,
                get_fn=lambda pid: list(server_comments),
            )
            self.assertEqual(res["comment_id"], 999333)
            self.assertTrue(res["forward_oos_eligible"])

    # 10. Unknown-POST failure without server acceptance fails closed
    def test_10_unknown_post_failure_without_server_acceptance_fails_closed(self):
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "receipts.ndjson"
            def network_fail(b):
                raise URLError("Network unreachable")

            with self.assertRaises(pub.MaturityObservationError) as ctx:
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    manifest_uri=self.manifest_uri,
                    manifest_raw=self.manifest_bytes,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    session_date="2026-10-15",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=ledger_path,
                    fetch_fn=self._good_fetcher,
                    post_fn=network_fail,
                    get_fn=lambda pid: [],
                )
            self.assertIn("PUBLICATION_POST_FAILED", str(ctx.exception))
            self.assertFalse(ledger_path.exists())

    # 11. Changed exact-comment refetch rejected
    def test_11_changed_exact_comment_refetch_rejected(self):
        with TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "receipts.ndjson"
            expected_body = pub.publication_v2_comment_body(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
            )
            def post_then_tamper(b):
                return self._comment(
                    expected_body,
                    comment_id=123999,
                    updated_at="2026-10-15T10:06:00Z",
                )
            with self.assertRaises(pub.MaturityObservationError) as ctx:
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    manifest_uri=self.manifest_uri,
                    manifest_raw=self.manifest_bytes,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    session_date="2026-10-15",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=ledger_path,
                    fetch_fn=self._good_fetcher,
                    post_fn=post_then_tamper,
                    get_fn=lambda pid: [post_then_tamper(expected_body)],
                )
            self.assertIn("PUBLICATION_EDITED_COMMENT_FORBIDDEN", str(ctx.exception))

    # 12. Receipt persistence failure keeps eligibility disabled
    def test_12_receipt_persistence_failure_keeps_eligibility_disabled(self):
        with TemporaryDirectory() as tmp:
            bad_dir = Path(tmp) / "as_dir"
            bad_dir.mkdir()
            # Passing a directory as the ledger path must fail closed
            body = pub.publication_v2_comment_body(
                self.manifest_event,
                artifact_commit_sha=self.sha,
                prediction_raw=self.pred_bytes,
                projection_raw=self.proj_bytes,
            )
            comment = self._comment(body, comment_id=1)
            with self.assertRaises(pub.MaturityObservationError) as ctx:
                pub.publish_durable_equity_attestation(
                    self.manifest_event,
                    manifest_uri=self.manifest_uri,
                    manifest_raw=self.manifest_bytes,
                    artifact_commit_sha=self.sha,
                    prediction_raw=self.pred_bytes,
                    projection_raw=self.proj_bytes,
                    session_date="2026-10-15",
                    evidence_root=Path(tmp),
                    receipt_ledger_path=bad_dir,
                    fetch_fn=self._good_fetcher,
                    post_fn=lambda b: comment,
                    get_fn=lambda pid: [comment],
                )
            self.assertIn("RECEIPT_PATH_CANNOT_BE_DIRECTORY", str(ctx.exception))

    # 13. Permanently reject orphaned MVELECTRO identity
    def test_13_permanently_reject_orphaned_mvelectro_identity(self):
        with self.assertRaises(pub.MaturityObservationError) as ctx:
            pub.validate_prediction_identity_durability("EQ7D-2026-10-14-MVELECTRO-V1", "2026-10-14")
        self.assertIn("ORPHAN_PREDICTION_ID_REJECTED", str(ctx.exception))

    # 14. Session date mismatch rejected without hardcoded fallback
    def test_14_session_date_mismatch_rejected_without_hardcoded_fallback(self):
        with self.assertRaises(pub.MaturityObservationError) as ctx:
            pub.validate_prediction_identity_durability("EQ7D-2026-10-15-RELIANCE-V1", "2026-10-16")
        self.assertIn("PREDICTION_ID_SESSION_DATE_MISMATCH", str(ctx.exception))
        with self.assertRaises(pub.MaturityObservationError) as ctx2:
            pub.validate_prediction_identity_durability("EQ7D-2026-10-15-RELIANCE-V1", None)
        self.assertIn("SESSION_DATE_REQUIRED", str(ctx2.exception))

    # 15. v2 parser strict field and type validation
    def test_15_v2_parser_strict_field_and_type_validation(self):
        body = pub.publication_v2_comment_body(
            self.manifest_event,
            artifact_commit_sha=self.sha,
            prediction_raw=self.pred_bytes,
            projection_raw=self.proj_bytes,
        )
        parsed = pub.parse_publication_v2_attestation(body)
        self.assertEqual(parsed["prediction_id"], self.pred_id)

        # Missing field
        bad_attestation = dict(parsed)
        del bad_attestation["artifact_commit_sha"]
        bad_body = pub.PUBLICATION_V2_BODY_PREFIX + json.dumps(bad_attestation)
        with self.assertRaises(pub.MaturityObservationError) as ctx:
            pub.parse_publication_v2_attestation(bad_body)
        self.assertIn("PUBLICATION_V2_FIELDS_INVALID", str(ctx.exception))

        # Extra field
        bad_attestation2 = dict(parsed)
        bad_attestation2["extra_forbidden_field"] = "evil"
        bad_body2 = pub.PUBLICATION_V2_BODY_PREFIX + json.dumps(bad_attestation2)
        with self.assertRaises(pub.MaturityObservationError) as ctx2:
            pub.parse_publication_v2_attestation(bad_body2)
        self.assertIn("PUBLICATION_V2_FIELDS_INVALID", str(ctx2.exception))

    # 16. Only an immutable owner-authored comment in PR 471 is authoritative
    def test_16_remote_comment_authority_is_required(self):
        body = pub.publication_v2_comment_body(
            self.manifest_event,
            artifact_commit_sha=self.sha,
            prediction_raw=self.pred_bytes,
            projection_raw=self.proj_bytes,
        )
        cases = {
            "wrong_login": self._comment(body, login="attacker"),
            "wrong_association": self._comment(
                body, author_association="CONTRIBUTOR"
            ),
            "wrong_pr_scope": {
                **self._comment(body),
                "issue_url": (
                    "https://api.github.com/repos/psw2025-cmd/"
                    "Genesis_System3/issues/472"
                ),
            },
        }
        for label, comment in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                ledger_path = Path(tmp) / "receipts.ndjson"
                with self.assertRaises(pub.MaturityObservationError) as ctx:
                    pub.publish_durable_equity_attestation(
                        self.manifest_event,
                        manifest_uri=self.manifest_uri,
                        manifest_raw=self.manifest_bytes,
                        artifact_commit_sha=self.sha,
                        prediction_raw=self.pred_bytes,
                        projection_raw=self.proj_bytes,
                        session_date="2026-10-15",
                        evidence_root=Path(tmp),
                        receipt_ledger_path=ledger_path,
                        fetch_fn=self._good_fetcher,
                        post_fn=lambda b, row=comment: row,
                        get_fn=lambda pid, row=comment: [row],
                    )
                self.assertIn(
                    str(ctx.exception),
                    {"PUBLICATION_AUTHOR_INVALID", "PUBLICATION_SOURCE_URL_INVALID"},
                )
                self.assertFalse(ledger_path.exists())

    # 17. Observation and publication cannot predate their durable anchors
    def test_17_publication_timestamp_order_is_required(self):
        body = pub.publication_v2_comment_body(
            self.manifest_event,
            artifact_commit_sha=self.sha,
            prediction_raw=self.pred_bytes,
            projection_raw=self.proj_bytes,
        )
        cases = {
            "pre_registration": (
                self._comment(body, created_at="2026-10-15T09:59:59Z"),
                datetime(2026, 10, 15, 10, 6, tzinfo=timezone.utc),
                "PUBLICATION_PRECEDES_ISSUANCE_MANIFEST",
            ),
            "observed_before_publication": (
                self._comment(body),
                datetime(2026, 10, 15, 10, 4, tzinfo=timezone.utc),
                "PUBLICATION_OBSERVED_BEFORE_PUBLISHED",
            ),
        }
        for label, (comment, observed, error) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                with self.assertRaises(pub.MaturityObservationError) as ctx:
                    pub.publish_durable_equity_attestation(
                        self.manifest_event,
                        manifest_uri=self.manifest_uri,
                        manifest_raw=self.manifest_bytes,
                        artifact_commit_sha=self.sha,
                        prediction_raw=self.pred_bytes,
                        projection_raw=self.proj_bytes,
                        session_date="2026-10-15",
                        evidence_root=Path(tmp),
                        receipt_ledger_path=Path(tmp) / "receipts.ndjson",
                        fetch_fn=self._good_fetcher,
                        post_fn=lambda b, row=comment: row,
                        get_fn=lambda pid, row=comment: [row],
                        first_observed_at=observed,
                    )
                self.assertIn(error, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
