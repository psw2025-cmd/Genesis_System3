#!/usr/bin/env python3
"""System3 pending-issue tracker — OVERWRITE-ONLY live checklist.

Canonical outputs (always replaced, never dated duplicates):
  reports/coordination/TRACKING_CHECKLIST.md
  reports/coordination/TRACKING_CHECKLIST.json
  reports/coordination/session_issues_master.csv

Agents must read TRACKING_CHECKLIST.md every session.
Do NOT create PENDING_*_YYYYMMDD tracking copies for routine refreshes.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "coordination"
BASE = os.environ.get(
    "SYSTEM3_PUBLIC_BASE",
    "https://genesis-system3-web-doq2wplepa-el.a.run.app",
).rstrip("/")
TIMEOUT = float(os.environ.get("SYSTEM3_TRACKER_TIMEOUT", "25"))

# Stable catalog — status may be auto-overridden by live probes below.
CATALOG: list[dict[str, str]] = [
    {"id": "PEND-001", "pri": "P0", "cat": "deploy", "title": "Serving SHA lag behind GitHub main", "verify": "deploy_info==main", "need_user": "None", "rec": "MRI Auto Deploy"},
    {"id": "PEND-002", "pri": "P0", "cat": "scheduler", "title": "Scheduler health UNHEALTHY", "verify": "scheduler/health healthy=true", "need_user": "None", "rec": "MRI Scheduler IAM"},
    {"id": "PEND-003", "pri": "P1", "cat": "broker", "title": "Broker AUTH_OK keep fresh", "verify": "broker connected AUTH_OK", "need_user": "None", "rec": "Watch rotate"},
    {"id": "PEND-004", "pri": "P0", "cat": "chain_ui", "title": "Stale chain badge false-green", "verify": "chain badge STALE when age>60s", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-005", "pri": "P0", "cat": "chain_ui", "title": "Default chain not ATM-centered", "verify": "default VISIBLE +/-10 ATM", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-006", "pri": "P0", "cat": "chain_ui", "title": "Missing LTP Chg %", "verify": "chain header LTP%", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-007", "pri": "P0", "cat": "chain_ui", "title": "Missing Buildup", "verify": "chain header Buildup", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-008", "pri": "P0", "cat": "chain_ui", "title": "Missing OI%/Vol%", "verify": "chain headers OI% Vol%", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-009", "pri": "P0", "cat": "chain_ui", "title": "Missing Greeks columns", "verify": "chain headers Delta..Vega", "need_user": "None", "rec": "Deploy OptionChain fix"},
    {"id": "PEND-010", "pri": "P1", "cat": "equity", "title": "Equity options security_id map", "verify": "equity chain load", "need_user": "Priority underlyings optional", "rec": "Scrip master map"},
    {"id": "PEND-011", "pri": "P1", "cat": "api_404", "title": "/api/holdings /api/funds 404", "verify": "HTTP 200 holdings+funds", "need_user": "None", "rec": "Deploy alias routes"},
    {"id": "PEND-012", "pri": "P1", "cat": "api_404", "title": "/api/charts 404", "verify": "charts 200 or MISSING label", "need_user": "None", "rec": "Implement or mark MISSING"},
    {"id": "PEND-013", "pri": "P1", "cat": "api_404", "title": "multibagger/predictions/backtest 404", "verify": "routes or MISSING", "need_user": "None", "rec": "Wire or honest MISSING"},
    {"id": "PEND-014", "pri": "P0", "cat": "paper", "title": "Paper positions file missing", "verify": "paper open_count or honest empty", "need_user": "LIVE stays OFF", "rec": "Cloud persistence"},
    {"id": "PEND-015", "pri": "P0", "cat": "paper", "title": "Paper P&L synthetic/stale", "verify": "same-day paper proof", "need_user": "None", "rec": "Paper lifecycle"},
    {"id": "PEND-016", "pri": "P0", "cat": "paper", "title": "/api/paper/* subroutes 404", "verify": "subroutes or UI aggregate", "need_user": "None", "rec": "Implement or document"},
    {"id": "PEND-017", "pri": "P0", "cat": "paper", "title": "Paper lifecycle gate FAIL", "verify": "REAL_PAPER_LIFECYCLE pass", "need_user": "None", "rec": "Market-hours proof"},
    {"id": "PEND-018", "pri": "P0", "cat": "paper", "title": "Expectancy negative", "verify": "POSITIVE_NET_EXPECTANCY pass", "need_user": "Do not weaken gate", "rec": "Better signals"},
    {"id": "PEND-019", "pri": "P0", "cat": "ml", "title": "Spearman rho below 0.70", "verify": "ML_SPEARMAN pass", "need_user": "Do not lower threshold", "rec": "Retrain/validate"},
    {"id": "PEND-020", "pri": "P0", "cat": "ml", "title": "ML predictions = 0", "verify": "predictions>0 or BLOCKED honest", "need_user": "None", "rec": "Prediction writer"},
    {"id": "PEND-021", "pri": "P0", "cat": "signals", "title": "Signal file missing / 429", "verify": "signals actionable", "need_user": "None", "rec": "Persist + rate limit"},
    {"id": "PEND-022", "pri": "P1", "cat": "positions", "title": "/api/positions empty file", "verify": "positions truth", "need_user": "None", "rec": "Align paths"},
    {"id": "PEND-023", "pri": "P0", "cat": "freshness", "title": "Tick health gate FAIL", "verify": "WEBSOCKET_TICK_HEALTH pass", "need_user": "None", "rec": "Refresh/WS proof"},
    {"id": "PEND-024", "pri": "P0", "cat": "visibility", "title": "Option visibility gate FAIL", "verify": "OPTION_STRIKE_VISIBILITY pass", "need_user": "None", "rec": "ATM audit"},
    {"id": "PEND-025", "pri": "P1", "cat": "auth", "title": "API key public_readonly", "verify": "policy decided", "need_user": "Enforce or document", "rec": "User decision"},
    {"id": "PEND-026", "pri": "P1", "cat": "governance", "title": "No RUHI board on UI", "verify": "progress board visible", "need_user": "Confirm want board", "rec": "UI board"},
    {"id": "PEND-027", "pri": "P2", "cat": "memory", "title": "Claude memory stale", "verify": "memory refreshed", "need_user": "Update Claude memory", "rec": "User"},
    {"id": "PEND-028", "pri": "P1", "cat": "gates", "title": "Gates not 7/7", "verify": "gates_passing==7", "need_user": "LIVE OFF until 7/7", "rec": "Close blockers"},
    {"id": "PEND-029", "pri": "P1", "cat": "dhan_parity", "title": "Full Dhan parity FAIL", "verify": "same-session Dhan match", "need_user": "Keep Dhan open", "rec": "Close chain gaps"},
    {"id": "PEND-030", "pri": "P2", "cat": "laptop", "title": "Wrong Cursor path", "verify": "primary clone open", "need_user": "Open primary path", "rec": "User"},
    {"id": "PEND-031", "pri": "P0", "cat": "multibagger", "title": "Multibagger 0 candidates", "verify": "candidates>0 or Delayed honest", "need_user": "None", "rec": "Research pipeline"},
    {"id": "PEND-032", "pri": "P1", "cat": "paper", "title": "Manual Dhan book vs paper separate", "verify": "broker vs paper snaps", "need_user": "None", "rec": "Keep separate truth"},
]


def http_get(path: str) -> tuple[int | None, Any, str]:
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "system3-pending-tracker/1"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = int(resp.status)
            try:
                return code, json.loads(raw), raw[:200]
            except json.JSONDecodeError:
                return code, None, raw[:200]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return int(e.code), None, body
    except Exception as e:  # noqa: BLE001
        return None, None, str(e)[:200]


def probe_live() -> dict[str, Any]:
    deploy_c, deploy, _ = http_get("/api/deploy_info")
    broker_c, broker, _ = http_get("/api/broker/status")
    gates_c, gates, _ = http_get("/api/auto_gates")
    paper_c, paper, _ = http_get("/api/paper")
    ml_c, ml, _ = http_get("/api/ml/performance")
    sig_c, sig, _ = http_get("/api/signals")
    sch_c, sch, _ = http_get("/api/scheduler/health")
    hold_c, _, _ = http_get("/api/holdings")
    funds_c, _, _ = http_get("/api/funds")
    charts_c, _, _ = http_get("/api/charts/NIFTY")
    pred_c, _, _ = http_get("/api/predictions")
    mb_c, _, _ = http_get("/api/multibagger")
    paper_trades_c, _, _ = http_get("/api/paper/trades")
    chain_c, chain, _ = http_get("/api/chain/NIFTY")

    serving = ""
    if isinstance(deploy, dict):
        serving = str(deploy.get("git_sha") or "")

    proof_gates = {}
    if isinstance(gates, dict):
        for g in gates.get("proof_gates") or []:
            if isinstance(g, dict) and g.get("gate_id"):
                proof_gates[str(g["gate_id"])] = bool(g.get("pass"))
        # also map from gates dict
        gmap = gates.get("gates") or {}
        if isinstance(gmap, dict):
            for gid, gval in gmap.items():
                if isinstance(gval, dict) and "pass" in gval:
                    proof_gates[str(gid)] = bool(gval.get("pass"))

    paper_open = None
    paper_trades = None
    if isinstance(paper, dict):
        pos = paper.get("positions") or {}
        if isinstance(pos, dict):
            paper_open = pos.get("open_count")
            msg = str(pos.get("message") or "")
        else:
            msg = ""
        pnl = ((paper.get("pnl") or {}).get("summary") or {}) if isinstance(paper.get("pnl"), dict) else {}
        paper_trades = pnl.get("total_trades")
    else:
        msg = ""

    return {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "base": BASE,
        "serving_sha": serving,
        "deploy_http": deploy_c,
        "broker_http": broker_c,
        "broker_connected": bool(isinstance(broker, dict) and broker.get("connected")),
        "broker_auth": (broker or {}).get("auth_classification") if isinstance(broker, dict) else None,
        "broker_secret_version": ((broker or {}).get("token_proof") or {}).get("secret_version") if isinstance(broker, dict) else None,
        "live_trading_enabled": bool(isinstance(deploy, dict) and deploy.get("live_trading_enabled")),
        "gates_http": gates_c,
        "gates_passing": (gates or {}).get("gates_passing") if isinstance(gates, dict) else None,
        "gates_total": (gates or {}).get("gates_total") if isinstance(gates, dict) else None,
        "trade_ready": (gates or {}).get("trade_ready") if isinstance(gates, dict) else None,
        "proof_gates": proof_gates,
        "paper_http": paper_c,
        "paper_open_count": paper_open,
        "paper_total_trades": paper_trades,
        "paper_positions_message": msg if "msg" in locals() else "",
        "ml_http": ml_c,
        "ml_predictions": ((((ml or {}).get("performance") or {}).get("models") or {}).get("model_accuracy_report") or {}).get("total_predictions") if isinstance(ml, dict) else None,
        "signals_http": sig_c,
        "signals_action": (sig or {}).get("action") if isinstance(sig, dict) else None,
        "scheduler_http": sch_c,
        "scheduler_healthy": (sch or {}).get("healthy") if isinstance(sch, dict) else None,
        "holdings_http": hold_c,
        "funds_http": funds_c,
        "charts_http": charts_c,
        "predictions_http": pred_c,
        "multibagger_http": mb_c,
        "paper_trades_http": paper_trades_c,
        "chain_http": chain_c,
        "chain_spot": (chain or {}).get("spot") if isinstance(chain, dict) else None,
        "chain_contracts": len((chain or {}).get("contracts") or []) if isinstance(chain, dict) else None,
    }


def classify(row: dict[str, str], live: dict[str, Any]) -> tuple[str, str]:
    """Return (status, live_proof). OPEN/WATCH/DONE/IN_PROGRESS."""
    iid = row["id"]
    pg = live.get("proof_gates") or {}

    if iid == "PEND-001":
        # Cannot know main SHA without git; mark OPEN if serving present (lag tracked externally)
        sha = (live.get("serving_sha") or "")[:7]
        return "OPEN", f"serving={sha or 'unknown'} (compare origin/main in session)"
    if iid == "PEND-002":
        ok = live.get("scheduler_healthy") is True
        return ("DONE" if ok else "OPEN"), f"healthy={live.get('scheduler_healthy')} http={live.get('scheduler_http')}"
    if iid == "PEND-003":
        ok = live.get("broker_connected") and live.get("broker_auth") == "AUTH_OK"
        return ("WATCH" if ok else "OPEN"), f"connected={live.get('broker_connected')} auth={live.get('broker_auth')} v={live.get('broker_secret_version')}"
    if iid in {"PEND-004", "PEND-005", "PEND-006", "PEND-007", "PEND-008", "PEND-009"}:
        return "IN_PROGRESS", "UI fix landed locally; DONE only after serving SHA re-snap"
    if iid == "PEND-011":
        ok = live.get("holdings_http") == 200 and live.get("funds_http") == 200
        return ("DONE" if ok else "OPEN"), f"holdings={live.get('holdings_http')} funds={live.get('funds_http')}"
    if iid == "PEND-012":
        ok = live.get("charts_http") == 200
        return ("DONE" if ok else "OPEN"), f"charts={live.get('charts_http')}"
    if iid == "PEND-013":
        ok = live.get("predictions_http") == 200 and live.get("multibagger_http") == 200
        return ("DONE" if ok else "OPEN"), f"predictions={live.get('predictions_http')} multibagger={live.get('multibagger_http')}"
    if iid == "PEND-014":
        open_c = live.get("paper_open_count")
        msg = str(live.get("paper_positions_message") or "")
        if open_c and int(open_c) > 0:
            return "DONE", f"open_count={open_c}"
        if "not found" in msg.lower():
            return "OPEN", msg
        return "OPEN", f"open_count={open_c} msg={msg[:80]}"
    if iid == "PEND-016":
        ok = live.get("paper_trades_http") == 200
        return ("DONE" if ok else "OPEN"), f"paper/trades={live.get('paper_trades_http')}"
    if iid == "PEND-017":
        ok = pg.get("REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF") is True
        return ("DONE" if ok else "OPEN"), f"pass={pg.get('REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF')}"
    if iid == "PEND-018":
        ok = pg.get("POSITIVE_NET_EXPECTANCY_AFTER_COSTS") is True
        return ("DONE" if ok else "OPEN"), f"pass={pg.get('POSITIVE_NET_EXPECTANCY_AFTER_COSTS')}"
    if iid == "PEND-019":
        ok = pg.get("ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS") is True
        return ("DONE" if ok else "OPEN"), f"pass={pg.get('ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS')}"
    if iid == "PEND-020":
        preds = live.get("ml_predictions")
        if preds is not None and int(preds) > 0:
            return "DONE", f"total_predictions={preds}"
        return "OPEN", f"total_predictions={preds}"
    if iid == "PEND-021":
        act = str(live.get("signals_action") or "")
        if act and act not in {"NO_TRADE"} and "not found" not in act.lower():
            return "WATCH", f"action={act}"
        return "OPEN", f"action={act} http={live.get('signals_http')}"
    if iid == "PEND-023":
        ok = pg.get("WEBSOCKET_TICK_HEALTH_PROVEN") is True
        return ("DONE" if ok else "OPEN"), f"pass={pg.get('WEBSOCKET_TICK_HEALTH_PROVEN')}"
    if iid == "PEND-024":
        ok = pg.get("OPTION_STRIKE_VISIBILITY_PROVEN") is True
        return ("DONE" if ok else "OPEN"), f"pass={pg.get('OPTION_STRIKE_VISIBILITY_PROVEN')}"
    if iid == "PEND-028":
        gp, gt = live.get("gates_passing"), live.get("gates_total")
        if gp is not None and gt is not None and int(gp) == int(gt):
            return "DONE", f"gates={gp}/{gt}"
        return "OPEN", f"gates={gp}/{gt} trade_ready={live.get('trade_ready')}"
    if iid == "PEND-025":
        return "WATCH", "public_readonly until user decides"
    if iid in {"PEND-027", "PEND-030"}:
        return "OPEN", "user action required"
    if iid == "PEND-003":
        return "WATCH", "broker watch"
    # default open
    return "OPEN", "awaiting implementation/proof"


def write_outputs(live: dict[str, Any], rows: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / "TRACKING_CHECKLIST.md"
    json_path = OUT_DIR / "TRACKING_CHECKLIST.json"
    csv_path = OUT_DIR / "session_issues_master.csv"

    open_n = sum(1 for r in rows if r["status"] == "OPEN")
    prog_n = sum(1 for r in rows if r["status"] == "IN_PROGRESS")
    done_n = sum(1 for r in rows if r["status"] == "DONE")
    watch_n = sum(1 for r in rows if r["status"] == "WATCH")
    p0_open = sum(1 for r in rows if r["pri"] == "P0" and r["status"] in {"OPEN", "IN_PROGRESS"})

    lines = [
        "# System3 TRACKING CHECKLIST (live — overwrite only)",
        "",
        f"**Updated UTC:** `{live['captured_utc']}`  ",
        f"**Base:** `{live['base']}`  ",
        f"**Serving SHA:** `{live.get('serving_sha') or 'unknown'}`  ",
        f"**Broker:** connected={live.get('broker_connected')} auth={live.get('broker_auth')} secret_v={live.get('broker_secret_version')}  ",
        f"**Gates:** {live.get('gates_passing')}/{live.get('gates_total')} trade_ready={live.get('trade_ready')}  ",
        f"**Scheduler healthy:** {live.get('scheduler_healthy')}  ",
        f"**LIVE trading:** {live.get('live_trading_enabled')}  ",
        "",
        f"**Counts:** OPEN={open_n} IN_PROGRESS={prog_n} WATCH={watch_n} DONE={done_n} · **P0 active={p0_open}**",
        "",
        "> This file is **replaced** on every tracker run. Do not create dated duplicate tracking logs.",
        "> Catalog/solutions: `docs/handoffs/SESSION_ISSUES_MASTER.md` · Runbook §0A/§10/§11",
        "",
        "## Checklist",
        "",
        "| ID | Pri | Status | Title | Live proof | Need from user | Recommendation |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['pri']} | **{r['status']}** | {r['title']} | {r['live_proof'][:120]} | {r['need_user']} | {r['rec']} |"
        )

    lines.extend(
        [
            "",
            "## Endpoint proof snapshot",
            "",
            f"- holdings={live.get('holdings_http')} funds={live.get('funds_http')} charts={live.get('charts_http')} predictions={live.get('predictions_http')} multibagger={live.get('multibagger_http')}",
            f"- paper={live.get('paper_http')} paper/trades={live.get('paper_trades_http')} open_count={live.get('paper_open_count')} total_trades={live.get('paper_total_trades')}",
            f"- chain/NIFTY={live.get('chain_http')} spot={live.get('chain_spot')} contracts={live.get('chain_contracts')}",
            f"- signals action={live.get('signals_action')} ml_predictions={live.get('ml_predictions')}",
            "",
            "## Agent next",
            "",
            "1. Read this file first every session",
            "2. Work highest P0 OPEN/IN_PROGRESS",
            "3. After deploy: re-run `python scripts/system3_pending_tracker_refresh.py`",
            "4. Re-snap UI; mark DONE only with serving proof",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    payload = {"live": live, "rows": rows, "counts": {"open": open_n, "in_progress": prog_n, "watch": watch_n, "done": done_n, "p0_active": p0_open}}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["issue_id", "priority", "category", "title", "status", "live_proof", "need_from_user", "recommendation", "verify", "serving_sha", "updated_utc"],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "issue_id": r["id"],
                    "priority": r["pri"],
                    "category": r["cat"],
                    "title": r["title"],
                    "status": r["status"],
                    "live_proof": r["live_proof"],
                    "need_from_user": r["need_user"],
                    "recommendation": r["rec"],
                    "verify": r["verify"],
                    "serving_sha": live.get("serving_sha") or "",
                    "updated_utc": live["captured_utc"],
                }
            )

    # Mirror under reports/latest/tracking WITHOUT dated names (overwrite)
    mirror = ROOT / "reports" / "latest" / "tracking"
    mirror.mkdir(parents=True, exist_ok=True)
    (mirror / "TRACKING_CHECKLIST.md").write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    (mirror / "TRACKING_CHECKLIST.json").write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"WROTE {md_path}")
    print(f"WROTE {json_path}")
    print(f"WROTE {csv_path}")
    print(f"OPEN={open_n} IN_PROGRESS={prog_n} DONE={done_n} P0_ACTIVE={p0_open}")


def main() -> int:
    live = probe_live()
    rows: list[dict[str, str]] = []
    for item in CATALOG:
        status, proof = classify(item, live)
        rows.append({**item, "status": status, "live_proof": proof})
    write_outputs(live, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
