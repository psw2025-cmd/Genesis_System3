"""No real cloud calls; verify the Cloud Run receipt never leaks values."""
import json
import unittest

from scripts.cloud_run_env_contract import EXPECTED, classify


def sample_doc(overrides=None):
    env = [{"name": name, "value": value} for name, value in EXPECTED.items()]
    if overrides:
        for index, item in enumerate(env):
            if item["name"] in overrides:
                env[index] = overrides[item["name"]]
    return {
        "metadata": {"name": "genesis-system3-web", "secret-data": "NEVER_LEAK_THIS"},
        "spec": {"template": {"spec": {"containers": [{"image": "example/image:tag", "env": env}]}}},
        "status": {"latestReadyRevisionName": "genesis-system3-web-00047-wzn",
                   "traffic": [{"revisionName": "genesis-system3-web-00047-wzn", "percent": 100}]},
    }


class SafeCloudRunEnvReceiptTests(unittest.TestCase):
    def test_all_explicit_values_match(self):
        result = classify(sample_doc(), EXPECTED)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checks"]["PAPER_MODE"], "MATCH")
        self.assertFalse(result["deployed_source_sha_verified"])

    def test_missing_mode_blocks(self):
        doc = sample_doc()
        doc["spec"]["template"]["spec"]["containers"][0]["env"] = [
            x for x in doc["spec"]["template"]["spec"]["containers"][0]["env"]
            if x["name"] != "PAPER_MODE"
        ]
        self.assertEqual(classify(doc, EXPECTED)["checks"]["PAPER_MODE"], "MISSING")

    def test_wrong_mode_does_not_leak_value(self):
        doc = sample_doc({"PAPER_MODE": {"name": "PAPER_MODE", "value": "SECRET_SHOULD_NOT_LEAK"}})
        receipt = classify(doc, EXPECTED)
        self.assertEqual(receipt["checks"]["PAPER_MODE"], "VALUE_MISMATCH")
        self.assertNotIn("SECRET_SHOULD_NOT_LEAK", json.dumps(receipt))
        self.assertNotIn("NEVER_LEAK_THIS", json.dumps(receipt))

    def test_duplicate_and_reference_mode_block(self):
        doc = sample_doc()
        env = doc["spec"]["template"]["spec"]["containers"][0]["env"]
        env.append({"name": "PAPER_MODE", "value": "1"})
        self.assertEqual(classify(doc, EXPECTED)["checks"]["PAPER_MODE"], "DUPLICATE")
        doc = sample_doc({"PAPER_MODE": {"name": "PAPER_MODE", "valueFrom": {"secretKeyRef": "REDACTED"}}})
        self.assertEqual(classify(doc, EXPECTED)["checks"]["PAPER_MODE"],
                         "REFERENCE_NOT_PLAINLY_VERIFIED")

    def test_invalid_container_count_and_ci_env_block(self):
        doc = sample_doc()
        doc["spec"]["template"]["spec"]["containers"].append({"env": []})
        self.assertEqual(classify(doc, EXPECTED)["status"], "FAIL")
        self.assertEqual(classify(sample_doc(), {"PAPER_MODE": "0"})["checks"]["PAPER_MODE"],
                         "CI_EXPECTATION_MISMATCH")


if __name__ == "__main__":
    unittest.main()
