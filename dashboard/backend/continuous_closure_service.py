"""Continuous closure control plane — repo-first scan, multi-source verify, resume.

Produces blocker cards + auto-resume pointer without inventing metrics or weakening
proof gates. Safe for PAPER/ANALYZER only.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_PROD = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
REQUEST_PATH_LIVE_TIMEOUT_S = 2.5
REQUEST_PATH_CACHE_TTL_S = 5.0
ORCHESTRATOR_LIVE_TIMEOUT_S = 4.0
ORCHESTRATOR_LIVE_BUDGET_S = 8.0
REQUEST_PATH_EVIDENCE_CLASS = "HISTORICAL_STORED"
LIVE_VERIFY_PATHS = (
    "/api/deploy/info",
    "/api/auto_gates",
    "/api/accuracy_trend",
    "/api/broker/status",
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def parse_backlog_cards(backlog_md: str) -> List[Dict[str, Any]]:
    """Parse markdown table rows from autonomous_loop/BACKLOG.md into cards."""
    cards: List[Dict[str, Any]] = []
    for line in backlog_md.splitlines():
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 5:
            continue
        if cols[0].lower() in {"id", "----"} or set(cols[0]) <= {"-"}:
            continue
        issue_id = cols[0]
        if not re.match(r"^[A-Z]+\d+[a-z]?$", issue_id, re.I) and not re.match(r"^A\d", issue_id):
            # allow A1, A2a, BLK-003 style
            if not re.match(r"^(A\d+[a-z]?|BLK-?\d+|SYS3-BLK-\d+)$", issue_id, re.I):
                continue
        status_raw = cols[-1]
        status_u = status_raw.upper()
        if "VERIFIED" in status_u or status_u.startswith("DONE") or "RESOLVED" in status_u:
            state = "RESOLVED"
        elif "IN_PROGRESS" in status_u:
            state = "IN_PROGRESS"
        else:
            state = "OPEN"
        cards.append(
            {
                "id": issue_id,
                "severity": cols[1] if len(cols) > 1 else "P2",
                "defect": cols[2] if len(cols) > 2 else "",
                "evidence": cols[3] if len(cols) > 3 else "",
                "status_note": status_raw,
                "state": state,
                "source": "backlog_md",
            }
        )
    return cards


def cards_from_auto_gates(auto_gates: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(auto_gates, dict):
        return out
    for g in auto_gates.get("proof_gates") or []:
        if not isinstance(g, dict):
            continue
        passed = g.get("pass") is True or str(g.get("status") or "").upper() == "PASS"
        gid = str(g.get("gate_id") or g.get("id") or "GATE")
        out.append(
            {
                "id": gid,
                "severity": "P0" if not passed else "P3",
                "defect": str(g.get("label") or g.get("name") or gid),
                "evidence": str(g.get("note") or g.get("blocker_id") or ""),
                "status_note": "PASS" if passed else str(g.get("status") or "FAIL"),
                "state": "RESOLVED" if passed else "OPEN",
                "source": "auto_gates",
                "blocker_id": g.get("blocker_id"),
            }
        )
    return out


def merge_cards(*groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for group in groups:
        for card in group:
            cid = str(card.get("id") or "").strip()
            if not cid:
                continue
            prev = by_id.get(cid)
            if prev is None:
                by_id[cid] = dict(card)
                continue
            # Prefer OPEN over RESOLVED when sources disagree (fail-closed).
            if prev.get("state") == "RESOLVED" and card.get("state") == "OPEN":
                by_id[cid] = dict(card)
            elif prev.get("source") == "auto_gates" and card.get("source") == "backlog_md":
                # Keep gate truth for state; attach backlog defect text.
                merged = dict(prev)
                if card.get("defect"):
                    merged["defect"] = card["defect"]
                if card.get("evidence"):
                    merged["evidence"] = f"{merged.get('evidence','')} | {card['evidence']}".strip(" |")
                by_id[cid] = merged
    severity_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    cards = list(by_id.values())
    cards.sort(
        key=lambda c: (
            0 if c.get("state") == "OPEN" else 1 if c.get("state") == "IN_PROGRESS" else 2,
            severity_rank.get(str(c.get("severity") or "P2").upper(), 9),
            str(c.get("id")),
        )
    )
    return cards


def _fetch_json(url: str, timeout_s: float) -> Tuple[Any, int]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body, int(getattr(resp, "status", 200) or 200)


def multi_source_verify(
    root: Path,
    *,
    prod_base: str = DEFAULT_PROD,
    timeout_s: float = ORCHESTRATOR_LIVE_TIMEOUT_S,
    max_budget_s: float = ORCHESTRATOR_LIVE_BUDGET_S,
) -> Dict[str, Any]:
    """Fan-in verify: local reports + optional live production APIs.

    Timeouts stay short and fail-closed so a hung peer/self URL cannot wedge
    the Cloud Run request path. The HTTP handler must not call this with
    include_live=True against its own public origin.
    """
    sources: Dict[str, Any] = {
        "repo": {"ok": True, "checks": {}},
        "reports": {"ok": True, "checks": {}},
        "live": {"ok": False, "checks": {}},
    }

    backlog = root / "reports" / "latest" / "autonomous_loop" / "BACKLOG.md"
    policy = root / "agent_policy.yaml"
    sources["repo"]["checks"]["backlog_exists"] = backlog.exists()
    sources["repo"]["checks"]["agent_policy_exists"] = policy.exists()
    sources["repo"]["ok"] = backlog.exists() and policy.exists()

    gates_summary = root / "reports" / "latest" / "system3_auto_gates" / "summary.json"
    readiness = root / "reports" / "latest" / "production_grade_readiness" / "summary.json"
    sources["reports"]["checks"]["auto_gates_summary"] = gates_summary.exists()
    sources["reports"]["checks"]["readiness_summary"] = readiness.exists()
    sources["reports"]["ok"] = True  # absence is informational, not hard fail

    live_payload: Dict[str, Any] = {}
    remaining = max(0.1, float(max_budget_s))
    deadline = time.monotonic() + remaining
    pool = ThreadPoolExecutor(max_workers=len(LIVE_VERIFY_PATHS))
    try:
        futures = {
            pool.submit(
                _fetch_json,
                prod_base.rstrip("/") + path,
                min(float(timeout_s), max(0.1, deadline - time.monotonic())),
            ): path
            for path in LIVE_VERIFY_PATHS
        }
        try:
            for fut in as_completed(futures, timeout=max(0.1, deadline - time.monotonic())):
                path = futures[fut]
                try:
                    body, status = fut.result(timeout=0)
                    live_payload[path] = body
                    sources["live"]["checks"][path] = {"ok": True, "status": status}
                except Exception as exc:
                    sources["live"]["checks"][path] = {"ok": False, "error": str(exc)[:160]}
        except Exception as exc:
            for path in LIVE_VERIFY_PATHS:
                sources["live"]["checks"].setdefault(
                    path,
                    {"ok": False, "error": f"budget_exceeded:{str(exc)[:80]}"},
                )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    sources["live"]["ok"] = all(
        bool((sources["live"]["checks"].get(p) or {}).get("ok"))
        for p in ("/api/deploy/info", "/api/auto_gates")
    )

    trend = live_payload.get("/api/accuracy_trend") or {}
    gates = live_payload.get("/api/auto_gates") or {}
    ml = None
    for g in gates.get("proof_gates") or []:
        if isinstance(g, dict) and g.get("gate_id") == "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS":
            ml = g
            break
    align = None
    if ml is not None and trend.get("days_available") is not None:
        align = int(trend.get("days_available") or -1) == int(ml.get("days_recorded") or -2)

    return {
        "sources": sources,
        "live_payload_keys": list(live_payload.keys()),
        "contracts": {
            "accuracy_trend_days": trend.get("days_available"),
            "ml_days_recorded": (ml or {}).get("days_recorded"),
            "accuracy_trend_auto_gates_align": align,
            "gates_passing": gates.get("gates_passing"),
            "gates_total": gates.get("gates_total"),
            "serving_sha": (live_payload.get("/api/deploy/info") or {}).get("git_sha"),
            "broker_connected": (live_payload.get("/api/broker/status") or {}).get("connected"),
        },
        "auto_gates": gates if gates else None,
        "checked_at_utc": _utc(),
        "prod_base": prod_base,
    }


def pick_resume_target(cards: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Auto-resume: next OPEN (else IN_PROGRESS) highest severity card."""
    for state in ("IN_PROGRESS", "OPEN"):
        for card in cards:
            if card.get("state") == state:
                return {
                    "next_id": card.get("id"),
                    "severity": card.get("severity"),
                    "defect": card.get("defect"),
                    "state": card.get("state"),
                    "instruction": (
                        "Continue Gemini + E2E continuous closure: test-first in tests/evals/, "
                        "fix root cause, PR→CI→merge→Cloud Run, live SHA verify, update BACKLOG, "
                        "post SYSTEM3_COORDINATION_V1 on Issue #188. Never invent prices/ρ or weaken gates."
                    ),
                }
    return None


def build_continuous_closure_report(
    root: Path,
    *,
    prod_base: str = DEFAULT_PROD,
    include_live: bool = True,
) -> Dict[str, Any]:
    backlog_path = root / "reports" / "latest" / "autonomous_loop" / "BACKLOG.md"
    backlog_cards = parse_backlog_cards(_read_text(backlog_path))

    verify: Dict[str, Any]
    if include_live:
        verify = multi_source_verify(root, prod_base=prod_base)
    else:
        verify = {
            "sources": {"repo": {"ok": backlog_path.exists()}, "reports": {"ok": True}, "live": {"ok": False}},
            "contracts": {},
            "auto_gates": None,
            "checked_at_utc": _utc(),
            "prod_base": prod_base,
        }

    gate_cards = cards_from_auto_gates(verify.get("auto_gates") if isinstance(verify.get("auto_gates"), dict) else None)
    # Prefer local gate summary when live unavailable
    if not gate_cards:
        local = _read_json(root / "reports" / "latest" / "system3_auto_gates" / "summary.json") or {}
        payload = local.get("payload") if isinstance(local.get("payload"), dict) else local
        gate_cards = cards_from_auto_gates(payload if isinstance(payload, dict) else None)

    cards = merge_cards(backlog_cards, gate_cards)
    open_n = sum(1 for c in cards if c.get("state") == "OPEN")
    resolved_n = sum(1 for c in cards if c.get("state") == "RESOLVED")
    resume = pick_resume_target(cards)

    watchdog = {
        "status": "ACTIVE" if open_n else "QUIESCENT",
        "open_blockers": open_n,
        "resolved_blockers": resolved_n,
        "banner_required": open_n > 0 or (verify.get("contracts") or {}).get("gates_passing")
        != (verify.get("contracts") or {}).get("gates_total"),
        "policy": "remove_banner_only_when_all_gates_genuinely_ready",
    }

    return {
        "schema": "continuous_closure_v1",
        "generated_at_utc": _utc(),
        "prod_base": prod_base,
        "phases": {
            "repo_first_scan": {
                "ok": bool(backlog_cards) or backlog_path.exists(),
                "backlog_path": str(backlog_path.relative_to(root)) if backlog_path.exists() else str(backlog_path),
                "backlog_cards": len(backlog_cards),
            },
            "multi_source_verify": verify,
            "watchdog": watchdog,
            "blocker_cards": cards,
            "auto_resume": resume,
        },
        "summary": {
            "open": open_n,
            "in_progress": sum(1 for c in cards if c.get("state") == "IN_PROGRESS"),
            "resolved": resolved_n,
            "total_cards": len(cards),
            "next": (resume or {}).get("next_id"),
            "serving_sha": (verify.get("contracts") or {}).get("serving_sha"),
            "gates": f"{(verify.get('contracts') or {}).get('gates_passing')}/{(verify.get('contracts') or {}).get('gates_total')}",
        },
        "safety": {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "zero_synthetic_inventions": True,
        },
        "request_path": {
            "self_http_fanout": bool(include_live),
            "include_live": bool(include_live),
        },
    }


def stamp_closure_request_path(
    report: Dict[str, Any],
    *,
    cache_hit: bool,
    cache_age_s: float = 0.0,
    live_query: bool = False,
) -> Dict[str, Any]:
    """Label a request-path closure payload so cache cannot impersonate live truth."""
    out = dict(report)
    request_path = dict(out.get("request_path") or {})
    request_path["self_http_fanout"] = False
    request_path["include_live"] = False
    request_path["live_query"] = bool(live_query)
    request_path["live_http_skipped_reason"] = "cloud_run_self_call_deadlock_prevention"
    request_path["cache_hit"] = bool(cache_hit)
    request_path["cache_age_s"] = round(max(0.0, float(cache_age_s)), 3)
    request_path["evidence_class"] = REQUEST_PATH_EVIDENCE_CLASS
    out["request_path"] = request_path
    out["served_at_utc"] = _utc()
    return out


def write_closure_artifacts(root: Path, report: Dict[str, Any]) -> Tuple[Path, Path]:
    out_dir = root / "reports" / "latest" / "continuous_closure"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = out_dir / "summary.json"
    state = out_dir / "resume_state.json"
    summary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    resume = report.get("phases", {}).get("auto_resume")
    state_doc = {
        "schema": "continuous_closure_resume_v1",
        "updated_at_utc": _utc(),
        "resume": resume,
        "summary": report.get("summary"),
        "how_next_session_continues": [
            "Read reports/latest/continuous_closure/resume_state.json",
            "Read reports/latest/autonomous_loop/BACKLOG.md",
            "Follow agent_policy.yaml + Gemini loop + E2E issues→solutions law",
            "Execute next OPEN card test-first; never fake gate PASS",
            "Append proof ledger + intent tick; do not wait for user on routine GitOps",
            "LIVE remains a human gate",
        ],
    }
    state.write_text(json.dumps(state_doc, indent=2) + "\n", encoding="utf-8")
    return summary, state
