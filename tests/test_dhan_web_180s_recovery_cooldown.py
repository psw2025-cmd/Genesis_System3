from __future__ import annotations

import importlib.util
import os
from pathlib import Path

_RUNTIME_PATCH = Path("core/brokers/dhan/cloud_runtime_patch.py")


def _load_runtime_patch():
    spec = importlib.util.spec_from_file_location("system3_dhan_web_180s_test", _RUNTIME_PATCH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_web_recovery_cooldown_floor_is_180_seconds(monkeypatch):
    monkeypatch.setenv("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "1")
    module = _load_runtime_patch()
    assert module._rotation_cooldown_s() == 180.0


def test_web_recovery_cooldown_default_remains_900_seconds(monkeypatch):
    monkeypatch.delenv("DHAN_CANONICAL_ROTATION_COOLDOWN_S", raising=False)
    module = _load_runtime_patch()
    assert module._rotation_cooldown_s() == 900.0


def test_web_never_mints_locally():
    text = _RUNTIME_PATCH.read_text(encoding="utf-8")
    assert "generate_token(" not in text
    assert "jobs/{job}:run" in text
    assert "return max(180.0" in text
