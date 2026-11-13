"""Pure, read-only gates for public metadata and paper signal display."""

from urllib.parse import urlparse

_CLOUD_URL = "https://genesis-system3-web-802404398783.asia-south1.run.app"


def public_url_for_runtime(candidate: str, *, on_cloud_run: bool) -> str:
    """Keep local loopback local, and never advertise it from Cloud Run."""
    value = str(candidate or "").strip().rstrip("/")
    if not on_cloud_run:
        return value or "http://127.0.0.1:8000"
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host or host in {"localhost", "127.0.0.1", "::1"}:
        return _CLOUD_URL
    return value


def gate_model_prediction(row: dict, *, loaded_model_count: int) -> dict:
    """Do not expose a trade recommendation when model proof is absent."""
    gated = dict(row)
    if loaded_model_count < 1 or gated.get("model_loaded") is not True:
        gated.update(
            model_loaded=False,
            confidence_pct=0.0,
            recommendation="WAIT",
            signal="HOLD",
        )
    return gated


def gate_model_state(state: dict) -> dict:
    """Return a safe display copy when no model is loaded in runtime state."""
    model = state.get("model") or {}
    metrics = model.get("metrics") or {} if isinstance(model, dict) else {}
    try:
        count = int(metrics.get("models_loaded") or 0)
    except (TypeError, ValueError):
        count = 0
    if count > 0:
        return state
    gated = dict(state)
    signals = dict(gated.get("signals") or {})
    last_signal = dict(signals.get("last_signal") or {})
    last_signal.update(action="WAIT", recommendation="WAIT", signal="HOLD", confidence=0.0, confidence_pct=0.0, model_loaded=False)
    signals.update(status="HOLD", confidence=0.0, last_signal=last_signal)
    gated["signals"] = signals
    gated["ml_predictions"] = [gate_model_prediction(row, loaded_model_count=0) for row in gated.get("ml_predictions") or [] if isinstance(row, dict)]
    return gated
