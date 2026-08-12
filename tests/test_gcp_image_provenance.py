from __future__ import annotations

import json
import unittest

from scripts.gcp_image_provenance import assert_same_artifact_image, resolve_artifact_digest


class GcpImageProvenanceTests(unittest.TestCase):
    def test_tag_and_cloud_run_digest_resolve_equal(self) -> None:
        digest = "a" * 64
        expected = "asia-south1-docker.pkg.dev/p/r/image:sha-tag"
        deployed = f"asia-south1-docker.pkg.dev/p/r/image@sha256:{digest}"

        def fake_run(args: list[str]) -> str:
            self.assertEqual(args[:5], ["gcloud", "artifacts", "docker", "images", "describe"])
            self.assertEqual(args[5], expected)
            return json.dumps({
                "image_summary": {
                    "fully_qualified_digest": f"asia-south1-docker.pkg.dev/p/r/image@sha256:{digest}"
                }
            })

        repo, resolved = assert_same_artifact_image(expected, deployed, run=fake_run)
        self.assertEqual(repo, "asia-south1-docker.pkg.dev/p/r/image")
        self.assertEqual(resolved, f"sha256:{digest}")

    def test_wrong_digest_is_rejected(self) -> None:
        expected_digest = "b" * 64
        deployed_digest = "c" * 64
        expected = "asia-south1-docker.pkg.dev/p/r/image:build-tag"
        deployed = f"asia-south1-docker.pkg.dev/p/r/image@sha256:{deployed_digest}"

        def fake_run(_args: list[str]) -> str:
            return json.dumps({"image_summary": {"digest": f"sha256:{expected_digest}"}})

        with self.assertRaisesRegex(RuntimeError, "candidate image mismatch"):
            assert_same_artifact_image(expected, deployed, run=fake_run)

    def test_resolution_failure_is_fail_closed(self) -> None:
        def fake_run(_args: list[str]) -> str:
            return "{}"

        with self.assertRaisesRegex(RuntimeError, "artifact_digest_resolution_ambiguous"):
            resolve_artifact_digest("asia-south1-docker.pkg.dev/p/r/image:tag", run=fake_run)

    def test_non_artifact_registry_reference_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "artifact_registry_reference_required"):
            resolve_artifact_digest("docker.io/library/python:3.11", run=lambda _args: "{}")


if __name__ == "__main__":
    unittest.main()
