"""Missing ML proof must never serialize as NULL or truthy readiness."""
from __future__ import annotations

import ast
import json
from pathlib import Path


APP = Path(__file__).resolve().parents[1] / "dashboard/backend/app.py"


def _functions():
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    wanted = {"_fetch_cloud_ml_performance", "_local_ml_readiness_view"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    scope = {"Any": object, "Dict": dict, "json": json, "_CLOUD_ML_PERFORMANCE_URL": "https://example.invalid/performance"}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(APP), "exec"), scope)
    return scope


def test_local_missing_proof_is_explicitly_blocked():
    view = _functions()["_local_ml_readiness_view"]({})
    assert view["ready_for_live"] is False
    assert view["status"] == "BLOCKED"
    assert view["ready_for_live_reason"] == "ML_PROOF_MISSING_OR_UNVERIFIED"


def test_local_string_true_does_not_authorize_live():
    view = _functions()["_local_ml_readiness_view"]({"ready_for_live": "true"})
    assert view["ready_for_live"] is False


def test_cloud_null_or_truthy_string_does_not_authorize_live(monkeypatch):
    scope = _functions()

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            return False
        def read(self, _limit):
            return b'{"ready_for_live":"true"}'

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    scope["urllib"] = urllib
    payload = scope["_fetch_cloud_ml_performance"]()
    assert payload["ready_for_live"] is False
    assert payload["status"] == "BLOCKED"


def test_cloud_read_failure_is_false_not_null(monkeypatch):
    scope = _functions()
    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError("offline")))
    scope["urllib"] = urllib
    payload = scope["_fetch_cloud_ml_performance"]()
    assert payload["ready_for_live"] is False
    assert payload["status"] == "UNVERIFIED"
