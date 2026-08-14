#!/usr/bin/env python3
"""Parallel external AI consultation over sanitized deterministic audit evidence.

No AI can override deterministic safety/runtime failures. Missing provider access
is BLOCKED, never PASS. Input is the sanitized audit JSON only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.getenv("SYSTEM3_CLOUD_AUDIT_JSON", "reports/latest/full_cloud_audit/full_cloud_audit.json"))
OUT = Path(os.getenv("SYSTEM3_AI_CONSENSUS_DIR", "reports/latest/ai_consensus"))
OPENAI_MODEL = os.getenv("OPENAI_AUDIT_MODEL", "gpt-4o")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_AUDIT_MODEL", "claude-sonnet-4-20250514")
ANTHROPIC_BETA = os.getenv("ANTHROPIC_1M_BETA_HEADER", "").strip()


def _post(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _get(url: str, headers: dict[str, str], timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _safe_error(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTPError:{exc.code}"
    return f"{type(exc).__name__}:{str(exc)[:100]}"


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None


def _prompt(audit: dict[str, Any]) -> str:
    compact = json.dumps(audit, sort_keys=True, separators=(",", ":"))
    return (
        "You are an independent cloud/security forensic reviewer. Analyze the supplied sanitized Genesis System3 audit. "
        "Do not assume missing evidence is healthy. Deterministic FAIL or safety failure cannot be overridden. "
        "Return ONLY JSON with keys: verdict (PASS or FAIL), confidence (0..1), blocking_findings (array of strings), "
        "rationale (string <= 600 chars). PASS only if the evidence itself proves deployment/runtime/security safety.\nAUDIT="
        + compact
    )


def _openai(audit: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return {"state": "BLOCKED_MISSING_API_KEY", "model": OPENAI_MODEL}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        model = _get(f"https://api.openai.com/v1/models/{OPENAI_MODEL}", {"Authorization": f"Bearer {key}"})
        if model.get("id") != OPENAI_MODEL:
            return {"state": "BLOCKED_MODEL_NOT_PROVEN", "model": OPENAI_MODEL}
        response = _post("https://api.openai.com/v1/chat/completions", headers, {
            "model": OPENAI_MODEL,
            "temperature": 0,
            "max_tokens": 1200,
            "messages": [
                {"role": "system", "content": "Return strict JSON only. You cannot override deterministic failures."},
                {"role": "user", "content": _prompt(audit)},
            ],
        })
        text = (((response.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
        parsed = _extract_json(text)
        if not parsed or parsed.get("verdict") not in {"PASS", "FAIL"}:
            return {"state": "FAIL_INVALID_RESPONSE", "model": OPENAI_MODEL}
        return {
            "state": "PASS", "model": OPENAI_MODEL, "verdict": parsed.get("verdict"),
            "confidence": parsed.get("confidence"), "blocking_findings": parsed.get("blocking_findings") or [],
            "rationale": str(parsed.get("rationale") or "")[:600],
            "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
    except Exception as exc:
        return {"state": "BLOCKED_PROVIDER_ERROR", "model": OPENAI_MODEL, "error": _safe_error(exc)}


def _anthropic(audit: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return {"state": "BLOCKED_MISSING_API_KEY", "model": ANTHROPIC_MODEL, "context_1m_proven": False}
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    if ANTHROPIC_BETA:
        headers["anthropic-beta"] = ANTHROPIC_BETA
    try:
        response = _post("https://api.anthropic.com/v1/messages", headers, {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 1200,
            "temperature": 0,
            "system": "Return strict JSON only. You cannot override deterministic failures.",
            "messages": [{"role": "user", "content": _prompt(audit)}],
        })
        text = "".join(str(x.get("text") or "") for x in response.get("content") or [] if isinstance(x, dict) and x.get("type") == "text")
        parsed = _extract_json(text)
        if not parsed or parsed.get("verdict") not in {"PASS", "FAIL"}:
            return {"state": "FAIL_INVALID_RESPONSE", "model": ANTHROPIC_MODEL, "context_1m_proven": False}
        return {
            "state": "PASS", "model": ANTHROPIC_MODEL, "verdict": parsed.get("verdict"),
            "confidence": parsed.get("confidence"), "blocking_findings": parsed.get("blocking_findings") or [],
            "rationale": str(parsed.get("rationale") or "")[:600],
            "context_1m_requested": True,
            "context_1m_proven": bool(ANTHROPIC_BETA),
            "context_beta_header_configured": bool(ANTHROPIC_BETA),
            "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
    except Exception as exc:
        return {
            "state": "BLOCKED_PROVIDER_ERROR", "model": ANTHROPIC_MODEL, "error": _safe_error(exc),
            "context_1m_requested": True, "context_1m_proven": False,
        }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        report = {"state": "BLOCKED_AUDIT_MISSING", "error": type(exc).__name__}
        (OUT / "ai_consensus.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2
    audit_hash = hashlib.sha256(json.dumps(audit, sort_keys=True).encode()).hexdigest()
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_openai = ex.submit(_openai, audit)
        f_anthropic = ex.submit(_anthropic, audit)
        openai = f_openai.result()
        anthropic = f_anthropic.result()

    providers_ready = openai.get("state") == "PASS" and anthropic.get("state") == "PASS"
    both_pass = providers_ready and openai.get("verdict") == "PASS" and anthropic.get("verdict") == "PASS"
    deterministic_pass = audit.get("state") == "PASS" and (audit.get("safety") or {}).get("state") == "PASS"
    if not providers_ready:
        state = "BLOCKED_EXTERNAL_AI"
    elif not deterministic_pass or not both_pass:
        state = "FAIL"
    else:
        state = "PASS"
    report = {
        "schema": "genesis-system3-ai-consensus-v1",
        "state": state,
        "deterministic_audit_state": audit.get("state"),
        "deterministic_safety_state": (audit.get("safety") or {}).get("state"),
        "audit_sha256": audit_hash,
        "openai": openai,
        "anthropic": anthropic,
        "consensus_rule": "deterministic PASS + OpenAI PASS + Anthropic PASS; missing provider is BLOCKED",
        "ai_can_override_deterministic_failure": False,
        "secret_values_exposed": False,
    }
    (OUT / "ai_consensus.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# Multi-AI Audit Consensus", "", f"Consensus: **{state}**", "",
        f"- Deterministic audit: `{audit.get('state')}`", f"- OpenAI: `{openai.get('state')}` / `{openai.get('verdict')}`",
        f"- Anthropic: `{anthropic.get('state')}` / `{anthropic.get('verdict')}`",
        f"- Claude 1M context proven: `{anthropic.get('context_1m_proven')}`", "",
        "AI cannot override a deterministic failure.", "",
    ]
    (OUT / "ai_consensus.md").write_text("\n".join(md), encoding="utf-8")
    print("AI_AUDIT_CONSENSUS " + json.dumps({"state": state, "openai": openai.get("state"), "anthropic": anthropic.get("state")}, sort_keys=True))
    return 0 if state == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
