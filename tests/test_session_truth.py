import os
import time
import unittest
from unittest.mock import patch

from dashboard.backend.session_truth import SessionTruthStore


class SessionTruthStoreTests(unittest.TestCase):
    def test_issue_returns_distinct_opaque_tokens(self):
        store = SessionTruthStore(backend="memory")
        token_a, rec_a = store.issue(max_age_seconds=60)
        token_b, rec_b = store.issue(max_age_seconds=60)
        self.assertNotEqual(token_a, token_b)
        self.assertNotEqual(rec_a.session_id_hash, rec_b.session_id_hash)
        self.assertGreaterEqual(len(token_a), 32)
        self.assertNotIn(token_a, rec_a.public_dict().values())
        self.assertNotIn(token_a, store._sessions)

    def test_validate_accepts_only_issued_token(self):
        store = SessionTruthStore(backend="memory")
        token, record = store.issue(max_age_seconds=60)
        self.assertEqual(store.validate(token), record)
        self.assertIsNone(store.validate("not-an-issued-session"))

    def test_logout_revoke_invalidates_server_side_and_keeps_tombstone(self):
        store = SessionTruthStore(backend="memory")
        token, _ = store.issue(max_age_seconds=60)
        self.assertIsNotNone(store.validate(token))
        self.assertTrue(store.revoke(token))
        self.assertIsNone(store.validate(token))
        self.assertEqual(store.active_count(), 0)
        self.assertEqual(store.revoked_count(), 1)
        self.assertFalse(store.revoke(token))

    def test_expiry_is_enforced_by_server_store(self):
        store = SessionTruthStore(backend="memory")
        token, _ = store.issue(max_age_seconds=1)
        self.assertIsNotNone(store.validate(token))
        time.sleep(1.05)
        self.assertIsNone(store.validate(token))
        self.assertEqual(store.active_count(), 0)
        self.assertEqual(store.revoked_count(), 0)

    def test_non_positive_ttl_rejected(self):
        store = SessionTruthStore(backend="memory")
        with self.assertRaises(ValueError):
            store.issue(max_age_seconds=0)

    def test_login_throttle_is_authoritative_and_clearable(self):
        store = SessionTruthStore(backend="memory")
        client = "203.0.113.8"
        allowed, retry_after = store.login_allowed(
            client, window_seconds=300, max_failures=3
        )
        self.assertTrue(allowed)
        self.assertEqual(retry_after, 0)

        self.assertEqual(store.record_login_failure(client, window_seconds=300), 1)
        self.assertEqual(store.record_login_failure(client, window_seconds=300), 2)
        self.assertEqual(store.record_login_failure(client, window_seconds=300), 3)
        allowed, retry_after = store.login_allowed(
            client, window_seconds=300, max_failures=3
        )
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

        # Raw client identifiers are never persisted as throttle keys.
        self.assertNotIn(client, store._login_attempts)
        store.clear_login_failures(client)
        self.assertEqual(store._login_attempts, {})
        self.assertTrue(
            store.login_allowed(client, window_seconds=300, max_failures=3)[0]
        )

    def test_cloud_runtime_cannot_select_process_memory(self):
        with patch.dict(os.environ, {"CLOUD_MODE": "1"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "requires SYSTEM3_SESSION_BACKEND=firestore"):
                SessionTruthStore(backend="memory")

    def test_local_default_remains_memory_for_unit_and_dev(self):
        env = dict(os.environ)
        env.pop("CLOUD_MODE", None)
        env.pop("K_SERVICE", None)
        env.pop("SYSTEM3_SESSION_BACKEND", None)
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(SessionTruthStore().backend_name, "memory")


if __name__ == "__main__":
    unittest.main()
