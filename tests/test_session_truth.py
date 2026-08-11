import time
import unittest

from dashboard.backend.session_truth import SessionTruthStore


class SessionTruthStoreTests(unittest.TestCase):
    def test_issue_returns_distinct_opaque_tokens(self):
        store = SessionTruthStore()
        token_a, rec_a = store.issue(max_age_seconds=60)
        token_b, rec_b = store.issue(max_age_seconds=60)
        self.assertNotEqual(token_a, token_b)
        self.assertNotEqual(rec_a.session_id_hash, rec_b.session_id_hash)
        self.assertGreaterEqual(len(token_a), 32)
        self.assertNotIn(token_a, rec_a.public_dict().values())

    def test_validate_accepts_only_issued_token(self):
        store = SessionTruthStore()
        token, record = store.issue(max_age_seconds=60)
        self.assertEqual(store.validate(token), record)
        self.assertIsNone(store.validate("not-an-issued-session"))

    def test_logout_revoke_invalidates_server_side(self):
        store = SessionTruthStore()
        token, _ = store.issue(max_age_seconds=60)
        self.assertIsNotNone(store.validate(token))
        self.assertTrue(store.revoke(token))
        self.assertIsNone(store.validate(token))
        self.assertFalse(store.revoke(token))

    def test_expiry_is_enforced_by_server_store(self):
        store = SessionTruthStore()
        token, _ = store.issue(max_age_seconds=1)
        self.assertIsNotNone(store.validate(token))
        time.sleep(1.05)
        self.assertIsNone(store.validate(token))
        self.assertEqual(store.active_count(), 0)

    def test_non_positive_ttl_rejected(self):
        store = SessionTruthStore()
        with self.assertRaises(ValueError):
            store.issue(max_age_seconds=0)


if __name__ == "__main__":
    unittest.main()
