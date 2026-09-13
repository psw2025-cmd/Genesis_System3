#!/usr/bin/env python3
"""
Evaluate prediction-accuracy, profit, and lifecycle gates from on-disk proof artifacts.

Outputs:
  reports/latest/system3_auto_gates/summary.json
  reports/latest/system3_auto_gates/summary.md

Read-only except optional sync of human_approval technical gates (--sync-gates).
"""

from __future__ import annotations

import argparse
import json
import math
import hashlib
import tempfile
import os
import sys
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports" / "latest" / "system3_auto_gates"
SPEARMAN_THRESHOLD = 0.70
SPEARMAN_DAYS_REQUIRED = 5
HUMAN_GATE_PATH = ROOT / "config" / "human_approval_gate.json"

GATE_IDS = [
    "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
    "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
    "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
    "WEBSOCKET_TICK_HEALTH_PROVEN",
    "MODEL_ACCURACY_REPORT_PRESENT",
    "OPTION_STRIKE_VISIBILITY_PROVEN",
    "EQUITY_FO_ELIGIBILITY_PROVEN",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _spearman_from_validation(data: Dict[str, Any]) -> Optional[float]:
    for key in ("rank_correlation_spearman", "spearman_correlation", "spearman_rho", "rho"):
        val = data.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    return None


def load_spearman_days(root: Path) -> Tuple[List[Dict[str, Any]], int, Optional[float]]:
    by_date: Dict[str, Dict[str, Any]] = {}

    def _ingest(data: Dict[str, Any], fallback_date: str = "") -> None:
        if data.get("error") and _spearman_from_validation(data) in (None, 0.0):
            return
        rho = _spearman_from_validation(data)
        if rho is None or not math.isfinite(rho):
            return
        day = str(data.get("date") or fallback_date or "").strip()
        if not day:
            return
        from scripts.system3_option_visibility_audit import BROKER_ACCEPTANCE_REQUIRED
        from core.utils.nse_holidays import HOLIDAYS_BY_YEAR, is_trading_day
        try:
            business_day = date.fromisoformat(day)
        except ValueError:
            return
        coverage = data.get('covered_underlyings')
        valid_coverage = isinstance(coverage, list) and set(BROKER_ACCEPTANCE_REQUIRED).issubset(coverage)
        qualifying = (business_day.year in HOLIDAYS_BY_YEAR and is_trading_day(business_day)[0]
                      and data.get('coverage_complete') is True and valid_coverage
                      and data.get('source') == 'state/gain_rank_history.json'
                      and data.get('status') == 'PASS'
                      and not any(data.get(k) for k in ('is_fixture', 'seeded', 'simulation', 'replay', 'demo')))
        by_date[day] = {
            "date": day,
            "rho": round(rho, 4),
            "hit_rate": data.get("hit_rate", data.get("match_rate_top3")),
            "status": data.get("status") or data.get("grade"),
            "pass": qualifying and rho >= SPEARMAN_THRESHOLD,
            "coverage_qualifying": qualifying,
        }

    mv_dir = root / "state" / "market_validations"
    if mv_dir.exists():
        for path in sorted(mv_dir.glob("*.json")):
            data = _read_json(path)
            if not data:
                continue
            _ingest(data, fallback_date=path.stem.replace("market_validation_", ""))

    days = [by_date[k] for k in sorted(by_date)]
    passing = sum(1 for d in days if d["pass"])
    latest_rho = days[-1]["rho"] if days else None
    return days, passing, latest_rho


def eval_spearman_gate(root: Path, now: Optional[datetime] = None) -> Dict[str, Any]:
    days, passing, latest = load_spearman_days(root)
    from core.utils.nse_holidays import HOLIDAYS_BY_YEAR, is_trading_day
    now = now or datetime.now(timezone.utc)
    ist = now.astimezone(timezone(timedelta(hours=5, minutes=30)))
    expected = ist.date() if (ist.hour, ist.minute) >= (15, 35) else ist.date() - timedelta(days=1)
    def previous_session(day):
        for _ in range(32):
            if day.year not in HOLIDAYS_BY_YEAR:
                return None
            if is_trading_day(day)[0]:
                return day
            day -= timedelta(days=1)
        return None
    expected = previous_session(expected)
    latest_required = expected.isoformat() if expected else None
    consecutive_pass = 0
    by_date = {d['date']: d for d in days}
    while expected is not None:
        record = by_date.get(expected.isoformat())
        if not record or not record['pass']:
            break
        consecutive_pass += 1
        expected = previous_session(expected - timedelta(days=1))
    ok = consecutive_pass >= SPEARMAN_DAYS_REQUIRED
    return {
        "gate_id": "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
        "pass": ok,
        "days_recorded": len(days),
        "days_passing_threshold": passing,
        "days_required": SPEARMAN_DAYS_REQUIRED,
        "threshold": SPEARMAN_THRESHOLD,
        "latest_rho": latest,
        "consecutive_pass_days": consecutive_pass,
        "latest_required_market_day": latest_required,
        "blocker_id": None if ok else "SYS3-BLK-005",
        "auto_action": "Run daily_gain_validate at 15:35 IST weekdays; auto_retrain if rho<0.40 x3 days",
        "days": days[-14:],
    }


def eval_expectancy_gate(root: Path) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "friction_expectancy" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    net = ev.get("net_expectancy_after_costs")
    try:
        net_f = float(net) if net is not None else None
    except (TypeError, ValueError):
        net_f = None
    source = str(data.get("source") or "").replace("\\", "/")
    is_fixture = (
        data.get("is_fixture") is True
        or "tests/fixtures" in source
        or "paper_closed_trades_feb2026" in source
    )
    ok = (
        (not is_fixture)
        and data.get("pass") is True
        and net_f is not None
        and net_f > 0
    )
    blocker = None if ok else ("INSUFFICIENT_REAL_TRADES" if is_fixture else "PROFIT_BLOCKER")
    return {
        "gate_id": "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
        "pass": ok,
        "is_fixture": is_fixture,
        "report_exists": path.exists(),
        "net_expectancy_after_costs": net_f,
        "win_rate": ev.get("win_rate"),
        "trade_count": ev.get("trade_count"),
        "source": source or None,
        "blocker_id": blocker,
        "auto_action": "Run scripts/system3_friction_expectancy_proof.py after paper trades accumulate",
    }


def eval_lifecycle_gate(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "analyzer_paper_lifecycle_proof" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    broker_connected = ev.get("lifecycle_proof_broker_not_connected") is not True
    if live_state:
        broker_connected = bool((live_state.get("broker") or {}).get("connected"))
    full_proven = ev.get("full_lifecycle_proven") is True
    if not full_proven and live_state and broker_connected:
        positions = live_state.get("positions") or []
        if positions and all(
            isinstance(p, dict) and p.get("strike") and p.get("entry_price") and p.get("position_id") for p in positions
        ):
            full_proven = True
    ok = (
        (data.get("pass") is True or full_proven)
        and full_proven
        and ev.get("lifecycle_proof_dry_run") is not True
        and broker_connected
    )
    market_open = bool((live_state or {}).get("market", {}).get("is_open"))
    return {
        "gate_id": "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
        "pass": ok,
        "report_exists": path.exists(),
        "full_lifecycle_proven": full_proven,
        "broker_connected": broker_connected,
        "market_open": market_open,
        "blocker_id": None if ok else "SYS3-BLK-008",
        "auto_action": "Run scripts/paper_lifecycle_proof.py during market hours with broker connected",
    }


def eval_tick_health_gate(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "websocket_tick_health" / "summary.json"
    data = _read_json(path) or {}
    ev = data.get("evidence") or {}
    tick_age = ev.get("last_tick_age_sec")
    refresh = ev.get("refresh_interval_sec")
    broker_ok = ev.get("broker_connected")
    if live_state:
        tick_age = (
            live_state.get("last_tick_age_sec")
            or (live_state.get("tick_health") or {}).get("last_tick_age_sec")
            or tick_age
        )
        refresh = (
            live_state.get("refresh_interval")
            or (live_state.get("tick_health") or {}).get("refresh_interval_sec")
            or refresh
        )
        broker_ok = (live_state.get("broker") or {}).get("connected") if broker_ok is None else broker_ok
    rest_ok = refresh is not None and float(refresh) <= 10
    ok = data.get("pass") is True or (rest_ok and broker_ok and tick_age is not None and float(tick_age) <= 15)
    return {
        "gate_id": "WEBSOCKET_TICK_HEALTH_PROVEN",
        "pass": ok,
        "report_exists": path.exists(),
        "last_tick_age_sec": tick_age,
        "refresh_interval_sec": refresh,
        "blocker_id": None if ok else "TICK_HEALTH_BLOCKER",
        "auto_action": "REST poll ≤10s counts for analyzer; WebSocket stream for live execution",
    }


def eval_model_accuracy_report(root: Path) -> Dict[str, Any]:
    path = root / "reports" / "latest" / "model_accuracy_report.json"
    data = _read_json(path) or {}
    summary = data.get("summary") or {}
    rows = summary.get("rows", 0)
    try:
        rows = int(rows)
    except (TypeError, ValueError):
        rows = 0
    ok = path.exists() and rows > 0
    spearman_days, passing, _ = load_spearman_days(root)
    return {
        "gate_id": "MODEL_ACCURACY_REPORT_PRESENT",
        "pass": ok,
        "report_exists": path.exists(),
        "rows": rows,
        "validation_days": len(spearman_days),
        "spearman_days_passing": passing,
        "blocker_id": None if ok else "SYS3-BLK-005",
        "auto_action": "Run scripts/system3_model_accuracy_tracker.py --api-base $CLOUD",
    }


def eval_option_visibility(root: Path, live_state: Optional[Dict[str, Any]] = None, now: Optional[datetime] = None) -> Dict[str, Any]:
    from scripts.system3_option_visibility_audit import BROKER_ACCEPTANCE_REQUIRED, SUPPORTED_INDEX_UNIVERSE, quote_proof
    js = root / "reports" / "latest" / "option_strike_visibility.json"
    data = _read_json(js) or {}
    rows = data.get('rows') if isinstance(data.get('rows'), list) else []
    proven = {}
    used_ids = set()
    duplicate_ids = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        quote = dict(row)
        quote['security_id'] = row.get('security_id') or row.get('instrument_token')
        quote['option_type'] = row.get('option_type') or row.get('option_side')
        symbol = str(row.get('underlying') or '').upper()
        if row.get('paper_trade_allowed') is not True or quote_proof(quote, now)['quote_status'] != 'PASS':
            continue
        security_id = str(quote['security_id'])
        if security_id in used_ids:
            duplicate_ids.add(security_id)
        used_ids.add(security_id)
        proven[symbol] = security_id
    missing = sorted(set(BROKER_ACCEPTANCE_REQUIRED) - set(proven))
    ok = not missing and not duplicate_ids
    return {
        "gate_id": "OPTION_STRIKE_VISIBILITY_PROVEN",
        "pass": ok,
        "rows": len(rows),
        "paper_trade_allowed_count": len(proven),
        "required_symbols": list(BROKER_ACCEPTANCE_REQUIRED),
        "supported_symbols": list(SUPPORTED_INDEX_UNIVERSE),
        "missing_required_symbols": missing,
        "duplicate_security_ids": sorted(duplicate_ids),
        "blocker_id": None if ok else "SYS3-BLK-003",
        "auto_action": "Run scripts/system3_option_visibility_audit.py",
    }


def eval_equity_fo_gate(root: Path) -> Dict[str, Any]:
    import sys

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from core.brokers.dhan.equity_fo_universe import (
            is_equity_fo_symbol,
            load_equity_fo_universe,
        )

        universe = load_equity_fo_universe()
        count = int(universe.get("underlying_count") or 0)
        ok = count >= 50 and is_equity_fo_symbol("RELIANCE")
    except Exception as exc:
        return {
            "gate_id": "EQUITY_FO_ELIGIBILITY_PROVEN",
            "pass": False,
            "error": str(exc)[:200],
            "blocker_id": "SYS3-BLK-004",
            "auto_action": "Verify security_id_list.csv OPTSTK universe loads",
        }
    return {
        "gate_id": "EQUITY_FO_ELIGIBILITY_PROVEN",
        "pass": ok,
        "underlying_count": count,
        "blocker_id": None if ok else "SYS3-BLK-004",
        "auto_action": "Wire is_tradeable_fo_symbol() in ranking/paper trade path",
    }


def evaluate_all(root: Path, live_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    gates = [
        eval_spearman_gate(root),
        eval_expectancy_gate(root),
        eval_lifecycle_gate(root, live_state),
        eval_tick_health_gate(root, live_state),
        eval_model_accuracy_report(root),
        eval_option_visibility(root, live_state),
        eval_equity_fo_gate(root),
    ]
    open_blockers = sorted({g["blocker_id"] for g in gates if g.get("blocker_id")})
    passing = sum(1 for g in gates if g.get("pass"))
    human = _read_json(HUMAN_GATE_PATH) or {}
    return {
        "generated_utc": _utc(),
        "gates": {g["gate_id"]: g for g in gates},
        "gates_passing": passing,
        "gates_total": len(gates),
        "open_blockers": open_blockers,
        "prediction_accuracy_blocked": not gates[0]["pass"],
        "profit_blocked": not gates[1]["pass"],
        "lifecycle_blocked": not gates[2]["pass"],
        "human_approval": human.get("approved"),
        "live_trading_enabled": False,
        "trade_ready": passing == len(gates),
        "analyzer_ready": passing >= 4,
        "technical_gates_still_required": [
            g["gate_id"]
            for g in gates
            if not g.get("pass")
            and g["gate_id"]
            in (
                "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
                "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
                "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF",
                "WEBSOCKET_TICK_HEALTH_PROVEN",
            )
        ],
        "recommended_auto_actions": [g["auto_action"] for g in gates if not g.get("pass")],
        "permanent_safety": ["LIVE_TRADING_DISABLED_BY_DESIGN"],
    }


def sync_human_technical_gates(root: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Remove cleared technical gates from human_approval_gate.json (never enable live)."""
    path = HUMAN_GATE_PATH
    data = _read_json(path)
    if not data:
        return {"synced": False, "reason": "human_approval_gate.json missing"}
    still_required = payload.get("technical_gates_still_required") or []
    old = list(data.get("technical_gates_still_required") or [])
    data["technical_gates_still_required"] = still_required
    data["live_trading_env_flip_authorized"] = False
    data["gates_synced_utc"] = _utc()
    data["gates_passing"] = payload.get("gates_passing")
    data["gates_total"] = payload.get("gates_total")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    removed = [g for g in old if g not in still_required]
    return {"synced": True, "removed_gates": removed, "still_required": still_required}


def write_reports(root: Path, payload: Dict[str, Any]) -> None:
    out = root / 'reports' / 'latest' / 'system3_auto_gates'
    out.mkdir(parents=True, exist_ok=True)
    # One atomic file contains both evidence and its generation manifest.
    # A reader never observes a new manifest paired with an old payload.
    payload = dict(payload)
    payload.pop('snapshot_manifest', None)
    content = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    digest = hashlib.sha256(content).hexdigest()
    payload['snapshot_manifest'] = {
        'schema_version': 1, 'snapshot_id': digest, 'payload_sha256': digest,
        'generated_at': payload['generated_utc'],
        'producer': 'scripts/system3_gate_evaluator.py',
        'source': 'local_evidence_evaluator',
        'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    fd, temp = tempfile.mkstemp(prefix='.summary-', suffix='.tmp', dir=out)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, out / 'summary.json')
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    lines = [
        "# System3 Auto Gates",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Gates passing: **{payload['gates_passing']}/{payload['gates_total']}**",
        f"Trade ready: **{payload['trade_ready']}**",
        f"Analyzer ready: **{payload['analyzer_ready']}**",
        "",
        "## Gates",
        "",
        "| Gate | Pass | Blocker |",
        "|---|---|---|",
    ]
    for gid, g in payload["gates"].items():
        lines.append(f"| `{gid}` | `{g.get('pass')}` | `{g.get('blocker_id') or '-'}` |")
    lines.extend(["", "## Open blockers", ""])
    for b in payload.get("open_blockers") or []:
        lines.append(f"- `{b}`")
    lines.extend(["", "## Auto actions", ""])
    for a in payload.get("recommended_auto_actions") or []:
        lines.append(f"- {a}")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 gate evaluator")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--sync-gates", action="store_true", help="Sync human_approval technical gates")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = evaluate_all(root)
    if args.sync_gates:
        payload["human_gate_sync"] = sync_human_technical_gates(root, payload)
    write_reports(root, payload)
    print("SYSTEM3_GATE_EVALUATOR_COMPLETE")
    print(
        json.dumps(
            {
                "gates_passing": payload["gates_passing"],
                "trade_ready": payload["trade_ready"],
                "open_blockers": payload["open_blockers"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
