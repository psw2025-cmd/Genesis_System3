#!/usr/bin/env python3
"""System3 MRI — Gmail + Scheduler 5-minute watch tick.

Polls live deploy_info / broker / scheduler/health (and optionally Gmail),
writes reports/latest/mri_watch/LATEST.json + TICK_LOG.jsonl + CHECKLIST.

Never enables LIVE, never IAM/WIF, never dumps secrets.
Does not add GitHub Actions schedule: — use --loop or Windows Task Scheduler.

Usage:
  python scripts/system3_mri_gmail_scheduler_watch.py
  python scripts/system3_mri_gmail_scheduler_watch.py --loop --interval-sec 300
  python scripts/system3_mri_gmail_scheduler_watch.py --skip-gmail
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "reports" / "latest" / "mri_watch"
LIVE_BASE = os.environ.get(
    "SYSTEM3_LIVE_BASE",
    "https://genesis-system3-web-doq2wplepa-el.a.run.app",
)
GMAIL_TOKEN = Path(
    os.environ.get(
        "SYSTEM3_GMAIL_TOKEN_PATH",
        r"C:\Pritam_CV_Tier1_EPC\Piping-E3D-Job-Intelligence\private-config\gmail_token.json",
    )
)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]
GMAIL_QUERY = (
    "(System3 OR Genesis_System3 OR genesis-system3 OR RHUI OR "
    '"issue #188" OR "Cloud Run" OR "Cloud Scheduler" OR '
    '"Workflow Priority Guard" OR CodeQL OR billing OR uptime OR '
    '"Google Cloud" OR psw2025-cmd OR system3-openalgo-safe) newer_than:7d'
)
TIMEOUT_S = 25


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _http_json(url: str) -> tuple[dict[str, Any] | None, str | None, int | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "system3-mri-watch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body), None, getattr(resp, "status", 200)
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}", e.code
    except Exception as e:  # noqa: BLE001 — tick must never crash silently without record
        return None, f"{type(e).__name__}: {e}", None


def _pull_gmail(max_results: int = 15) -> dict[str, Any]:
    if not GMAIL_TOKEN.exists():
        return {
            "ok": False,
            "blocked": True,
            "reason": f"token missing: {GMAIL_TOKEN}",
            "enable_path": (
                "Keep token only under private-config (or SYSTEM3_GMAIL_TOKEN_PATH). "
                "Re-auth locally with existing Piping-E3D gmail OAuth flow; "
                "never paste secrets into chat. Re-run access probe after."
            ),
        }
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as e:
        return {
            "ok": False,
            "blocked": True,
            "reason": f"gmail libs missing: {e}",
            "enable_path": "pip install google-api-python-client google-auth-httplib2 google-auth",
        }

    try:
        creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN), GMAIL_SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
        res = (
            svc.users()
            .messages()
            .list(userId="me", q=GMAIL_QUERY, maxResults=max_results)
            .execute()
        )
        msgs = res.get("messages") or []
        out: list[dict[str, Any]] = []
        for m in msgs:
            full = (
                svc.users()
                .messages()
                .get(
                    userId="me",
                    id=m["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            headers = {
                h["name"]: h["value"]
                for h in full.get("payload", {}).get("headers", [])
            }
            subject = headers.get("Subject") or ""
            snippet = (full.get("snippet") or "")[:240]
            out.append(
                {
                    "id": m["id"],
                    "threadId": full.get("threadId"),
                    "from": headers.get("From"),
                    "subject": subject,
                    "date": headers.get("Date"),
                    "snippet": snippet,
                    "class": _classify_mail(subject, snippet),
                }
            )
        return {
            "ok": True,
            "blocked": False,
            "query": GMAIL_QUERY,
            "count": len(out),
            "messages": out,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "blocked": True,
            "reason": f"{type(e).__name__}: {e}",
            "enable_path": (
                "Refresh gmail_token.json via local OAuth only; "
                "do not paste tokens in chat."
            ),
        }


def _classify_mail(subject: str, snippet: str) -> str:
    text = f"{subject} {snippet}".lower()
    if any(k in text for k in ("billing", "invoice", "payment")):
        return "MRI-BILL"
    if any(k in text for k in ("security", "suspicious", "2-step", "signin")):
        return "MRI-SEC"
    if any(k in text for k in ("uptime", "downtime", "monitoring")):
        return "MRI-UP"
    if "scheduler" in text:
        return "MRI-SCHED"
    if "cloud run" in text or "revision" in text:
        return "MRI-RUN"
    if any(k in text for k in ("workflow", "codeql", "actions", "priority guard")):
        return "MRI-GH"
    if any(k in text for k in ("token", "secret manager", "rotate")):
        return "MRI-TOK"
    if any(k in text for k in ("ruhi", "chatgpt", "#188", "issue #188")):
        return "MRI-RUHI"
    return "MRI-OTHER"


def _decide(
    deploy: dict[str, Any] | None,
    broker: dict[str, Any] | None,
    sched: dict[str, Any] | None,
    deploy_err: str | None,
    broker_err: str | None,
    sched_err: str | None,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if deploy_err or deploy is None:
        reasons.append(f"deploy_info unreachable: {deploy_err}")
        return "FAIL", reasons
    if sched_err or sched is None:
        reasons.append(f"scheduler/health unreachable: {sched_err}")
        return "FAIL", reasons
    if broker_err or broker is None:
        reasons.append(f"broker/status unreachable: {broker_err}")
        return "FAIL", reasons

    if deploy.get("live_trading_enabled") is True:
        reasons.append("LIVE unexpectedly true")
        return "FAIL", reasons
    if broker.get("live_trading_enabled") is True or broker.get(
        "order_placement_allowed"
    ):
        reasons.append("LIVE/orders unexpectedly allowed")
        return "FAIL", reasons

    if not sched.get("healthy") or not sched.get("transport_healthy"):
        reasons.append(
            f"scheduler unhealthy status={sched.get('status')} "
            f"severity={((sched.get('observability') or {}).get('alert_severity'))}"
        )
        return "FAIL", reasons
    cov = sched.get("coverage") or {}
    if cov.get("contract_matched") is False:
        reasons.append("scheduler contract_matched=false")
        return "FAIL", reasons

    auth = broker.get("auth_classification")
    if auth != "AUTH_OK" or not broker.get("connected"):
        reasons.append(f"broker auth={auth} connected={broker.get('connected')}")
        return "FAIL", reasons

    # WARN conditions
    br = sched.get("business_readiness")
    if br and br != "READY":
        reasons.append(f"business_readiness={br}")
    hours = ((broker.get("token_proof") or {}).get("hours_remaining"))
    try:
        if hours is not None and float(hours) < 1.0:
            reasons.append(f"token hours_remaining={hours}")
    except (TypeError, ValueError):
        pass
    obs = sched.get("observability") or {}
    sev = obs.get("alert_severity")
    if sev and sev not in ("none", None, "None"):
        reasons.append(f"alert_severity={sev}")

    if reasons:
        return "WARN", reasons
    return "OK", ["all polled surfaces within OK band"]


def _seed_checklist(
    severity: str,
    reasons: list[str],
    deploy: dict[str, Any] | None,
    broker: dict[str, Any] | None,
    sched: dict[str, Any] | None,
    gmail: dict[str, Any],
    gates: dict[str, Any] | None,
) -> list[dict[str, str]]:
    now = _utc_now()
    serving = (deploy or {}).get("git_sha") or ""
    hours = str(((broker or {}).get("token_proof") or {}).get("hours_remaining") or "")
    br = (sched or {}).get("business_readiness") or ""
    gpass = (gates or {}).get("gates_passing")
    gtot = (gates or {}).get("gates_total")
    rows = [
        {
            "id": "MRI-TRUTH-001",
            "priority": "P0",
            "status": "DONE",
            "title": "Session tick truth poll completed",
            "how_to": "Run scripts/system3_mri_gmail_scheduler_watch.py",
            "owner": "AGENT",
            "proof_required": "reports/latest/mri_watch/LATEST.json",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": f"severity={severity}",
        },
        {
            "id": "MRI-SCHED-001",
            "priority": "P0",
            "status": "WATCH" if br and br != "READY" else ("DONE" if severity == "OK" else "OPEN"),
            "title": f"Scheduler business_readiness={br or 'n/a'}",
            "how_to": "GET /api/scheduler/health?refresh=true; wait weekday jobs if PARTIAL overnight",
            "owner": "AGENT",
            "proof_required": f"{LIVE_BASE}/api/scheduler/health?refresh=true",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": "; ".join(reasons)[:400],
        },
        {
            "id": "MRI-TOK-001",
            "priority": "P0",
            "status": "WATCH" if hours and _safe_float(hours, 99) < 1.0 else "WATCH",
            "title": f"Token hours_remaining={hours}",
            "how_to": "Confirm rotate job ENABLED; never mint LIVE; watch AUTH_OK",
            "owner": "AGENT",
            "proof_required": f"{LIVE_BASE}/api/broker/status",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": f"serving={serving[:12]}",
        },
        {
            "id": "MRI-GATES-001",
            "priority": "P0",
            "status": "OPEN" if (gpass is not None and gtot and gpass < gtot) else "WATCH",
            "title": f"Gates {gpass}/{gtot} — LIVE stays OFF",
            "how_to": "Do not weaken gates; close blockers via market-hours proofs",
            "owner": "AGENT",
            "proof_required": f"{LIVE_BASE}/api/auto_gates",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": "",
        },
        {
            "id": "MRI-LAG-001",
            "priority": "P1",
            "status": "WATCH",
            "title": f"Serving SHA {serving[:12]} — classify lag; no blind redeploy",
            "how_to": "Compare origin/main; redeploy only for runtime path merges",
            "owner": "AGENT",
            "proof_required": "reports/latest/repo_path_audit/cloud_github_vs_laptop.json",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": "",
        },
        {
            "id": "MRI-GMAIL-001",
            "priority": "P1",
            "status": (
                "BLOCKED"
                if gmail.get("blocked")
                else ("DONE" if gmail.get("ok") else "OPEN")
            ),
            "title": (
                f"Gmail pull blocked: {gmail.get('reason')}"
                if gmail.get("blocked")
                else f"Gmail classified count={gmail.get('count', 0)}"
            ),
            "how_to": gmail.get("enable_path")
            or "Token under private-config; classify into MRI-* ids",
            "owner": "AGENT",
            "proof_required": "reports/latest/mri_watch/gmail_latest.json",
            "last_seen_utc": now,
            "source": "gmail",
            "actions_taken": "",
        },
        {
            "id": "MRI-LOOP-001",
            "priority": "P0",
            "status": "OPEN",
            "title": "Ensure 5-min recurrence (Task Scheduler or --loop)",
            "how_to": (
                "schtasks /Create /TN System3_MRI_Gmail_Scheduler_Watch "
                "/SC MINUTE /MO 5 /TR \"python scripts\\system3_mri_gmail_scheduler_watch.py\" /F"
            ),
            "owner": "HUMAN",
            "proof_required": "LATEST.json age < 10 minutes",
            "last_seen_utc": now,
            "source": "live",
            "actions_taken": "script supports --loop --interval-sec 300",
        },
    ]
    # Map mail classes into checklist rows
    for msg in (gmail.get("messages") or [])[:8]:
        cls = msg.get("class") or "MRI-OTHER"
        rows.append(
            {
                "id": f"{cls}-{msg.get('id', '')[:8]}",
                "priority": "P0" if cls in ("MRI-SEC", "MRI-SCHED", "MRI-RUN") else "P1",
                "status": "WATCH",
                "title": (msg.get("subject") or "")[:120],
                "how_to": "Confirm against live APIs before FAIL escalation; Gmail is transport only",
                "owner": "HUMAN" if cls in ("MRI-BILL", "MRI-SEC") else "AGENT",
                "proof_required": "reports/latest/mri_watch/gmail_latest.json",
                "last_seen_utc": now,
                "source": "gmail",
                "actions_taken": "",
            }
        )
    return rows


def _safe_float(v: Any, default: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _write_checklist(rows: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "id",
        "priority",
        "status",
        "title",
        "how_to",
        "owner",
        "proof_required",
        "last_seen_utc",
        "source",
        "actions_taken",
    ]
    csv_path = OUT_DIR / "CHECKLIST.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    md_lines = [
        "# MRI Gmail+Scheduler watch checklist",
        "",
        f"Updated UTC: `{_utc_now()}`",
        "",
        "| id | pri | status | owner | title | proof |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        md_lines.append(
            f"| {r['id']} | {r['priority']} | **{r['status']}** | {r['owner']} | "
            f"{r['title'][:80]} | `{r['proof_required'][:60]}` |"
        )
    (OUT_DIR / "CHECKLIST.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def run_tick(*, skip_gmail: bool = False) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    observed = _utc_now()

    deploy, deploy_err, deploy_code = _http_json(f"{LIVE_BASE}/api/deploy_info")
    broker, broker_err, broker_code = _http_json(f"{LIVE_BASE}/api/broker/status")
    sched, sched_err, sched_code = _http_json(
        f"{LIVE_BASE}/api/scheduler/health?refresh=true"
    )
    gates, gates_err, gates_code = _http_json(f"{LIVE_BASE}/api/auto_gates")

    severity, reasons = _decide(
        deploy, broker, sched, deploy_err, broker_err, sched_err
    )

    # Re-verify once on WARN/FAIL
    if severity in ("WARN", "FAIL"):
        time.sleep(1.0)
        sched2, sched_err2, sched_code = _http_json(
            f"{LIVE_BASE}/api/scheduler/health?refresh=true"
        )
        broker2, broker_err2, broker_code = _http_json(f"{LIVE_BASE}/api/broker/status")
        deploy2, deploy_err2, deploy_code = _http_json(f"{LIVE_BASE}/api/deploy_info")
        if sched2 is not None:
            sched, sched_err = sched2, sched_err2
        if broker2 is not None:
            broker, broker_err = broker2, broker_err2
        if deploy2 is not None:
            deploy, deploy_err = deploy2, deploy_err2
        severity, reasons = _decide(
            deploy, broker, sched, deploy_err, broker_err, sched_err
        )
        reasons.append("reverified=true")

    if skip_gmail:
        gmail: dict[str, Any] = {
            "ok": False,
            "blocked": True,
            "reason": "skipped via --skip-gmail",
            "enable_path": "Re-run without --skip-gmail when token available",
        }
    else:
        gmail = _pull_gmail()

    (OUT_DIR / "gmail_latest.json").write_text(
        json.dumps(gmail, indent=2), encoding="utf-8"
    )

    rows = _seed_checklist(severity, reasons, deploy, broker, sched, gmail, gates)
    _write_checklist(rows)

    tick = {
        "marker": "MRI_GMAIL_SCHEDULER_WATCH_V1",
        "observed_at_utc": observed,
        "severity": severity,
        "reasons": reasons,
        "live_base": LIVE_BASE,
        "http": {
            "deploy_info": {"ok": deploy is not None, "code": deploy_code, "error": deploy_err},
            "broker_status": {"ok": broker is not None, "code": broker_code, "error": broker_err},
            "scheduler_health": {
                "ok": sched is not None,
                "code": sched_code,
                "error": sched_err,
            },
            "auto_gates": {"ok": gates is not None, "code": gates_code, "error": gates_err},
        },
        "deploy": {
            "git_sha": (deploy or {}).get("git_sha"),
            "service_name": (deploy or {}).get("service_name"),
            "live_trading_enabled": (deploy or {}).get("live_trading_enabled"),
            "region": (deploy or {}).get("region"),
            "project_id": (deploy or {}).get("project_id"),
        },
        "broker": {
            "connected": (broker or {}).get("connected"),
            "auth_classification": (broker or {}).get("auth_classification"),
            "live_trading_enabled": (broker or {}).get("live_trading_enabled"),
            "order_placement_allowed": (broker or {}).get("order_placement_allowed"),
            "hours_remaining": ((broker or {}).get("token_proof") or {}).get(
                "hours_remaining"
            ),
            "secret_version": ((broker or {}).get("token_proof") or {}).get(
                "secret_version"
            ),
            "token_value_exposed": False,
        },
        "scheduler": {
            "healthy": (sched or {}).get("healthy"),
            "transport_healthy": (sched or {}).get("transport_healthy"),
            "status": (sched or {}).get("status"),
            "business_readiness": (sched or {}).get("business_readiness"),
            "business_readiness_reasons": (sched or {}).get("business_readiness_reasons"),
            "contract_matched": ((sched or {}).get("coverage") or {}).get(
                "contract_matched"
            ),
            "alert_severity": ((sched or {}).get("observability") or {}).get(
                "alert_severity"
            ),
            "enabled": ((sched or {}).get("coverage") or {}).get("enabled"),
            "paused": ((sched or {}).get("coverage") or {}).get("paused"),
            "deploy_git_sha": (sched or {}).get("deploy_git_sha"),
        },
        "gates": {
            "gates_passing": (gates or {}).get("gates_passing"),
            "gates_total": (gates or {}).get("gates_total"),
            "trade_ready": (gates or {}).get("trade_ready"),
            "live_trading_enabled": (gates or {}).get("live_trading_enabled"),
            "open_blockers": (gates or {}).get("open_blockers"),
        },
        "gmail": {
            "ok": gmail.get("ok"),
            "blocked": gmail.get("blocked"),
            "count": gmail.get("count"),
            "reason": gmail.get("reason"),
        },
        "actions": {
            "blind_redeploy": False,
            "live_enable": False,
            "iam_wif_change": False,
            "checklist_path": "reports/latest/mri_watch/CHECKLIST.md",
            "plan_path": "docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md",
        },
        "hard_bans_honored": [
            "no_IAM",
            "no_WIF",
            "no_LIVE",
            "no_blind_redeploy",
            "no_actions_schedule_cron",
        ],
    }

    (OUT_DIR / "LATEST.json").write_text(json.dumps(tick, indent=2), encoding="utf-8")
    with (OUT_DIR / "TICK_LOG.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(tick, separators=(",", ":")) + "\n")

    # Compact digest for coordination mirror
    digest = [
        f"# MRI watch digest ({observed})",
        "",
        f"- severity: **{severity}**",
        f"- serving: `{(deploy or {}).get('git_sha')}`",
        f"- broker: auth={(broker or {}).get('auth_classification')} hours={tick['broker']['hours_remaining']}",
        f"- scheduler: healthy={(sched or {}).get('healthy')} readiness={(sched or {}).get('business_readiness')}",
        f"- gates: {(gates or {}).get('gates_passing')}/{(gates or {}).get('gates_total')}",
        f"- gmail: ok={gmail.get('ok')} blocked={gmail.get('blocked')} count={gmail.get('count')}",
        f"- reasons: {reasons}",
        "",
        "Plan: `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md`",
        "",
    ]
    (OUT_DIR / "DIGEST.md").write_text("\n".join(digest), encoding="utf-8")
    return tick


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="System3 MRI Gmail+Scheduler watch")
    p.add_argument("--loop", action="store_true", help="Repeat forever")
    p.add_argument("--interval-sec", type=int, default=300, help="Loop interval (default 300)")
    p.add_argument("--skip-gmail", action="store_true", help="Skip Gmail pull")
    p.add_argument("--once", action="store_true", help="Single tick (default)")
    args = p.parse_args(argv)

    def _one() -> int:
        tick = run_tick(skip_gmail=args.skip_gmail)
        sev = tick["severity"]
        print(
            f"MRI_WATCH severity={sev} serving={(tick.get('deploy') or {}).get('git_sha')} "
            f"gmail_ok={tick.get('gmail', {}).get('ok')} -> {OUT_DIR / 'LATEST.json'}"
        )
        return 0 if sev in ("OK", "WARN") else 2

    if args.loop:
        while True:
            _one()
            time.sleep(max(30, int(args.interval_sec)))
    return _one()


if __name__ == "__main__":
    raise SystemExit(main())
