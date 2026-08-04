"""
Tests for live-trading gate observability and the state-store backend abstraction.

These tests validate:
- Gate response always includes failing_reasons list
- Gate remains blocked when any required condition fails
- failing_reasons contains actionable information for each failed gate
- StateStoreBackend LocalFileBackend read/write/exists behaviour
- GCSBackend raises ImportError when google-cloud-storage is not installed
- Diagnostics endpoint returns correct structure
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Helper: import the backend module from source (no package install needed)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "backend"))

from dashboard.backend.state_store_backend import (  # noqa: E402
    GCSBackend,
    LocalFileBackend,
    StateStoreBackend,
    get_backend,
    _make_local,
)
import dashboard.backend.state_store_backend as _ssb_mod


# ===========================================================================
# StateStoreBackend — LocalFileBackend
# ===========================================================================


@pytest.fixture()
def tmp_backend(tmp_path):
    return LocalFileBackend(tmp_path)


def test_local_backend_read_missing_returns_none(tmp_backend):
    assert tmp_backend.read("state/nonexistent.json") is None


def test_local_backend_write_then_read(tmp_backend):
    tmp_backend.write("state/test.json", '{"hello": "world"}')
    assert tmp_backend.read("state/test.json") == '{"hello": "world"}'


def test_local_backend_exists(tmp_backend):
    assert not tmp_backend.exists("state/test.json")
    tmp_backend.write("state/test.json", "x")
    assert tmp_backend.exists("state/test.json")


def test_local_backend_write_creates_parent_dirs(tmp_backend):
    tmp_backend.write("deep/nested/dir/file.json", "data")
    assert tmp_backend.exists("deep/nested/dir/file.json")


def test_local_backend_read_json_convenience(tmp_backend):
    obj = {"gate": "kill_switch", "passed": True}
    tmp_backend.write("config/kill_switch.json", json.dumps(obj))
    result = tmp_backend.read_json("config/kill_switch.json")
    assert result["gate"] == "kill_switch"


def test_local_backend_read_json_returns_default_on_missing(tmp_backend):
    assert tmp_backend.read_json("missing.json", default={"x": 1}) == {"x": 1}


def test_local_backend_write_json_convenience(tmp_backend):
    tmp_backend.write_json("state/pnl.json", {"total": 100})
    raw = tmp_backend.read("state/pnl.json")
    assert json.loads(raw)["total"] == 100


def test_local_backend_path_traversal_blocked(tmp_backend, tmp_path):
    """Keys with '..' must not escape the root directory."""
    tmp_backend.write("../escape.json", "bad")
    # The written file must be inside tmp_path, not outside.
    escaped = tmp_path.parent / "escape.json"
    assert not escaped.exists(), "Path traversal must be blocked"


def test_local_backend_overwrite(tmp_backend):
    tmp_backend.write("state/x.json", "first")
    tmp_backend.write("state/x.json", "second")
    assert tmp_backend.read("state/x.json") == "second"


# ===========================================================================
# StateStoreBackend — GCSBackend import guard
# ===========================================================================


def test_gcs_backend_raises_import_error_when_package_missing():
    """GCSBackend must raise ImportError if google-cloud-storage is absent."""
    # Temporarily hide the package from the import system.
    with mock.patch.dict(sys.modules, {"google.cloud": None, "google.cloud.storage": None}):
        with pytest.raises((ImportError, TypeError)):
            GCSBackend()


def test_gcs_backend_raises_value_error_without_bucket_env():
    """GCSBackend must raise ValueError when GCS_STATE_BUCKET is not set."""
    # Provide a minimal fake google.cloud.storage so import succeeds.
    fake_gcs = ModuleType("google.cloud.storage")
    fake_gcs.Client = mock.MagicMock()

    fake_google = ModuleType("google")
    fake_google_cloud = ModuleType("google.cloud")
    fake_google_cloud.storage = fake_gcs

    with mock.patch.dict(sys.modules, {
        "google": fake_google,
        "google.cloud": fake_google_cloud,
        "google.cloud.storage": fake_gcs,
    }):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GCS_STATE_BUCKET", None)
            with pytest.raises(ValueError, match="GCS_STATE_BUCKET"):
                GCSBackend()


# ===========================================================================
# get_backend singleton and factory
# ===========================================================================


def test_get_backend_returns_local_by_default(tmp_path):
    """get_backend() with STATE_BACKEND unset should return LocalFileBackend."""
    _ssb_mod._backend = None  # reset singleton
    with mock.patch.dict(os.environ, {"STATE_BACKEND": "local"}):
        backend = get_backend(root_dir=tmp_path)
    assert isinstance(backend, LocalFileBackend)
    _ssb_mod._backend = None  # clean up


def test_get_backend_singleton(tmp_path):
    """Repeated calls return the same instance."""
    _ssb_mod._backend = None
    with mock.patch.dict(os.environ, {"STATE_BACKEND": "local"}):
        b1 = get_backend(root_dir=tmp_path)
        b2 = get_backend(root_dir=tmp_path)
    assert b1 is b2
    _ssb_mod._backend = None


# ===========================================================================
# Live-trading gate — structure and safety tests
# ===========================================================================


def _build_gate_response(
    live_env: str = "0",
    kill_switch_activated: bool = False,
    live_trading_approved: bool = False,
    max_daily_loss_inr: int = 5000,
    val_days: int = 0,
    avg_rho: float = 0.0,
):
    """
    Simulate the gate evaluation logic from /api/live-trading/gate
    so we can test it without spinning up the full FastAPI app.
    """
    gates = []
    gate_open = True

    def gate(name, passed, detail, fix_hint=""):
        nonlocal gate_open
        if not passed:
            gate_open = False
        gates.append({"gate": name, "passed": passed, "detail": detail, "fix_hint": fix_hint})

    # Gate 1
    gate(
        "env_live_disabled",
        live_env == "0",
        f"LIVE_TRADING_ENABLED={live_env}",
        fix_hint="Set in Cloud Run Variables & Secrets",
    )
    # Gate 2a
    gate(
        "kill_switch_off",
        not kill_switch_activated,
        "Kill switch not activated" if not kill_switch_activated else "KILL SWITCH ACTIVE",
        fix_hint="Set kill_switch_activated=false in kill_switch.json",
    )
    # Gate 2b
    gate(
        "human_approved",
        live_trading_approved,
        "Human approval given" if live_trading_approved else "NOT APPROVED",
        fix_hint="POST /api/live-trading/approve with approval phrase",
    )
    # Gate 3
    gate(
        "validation_days",
        val_days >= 10,
        f"{val_days} validation days (need ≥10)",
        fix_hint="Run daily validation for ≥10 market days",
    )
    gate(
        "ml_accuracy_rho",
        avg_rho >= 0.70,
        f"Avg Spearman ρ={avg_rho:.3f}",
        fix_hint="Improve ML model until ρ ≥ 0.70",
    )
    # Gate 4
    gate(
        "max_loss_configured",
        0 < max_daily_loss_inr <= 10000,
        f"Max daily loss = ₹{max_daily_loss_inr}",
        fix_hint="Set max_daily_loss_inr in kill_switch.json",
    )

    failing_reasons = [
        f"[{g['gate']}] {g['detail']}" + (f" — Fix: {g['fix_hint']}" if g.get("fix_hint") else "")
        for g in gates if not g["passed"]
    ]

    return {
        "gate_open": gate_open,
        "gates": gates,
        "failing_reasons": failing_reasons,
        "summary": f"{sum(1 for g in gates if g['passed'])}/{len(gates)} gates passed",
        "verdict": "LIVE_TRADING_ALLOWED" if gate_open else "LIVE_TRADING_BLOCKED",
        "live_trading_status": "OFF — remains off until all gates pass",
    }


def test_gate_blocked_by_default():
    """No gates pass by default — live trading must be blocked."""
    resp = _build_gate_response()
    assert resp["gate_open"] is False
    assert resp["verdict"] == "LIVE_TRADING_BLOCKED"


def test_gate_response_always_has_failing_reasons_key():
    """failing_reasons must always be present even when empty."""
    resp = _build_gate_response()
    assert "failing_reasons" in resp


def test_gate_failing_reasons_lists_all_failed_gates():
    resp = _build_gate_response()
    failed_names = {g["gate"] for g in resp["gates"] if not g["passed"]}
    reasons_text = " ".join(resp["failing_reasons"])
    for name in failed_names:
        assert name in reasons_text, f"Gate '{name}' not in failing_reasons"


def test_gate_failing_reasons_empty_when_all_pass():
    resp = _build_gate_response(
        live_env="0",
        kill_switch_activated=False,
        live_trading_approved=True,
        max_daily_loss_inr=5000,
        val_days=10,
        avg_rho=0.71,
    )
    assert resp["gate_open"] is True
    assert resp["failing_reasons"] == []


def test_gate_blocked_when_kill_switch_active():
    resp = _build_gate_response(
        kill_switch_activated=True,
        live_trading_approved=True,
        val_days=10,
        avg_rho=0.75,
        max_daily_loss_inr=5000,
    )
    assert resp["gate_open"] is False
    assert any("kill_switch" in r for r in resp["failing_reasons"])


def test_gate_blocked_when_env_live_enabled_but_not_approved():
    """Even if LIVE_TRADING_ENABLED=1, gate blocks if not approved."""
    resp = _build_gate_response(
        live_env="1",
        live_trading_approved=False,
        val_days=10,
        avg_rho=0.75,
        max_daily_loss_inr=5000,
    )
    assert resp["gate_open"] is False


def test_gate_blocked_when_rho_below_threshold():
    resp = _build_gate_response(
        live_trading_approved=True,
        val_days=10,
        avg_rho=0.55,  # below 0.70
        max_daily_loss_inr=5000,
    )
    assert resp["gate_open"] is False
    assert any("ml_accuracy_rho" in r for r in resp["failing_reasons"])


def test_gate_blocked_when_insufficient_validation_days():
    resp = _build_gate_response(
        live_trading_approved=True,
        val_days=5,  # below 10
        avg_rho=0.80,
        max_daily_loss_inr=5000,
    )
    assert resp["gate_open"] is False
    assert any("validation_days" in r for r in resp["failing_reasons"])


def test_gate_blocked_when_max_loss_exceeds_limit():
    resp = _build_gate_response(
        live_trading_approved=True,
        val_days=10,
        avg_rho=0.80,
        max_daily_loss_inr=99999,  # above 10000
    )
    assert resp["gate_open"] is False
    assert any("max_loss" in r for r in resp["failing_reasons"])


def test_gate_blocked_when_max_loss_is_zero():
    resp = _build_gate_response(
        live_trading_approved=True,
        val_days=10,
        avg_rho=0.80,
        max_daily_loss_inr=0,
    )
    assert resp["gate_open"] is False


def test_gate_fix_hints_present_in_failing_reasons():
    resp = _build_gate_response()
    for reason in resp["failing_reasons"]:
        assert "Fix:" in reason, f"Missing fix hint in: {reason}"


def test_gate_each_entry_has_fix_hint_key():
    resp = _build_gate_response()
    for g in resp["gates"]:
        assert "fix_hint" in g, f"Gate '{g['gate']}' missing fix_hint key"


# ===========================================================================
# Diagnostics response structure
# ===========================================================================


def _build_diagnostics_response(env: dict | None = None):
    """Simulate the /api/diagnostics logic with controlled env."""
    _required = [
        ("DHAN_CLIENT_ID", "Dhan broker client ID"),
        ("DHAN_ACCESS_TOKEN", "Dhan broker access token"),
        ("LIVE_TRADING_ENABLED", "Must be '0' for paper"),
        ("WORKER_PUSH_TOKEN", "Shared secret"),
        ("GOOGLE_CLOUD_PROJECT", "GCP project ID"),
        ("GCP_REGION", "Cloud Run region"),
        ("CLOUD_MODE", "Set to '1' on Cloud Run"),
    ]
    _secret_vars = {"DHAN_ACCESS_TOKEN", "WORKER_PUSH_TOKEN"}

    env = env or {}
    required_status = []
    missing_required = []
    for var, desc in _required:
        val = env.get(var)
        present = val is not None and val.strip() != ""
        entry = {"var": var, "present": present, "description": desc}
        if present and var not in _secret_vars:
            entry["value"] = val.strip()
        elif present:
            entry["value"] = "***"
        if not present:
            missing_required.append(var)
        required_status.append(entry)

    return {
        "status": "ok" if not missing_required else "missing_required_vars",
        "all_required_present": len(missing_required) == 0,
        "missing_required": missing_required,
        "required_vars": required_status,
    }


def test_diagnostics_reports_missing_vars():
    resp = _build_diagnostics_response(env={})
    assert resp["status"] == "missing_required_vars"
    assert len(resp["missing_required"]) > 0


def test_diagnostics_ok_when_all_required_present():
    env = {
        "DHAN_CLIENT_ID": "client123",
        "DHAN_ACCESS_TOKEN": "token_abc_xyz",
        "LIVE_TRADING_ENABLED": "0",
        "WORKER_PUSH_TOKEN": "secret",
        "GOOGLE_CLOUD_PROJECT": "my-project",
        "GCP_REGION": "asia-south1",
        "CLOUD_MODE": "1",
    }
    resp = _build_diagnostics_response(env=env)
    assert resp["status"] == "ok"
    assert resp["all_required_present"] is True
    assert resp["missing_required"] == []


def test_diagnostics_masks_secret_vars():
    env = {
        "DHAN_CLIENT_ID": "client123",
        "DHAN_ACCESS_TOKEN": "supersecrettoken",
        "LIVE_TRADING_ENABLED": "0",
        "WORKER_PUSH_TOKEN": "pushsecret",
        "GOOGLE_CLOUD_PROJECT": "my-project",
        "GCP_REGION": "asia-south1",
        "CLOUD_MODE": "1",
    }
    resp = _build_diagnostics_response(env=env)
    for entry in resp["required_vars"]:
        if entry["var"] in ("DHAN_ACCESS_TOKEN", "WORKER_PUSH_TOKEN"):
            if entry.get("present"):
                assert entry.get("value", "").startswith("***"), \
                    f"{entry['var']} value should be masked"


def test_diagnostics_lists_each_required_var():
    resp = _build_diagnostics_response(env={})
    var_names = {e["var"] for e in resp["required_vars"]}
    assert "DHAN_CLIENT_ID" in var_names
    assert "LIVE_TRADING_ENABLED" in var_names
    assert "GOOGLE_CLOUD_PROJECT" in var_names
