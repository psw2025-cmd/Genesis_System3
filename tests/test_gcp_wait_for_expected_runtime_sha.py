from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "gcp_wait_for_expected_runtime_sha.py"


def _load_module():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("gcp_wait_for_expected_runtime_sha_test", SCRIPT)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        if sys.path and sys.path[0] == str(SCRIPTS):
            sys.path.pop(0)


def test_single_100_revision_requires_exactly_one_traffic_target():
    mod = _load_module()
    assert mod._single_100_revision({"status": {"traffic": [{"revisionName": "rev-a", "percent": 100}]}}) == "rev-a"
    assert mod._single_100_revision({"status": {"traffic": [{"revisionName": "rev-a", "percent": 90}, {"revisionName": "rev-b", "percent": 10}]}}) is None


def test_safe_deploy_sha_reads_only_named_env_and_requires_full_sha():
    mod = _load_module()
    sha = "a" * 40
    revision = {"spec": {"containers": [{"env": [{"name": "OTHER", "value": "secret-ish"}, {"name": "DEPLOY_GIT_SHA", "value": sha}]}]}}
    assert mod._safe_deploy_sha(revision) == sha
    revision["spec"]["containers"][0]["env"][1]["value"] = "short"
    assert mod._safe_deploy_sha(revision) is None


def test_main_waits_until_expected_runtime_is_serving(monkeypatch, tmp_path: Path):
    mod = _load_module()
    expected = "b" * 40
    observations = iter([
        ("rev-old", "a" * 40, None),
        ("rev-new", expected, None),
    ])
    monkeypatch.setattr(mod, "OUT", tmp_path)
    monkeypatch.setattr(mod, "TIMEOUT_S", 30)
    monkeypatch.setattr(mod, "POLL_S", 2)
    monkeypatch.setattr(mod, "resolve_runtime_deploy_sha", lambda head: (expected, ["config/example.json"]))
    monkeypatch.setattr(mod, "observe", lambda: next(observations))
    monkeypatch.setattr(mod.time, "sleep", lambda _: None)
    assert mod.main() == 0
    report = json.loads((tmp_path / "runtime_convergence.json").read_text(encoding="utf-8"))
    assert report["state"] == "PASS"
    assert report["expected_serving_sha"] == expected
    assert report["serving_sha"] == expected
    assert report["attempt_count"] == 2
    assert report["read_only"] is True
