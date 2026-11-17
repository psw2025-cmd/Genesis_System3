import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_observability_bootstrap_is_read_only_and_least_privilege():
    text = (ROOT / "deploy/gcp/bootstrap_observability.sh").read_text(encoding="utf-8")

    assert 'OBSERVER_SA_NAME="${OBSERVER_SA_NAME:-genesis-system3-observer}"' in text
    assert 'SCHEDULER_SA_NAME="${SCHEDULER_SA_NAME:-genesis-system3-observer-scheduler}"' in text
    assert '--role="roles/storage.objectCreator"' in text
    assert '--role="roles/run.invoker"' in text
    assert "--uniform-bucket-level-access" in text
    assert "--public-access-prevention" in text
    assert "--lifecycle-file=observability/gcs_lifecycle.json" in text
    assert '--schedule="*/5 * * * *"' in text
    assert '--period=1' in text
    assert '"/api/health"' in text
    assert '"/ui"' in text
    assert "monitoring.googleapis.com/uptime_check/check_passed" in text
    assert '"duration": "180s"' in text
    assert '"severity": "p0"' in text
    assert "gcloud monitoring policies create" in text
    assert "notification_channels=NOT_CONFIGURED" in text

    forbidden = [
        "roles/secretmanager.admin",
        "roles/secretmanager.secretAccessor",
        "dhan-pin",
        "dhan-totp-secret",
        "DHAN_ACCESS_TOKEN",
        "API_KEY=",
        "place_order",
        "modify_order",
        "cancel_order",
        "LIVE_TRADING_ENABLED=1",
        "SYSTEM3_LIVE_TRADING_ALLOWED=1",
        "AUTO_EXECUTE_TRADES=1",
    ]
    for marker in forbidden:
        assert marker not in text


def test_synthetic_build_uses_dedicated_dockerfile_and_image_substitution():
    text = (ROOT / "observability/cloudbuild.synthetic.yaml").read_text(encoding="utf-8")
    assert "observability/Dockerfile.synthetic" in text
    assert "${_IMAGE}" in text
    assert "CLOUD_LOGGING_ONLY" in text


def test_observability_bootstrap_has_valid_bash_syntax():
    subprocess.run(
        ["bash", "-n", str(ROOT / "deploy/gcp/bootstrap_observability.sh")],
        check=True,
        text=True,
        capture_output=True,
    )


def test_synthetic_has_valid_node_syntax_when_node_is_available():
    node = shutil.which("node")
    if node is None:
        return
    subprocess.run(
        [node, "--check", str(ROOT / "observability/playbooks/synthetic_smoke.js")],
        check=True,
        text=True,
        capture_output=True,
    )
