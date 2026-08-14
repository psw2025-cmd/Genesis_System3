#!/usr/bin/env python3
"""Market-hours engineering loop — smoke matrix + failure playbooks (cloud proof).

Runs dual-path checks (urllib) against the public Cloud Run dashboard. Writes
reports/latest/market_hours_engineering_loop/{summary.json,README.md}.

Exit codes:
  0 = all hard checks pass (soft gaps allowed after hours)
  1 = hard failure requiring engineering action
  2 = ML collection incomplete or gate honest-fail (expected until 5×ρ≥0.70)

Never enables LIVE trading. Never resumes paused schedulers.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "market_hours_engineering_loop"
BASE = os.environ.get(
    "SYSTEM3_CLOUD_BASE", "https://genesis-system3-web-doq2wplepa-el.a.run.app"
).rstrip("/")
IST = ZoneInfo("Asia/Kolkata")

# Agent domains (consult each other via shared summary.json)
AGENTS = (
    "control_plane",
    "broker_data",
    "ml_history",
    "ui_dashboard",
    "business_lanes",
)


def _get(path: str, timeout: float = 45.0) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "genesis-eng-loop"})
    started = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            if "json" in ctype or path.startswith("/api/"):
                try:
                    data: Any = json.loads(raw.decode("utf-8", errors="replace"))
                except Exception:
                    data = raw.decode("utf-8", errors="replace")[:400]
            else:
                data = raw.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "status": int(getattr(resp, "status", 200) or 200),
                "elapsed_s": (datetime.now(timezone.utc) - started).total_seconds(),
                "data": data,
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": int(exc.code), "elapsed_s": 0.0, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "status": 0, "elapsed_s": 0.0, "error": f"{type(exc).__name__}: {exc}"}


def _market_session_now() -> Dict[str, Any]:
    now = datetime.now(IST)
    weekday = now.weekday() < 5
    minutes = now.hour * 60 + now.minute
    open_m, close_m = 9 * 60 + 15, 15 * 60 + 30
    in_session = weekday and open_m <= minutes <= close_m
    return {
        "ist": now.isoformat(timespec="seconds"),
        "weekday": weekday,
        "in_session": in_session,
        "phase": "market_open" if in_session else ("weekend" if not weekday else "after_hours_or_pre"),
    }


def _playbook(check_id: str, detail: Any) -> Dict[str, str]:
    catalog = {
        "scheduler_unhealthy": {
            "owner": "control_plane",
            "action": "Inspect collector lease + /api/scheduler/health?refresh=true; run control-plane-verify job; do not resume paused schedulers",
        },
        "contract_mismatch": {
            "owner": "control_plane",
            "action": "Diff coverage vs scheduler_contract.py SSOT; fix scheduler identity only if contract drifted",
        },
        "live_on": {
            "owner": "control_plane",
            "action": "EMERGENCY: force LIVE_TRADING_ENABLED=0 / ANALYZE_MODE=1 on service+jobs; re-prove broker/auth",
        },
        "broker_down": {
            "owner": "broker_data",
            "action": "Execute dhan-token-rotate job; recheck /api/broker/status; confirm Secret Manager token",
        },
        "chain_empty": {
            "owner": "broker_data",
            "action": "During session: verify Dhan chain push path; after hours: confirm last-good snapshot age; fix feedQuality empty-state if UI looks broken",
        },
        "ui_down": {
            "owner": "ui_dashboard",
            "action": "Check Cloud Run revision serving /ui; redeploy if asset 404; hard-refresh provenance",
        },
        "ml_days_short": {
            "owner": "ml_history",
            "action": "Cloud execute ml-history-bootstrap for continuum OR wait validate-daily; never soft-pass ρ≥0.70",
        },
        "ml_gate_fail": {
            "owner": "ml_history",
            "action": "Need 5 days with ρ≥0.70; run validate after close; retrain only if rho<0.40×3; UI must show honest fail",
        },
        "business_skipped_in_session": {
            "owner": "business_lanes",
            "action": "In session SKIPPED is a gap: execute rank/forecast/signals jobs, check MARKET_SESSION detector and artifacts",
        },
        "scanner_empty_in_session": {
            "owner": "ui_dashboard",
            "action": "Market-open scanner empty: investigate market-top micro refresh + Dhan OE; UI must not show stale PASS",
        },
    }
    row = catalog.get(check_id) or {
        "owner": "control_plane",
        "action": f"Investigate {check_id}: {json.dumps(detail, default=str)[:180]}",
    }
    return {"check_id": check_id, **row}


def run_once() -> Tuple[Dict[str, Any], int]:
    session = _market_session_now()
    hard_fails: List[str] = []
    soft_gaps: List[str] = []
    passes: List[str] = []
    next_actions: List[Dict[str, str]] = []
    agent_notes: Dict[str, List[str]] = {a: [] for a in AGENTS}

    # --- control_plane ---
    health = _get("/api/scheduler/health?refresh=true")
    h = health.get("data") if isinstance(health.get("data"), dict) else {}
    cov = h.get("coverage") if isinstance(h.get("coverage"), dict) else {}
    obs = h.get("observability") if isinstance(h.get("observability"), dict) else {}
    if health.get("ok") and h.get("status") == "HEALTHY" and cov.get("contract_matched") is True:
        passes.append("scheduler_health")
        agent_notes["control_plane"].append("HEALTHY + contract_matched")
    else:
        hard_fails.append("scheduler_unhealthy")
        next_actions.append(_playbook("scheduler_unhealthy", {"http": health.get("status"), "body_status": h.get("status")}))
    if h.get("live_trading_enabled") is True:
        hard_fails.append("live_on")
        next_actions.append(_playbook("live_on", {}))
    else:
        passes.append("live_off")
    if cov.get("total") == 9 and cov.get("enabled") == 6 and cov.get("paused") == 3:
        passes.append("coverage_9_6_3")
    else:
        hard_fails.append("contract_mismatch")
        next_actions.append(_playbook("contract_mismatch", cov))

    # --- broker_data ---
    broker = _get("/api/broker/status")
    b = broker.get("data") if isinstance(broker.get("data"), dict) else {}
    if broker.get("ok") and b.get("connected") is True and b.get("order_placement_allowed") is not True:
        passes.append("broker_connected_orders_off")
        agent_notes["broker_data"].append("connected; orders blocked")
    else:
        hard_fails.append("broker_down")
        next_actions.append(_playbook("broker_down", b))

    chains_ok = 0
    chain_detail = {}
    for sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
        ch = _get(f"/api/chain/{sym}", timeout=90)
        d = ch.get("data") if isinstance(ch.get("data"), dict) else {}
        spot = float(d.get("spot") or 0)
        n = len(d.get("contracts") or [])
        ok = bool(ch.get("ok") and spot > 0 and n > 0)
        if not ok and session["in_session"]:
            # One retry — Dhan/index feed can flap at open.
            ch = _get(f"/api/chain/{sym}", timeout=90)
            d = ch.get("data") if isinstance(ch.get("data"), dict) else {}
            spot = float(d.get("spot") or 0)
            n = len(d.get("contracts") or [])
            ok = bool(ch.get("ok") and spot > 0 and n > 0)
        chain_detail[sym] = {"spot": spot, "contracts": n, "status": d.get("status"), "ok": ok}
        if ok:
            chains_ok += 1
    if chains_ok == 4:
        passes.append("chains_4")
        agent_notes["broker_data"].append("4/4 chains spot+contracts")
    elif session["in_session"] and chains_ok >= 3:
        soft_gaps.append(f"chains_flaky:{chains_ok}/4")
        next_actions.append(_playbook("chain_empty", chain_detail))
        agent_notes["broker_data"].append(f"flaky open feed {chains_ok}/4 — retry loop")
    elif session["in_session"]:
        hard_fails.append("chain_empty")
        next_actions.append(_playbook("chain_empty", chain_detail))
    else:
        soft_gaps.append(f"chains_partial_after_hours:{chains_ok}/4")
        next_actions.append(_playbook("chain_empty", chain_detail))

    # --- ui_dashboard ---
    ui = _get("/ui/")
    if ui.get("ok") and ui.get("status") == 200:
        passes.append("cloud_ui")
        agent_notes["ui_dashboard"].append("cloud /ui 200")
    else:
        hard_fails.append("ui_down")
        next_actions.append(_playbook("ui_down", ui))

    top = _get("/api/scanner/top_contract_gainers?top_n=3&market_top_n=10&include_equity=1", timeout=90)
    td = top.get("data") if isinstance(top.get("data"), dict) else {}
    rows = td.get("market_top_table") or []
    if top.get("ok") and len(rows) > 0:
        passes.append("scanner_rows")
        agent_notes["ui_dashboard"].append(f"scanner rows={len(rows)}")
    elif session["in_session"]:
        hard_fails.append("scanner_empty_in_session")
        next_actions.append(_playbook("scanner_empty_in_session", {"status": td.get("status")}))
    else:
        soft_gaps.append(f"scanner_empty_expected:{td.get('status')}")
        agent_notes["ui_dashboard"].append("scanner empty after hours — expected")

    # --- ml_history ---
    gates = _get("/api/auto_gates?refresh=true")
    g = gates.get("data") if isinstance(gates.get("data"), dict) else {}
    ml = (g.get("gates") or {}).get("ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS") or {}
    days_rec = int(ml.get("days_recorded") or 0)
    days_pass = int(ml.get("days_passing_threshold") or 0)
    ml_pass = ml.get("pass") is True
    if days_rec >= 5:
        passes.append("ml_days_recorded_ge_5")
        agent_notes["ml_history"].append(f"days_recorded={days_rec}")
    else:
        soft_gaps.append(f"ml_days_short:{days_rec}/5")
        next_actions.append(_playbook("ml_days_short", ml))
    if ml_pass:
        passes.append("ml_gate_pass")
    else:
        soft_gaps.append(f"ml_gate_honest_fail:pass_days={days_pass}/5 rho={ml.get('latest_rho')}")
        next_actions.append(_playbook("ml_gate_fail", ml))
        agent_notes["ml_history"].append("gate fail is honest until 5×ρ≥0.70")

    # --- business_lanes (lane windows differ; do not treat evening/post-close SKIPPED as hard) ---
    arts = h.get("artifacts") if isinstance(h.get("artifacts"), list) else []
    by_lane = {str(a.get("lane")): a for a in arts if isinstance(a, dict)}
    minute = datetime.now(IST).hour * 60 + datetime.now(IST).minute
    expected_now = []
    if session["in_session"]:
        expected_now.extend(["rank", "forecast"])
    if 18 * 60 + 30 <= minute <= 23 * 60:
        expected_now.append("signals")
    if 15 * 60 + 30 <= minute <= 16 * 60 + 45:
        expected_now.append("validate")
    bad_lanes = []
    for lane in expected_now:
        art = by_lane.get(lane) or {}
        st = str(art.get("status") or "").upper()
        reason = str(art.get("reason_code") or "")
        if st == "SKIPPED" and reason == "MARKET_SESSION_CLOSED":
            bad_lanes.append(lane)
        elif st in {"", "SKIPPED"} and lane in {"rank", "forecast"} and session["in_session"]:
            bad_lanes.append(lane)
    if bad_lanes:
        hard_fails.append("business_skipped_in_session")
        next_actions.append(_playbook("business_skipped_in_session", {"bad_lanes": bad_lanes}))
    else:
        passes.append("business_lanes_window_ok")
        skipped = [k for k, v in by_lane.items() if str(v.get("status")).upper() == "SKIPPED"]
        if skipped:
            soft_gaps.append(f"lanes_skipped_outside_window:{','.join(skipped)}")
        agent_notes["business_lanes"].append(f"expected_now={expected_now}")

    # Cross-agent consultation notes
    consultations = [
        {
            "from": "broker_data",
            "to": "ui_dashboard",
            "info": f"chains_ok={chains_ok}; scanner_rows={len(rows)}; UI must reflect after-hours honestly",
        },
        {
            "from": "ml_history",
            "to": "ui_dashboard",
            "info": f"ML pass={ml_pass} days_rec={days_rec} pass_days={days_pass}; dashboard must not claim LIVE ready",
        },
        {
            "from": "control_plane",
            "to": "business_lanes",
            "info": f"health={h.get('status')} business_readiness={h.get('business_readiness')} phase={session['phase']}",
        },
        {
            "from": "ui_dashboard",
            "to": "control_plane",
            "info": "Dashboard is proof surface — any API hard fail blocks full-pass goal",
        },
    ]

    summary = {
        "schema": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "base": BASE,
        "session": session,
        "live_trading_enabled": False,
        "pass": passes,
        "hard_fails": hard_fails,
        "soft_gaps": soft_gaps,
        "next_actions": next_actions,
        "agent_notes": agent_notes,
        "consultations": consultations,
        "ml": {
            "days_recorded": days_rec,
            "days_passing_threshold": days_pass,
            "pass": ml_pass,
            "latest_rho": ml.get("latest_rho"),
            "evidence_plane": g.get("evidence_plane"),
        },
        "coverage": cov,
        "observability": obs,
        "deploy_git_sha": h.get("deploy_git_sha"),
        "overall_hard_pass": len(hard_fails) == 0,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Market Hours Engineering Loop",
        "",
        f"- Phase: `{session['phase']}` IST `{session['ist']}`",
        f"- Hard pass: **{summary['overall_hard_pass']}**",
        f"- Hard fails: `{hard_fails or 'none'}`",
        f"- Soft gaps: `{soft_gaps or 'none'}`",
        f"- ML: recorded={days_rec} passing_ρ≥0.70={days_pass}/5 gate={ml_pass}",
        f"- LIVE: OFF",
        "",
        "## Next actions",
        "",
    ]
    for a in next_actions:
        lines.append(f"- **{a.get('owner')}** / `{a.get('check_id')}`: {a.get('action')}")
    lines.extend(["", "## Consultations", ""])
    for c in consultations:
        lines.append(f"- {c['from']} → {c['to']}: {c['info']}")
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "overall_hard_pass": summary["overall_hard_pass"],
        "hard_fails": hard_fails,
        "soft_gaps": soft_gaps,
        "ml": summary["ml"],
        "next_actions": next_actions,
        "phase": session["phase"],
    }, indent=2))

    if hard_fails:
        return summary, 1
    if soft_gaps and any(g.startswith("ml_") for g in soft_gaps):
        return summary, 2
    return summary, 0


def main() -> int:
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    _, code = run_once()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
