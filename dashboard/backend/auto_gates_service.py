"""
Auto gates service — production-grade prediction/profit/lifecycle blocker truth for dashboard API.
"""

from __future__ import annotations

import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
GATES_JSON = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
FRICTION_JSON = ROOT / "reports" / "latest" / "friction_expectancy" / "summary.json"
VIABILITY_JSON = ROOT / "reports" / "latest" / "production_viability_bridge" / "latest.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _proof_gates_from_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapt evaluator gates for UI without inventing PASS states.

    The evaluator is the authority.  Notes may be made more readable here, but
    no heuristic, missing value or PAPER-mode convenience may turn a failed
    evaluator gate into PASS.
    """
    gates = payload.get("gates") or {}
    mapping = [
        ("ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS", "ML Accuracy (Spearman ρ)"),
        ("POSITIVE_NET_EXPECTANCY_AFTER_COSTS", "Profit / Expectancy"),
        ("REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF", "Paper Lifecycle"),
        ("WEBSOCKET_TICK_HEALTH_PROVEN", "Tick / Data Freshness"),
        ("MODEL_ACCURACY_REPORT_PRESENT", "Model Accuracy Report"),
        ("OPTION_STRIKE_VISIBILITY_PROVEN", "Option Strike Visibility"),
        ("EQUITY_FO_ELIGIBILITY_PROVEN", "Equity F&O Eligibility"),
    ]
    out: List[Dict[str, Any]] = []
    for gid, label in mapping:
        g = gates.get(gid) or {}
        ok = g.get("pass") is True

        if gid == "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS":
            days_rec = g.get("days_recorded", 0)
            days_req = g.get("days_required", 5)
            rho = g.get("latest_rho", "?")
            threshold = g.get("threshold", 0.7)
            note = f"{days_rec}/{days_req} days · ρ={rho} · need ≥{threshold}"
        elif gid == "POSITIVE_NET_EXPECTANCY_AFTER_COSTS":
            exp = g.get("net_expectancy_after_costs")
            wr = g.get("win_rate")
            note = f"expectancy={exp} · win_rate={wr}"
        elif gid == "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF":
            full = bool(g.get("full_lifecycle_proven"))
            broker = bool(g.get("broker_connected"))
            note = (
                "market-session lifecycle proof collected"
                if full
                else f"proof pending · broker_connected={str(broker).lower()}"
            )
        elif gid == "WEBSOCKET_TICK_HEALTH_PROVEN":
            tick_age = g.get("last_tick_age_sec")
            refresh = g.get("refresh_interval_sec")
            note = (
                f"tick_age={tick_age}s · refresh={refresh}s"
                if tick_age is not None
                else f"tick evidence pending · refresh={refresh}"
            )
        else:
            note = g.get("auto_action") or "Evaluator evidence pending"

        out.append(
            {
                "name": label,
                "gate_id": gid,
                "label": label,
                "status": "PASS" if ok else "COLLECTING",
                "pass": ok,
                "ok": ok,
                "note": note,
                "blocker_id": g.get("blocker_id"),
                "days_recorded": g.get("days_recorded"),
                "days_required": g.get("days_required"),
                "latest_rho": g.get("latest_rho"),
                "days_passing_threshold": g.get("days_passing_threshold"),
            }
        )
    return out


def build_auto_gates_report(
    refresh: bool = False,
    live_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Pure snapshot read. Compatibility arguments never generate evidence."""
    from scripts.system3_gate_evaluator import GATE_IDS

    payload = _read(GATES_JSON) or {}
    if not isinstance(payload, dict):
        payload = {}
    manifest = payload.get('snapshot_manifest') or {}
    if not isinstance(manifest, dict):
        manifest = {}
    evidence = {k: v for k, v in payload.items() if k != 'snapshot_manifest'}
    reason = None
    age = None
    try:
        digest = hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()
        if manifest.get('schema_version') != 1 or manifest.get('payload_sha256') != digest or manifest.get('snapshot_id') != digest:
            reason = 'SNAPSHOT_INTEGRITY_NOT_PROVEN'
        elif manifest.get('producer') != 'scripts/system3_gate_evaluator.py':
            reason = 'SNAPSHOT_PRODUCER_NOT_PROVEN'
        stamp = datetime.fromisoformat(str(manifest.get('generated_at') or '').replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('Timezone missing')
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        if age < 0 or age > 300:
            reason = 'SNAPSHOT_STALE_OR_FUTURE'
    except (ValueError, TypeError, OverflowError):
        reason = 'SNAPSHOT_INVALID_OR_MISSING'
    raw_gates = evidence.get('gates')
    if not isinstance(raw_gates, dict) or set(raw_gates) != set(GATE_IDS):
        reason = reason or 'SNAPSHOT_GATE_SET_INCOMPLETE'
    if reason:
        gates = {gid: {'gate_id': gid, 'pass': False, 'status': 'UNKNOWN', 'blocker_id': reason} for gid in GATE_IDS}
    else:
        gates = {}
        for gid in GATE_IDS:
            row = raw_gates[gid]
            if not isinstance(row, dict):
                row = {}
            gates[gid] = {**row, 'gate_id': gid, 'pass': row.get('pass') is True}
    proof = _proof_gates_from_payload({'gates': gates})
    for row in proof:
        if reason:
            row['status'] = 'UNKNOWN'
    passing = sum(row['pass'] is True for row in gates.values())
    blockers = sorted({row.get('blocker_id') or gid for gid, row in gates.items() if row['pass'] is not True})
    return {
        'generated_utc': manifest.get('generated_at'),
        'observed_at': _utc(),
        'data_asof': evidence.get('data_asof'),
        'source': 'local_gate_snapshot', 'evidence_plane': 'local_reports',
        'snapshot_id': manifest.get('snapshot_id'),
        'ssot_version': manifest.get('snapshot_id'),
        'snapshot_sha256': manifest.get('payload_sha256'),
        'snapshot_manifest': manifest,
        'snapshot_age_sec': age,
        'status': 'UNKNOWN' if reason else 'ok',
        'stale': bool(reason), 'stale_reason': reason,
        'runtime_driven': False,
        'gates': gates, 'proof_gates': proof,
        'gates_passing': passing, 'gates_total': len(GATE_IDS),
        'open_blockers': blockers,
        'trade_ready': not reason and passing == len(GATE_IDS),
        'analyzer_ready': not reason and evidence.get('analyzer_ready') is True,
        'prediction_accuracy_blocked': not gates[GATE_IDS[0]]['pass'],
        'profit_blocked': not gates['POSITIVE_NET_EXPECTANCY_AFTER_COSTS']['pass'],
        'lifecycle_blocked': not gates['REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF']['pass'],
        'technical_gates_still_required': [gid for gid, row in gates.items() if not row['pass']],
        'recommended_auto_actions': evidence.get('recommended_auto_actions') or [],
        'production_live_ready': False,
        'live_trading_enabled': False, 'order_placement_allowed': False,
        'permanent_safety': ['LIVE_TRADING_DISABLED_BY_DESIGN'],
    }
