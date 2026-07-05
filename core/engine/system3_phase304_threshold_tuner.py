"""
System3 Phase 304 - Dynamic Threshold Tuner (Safe Mode)

Proposes updated BUY/SELL thresholds using Phase 222 + Phases 301-303, but DO NOT change live thresholds automatically.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

THRESHOLD_CANDIDATES_JSON = STORAGE_META / "system3_threshold_candidates.json"
PERFORMANCE_301_JSON = STORAGE_META / "system3_daily_performance_301.json"
REGIME_302_JSON = STORAGE_META / "system3_regime_performance_302.json"
DECAY_303_JSON = STORAGE_META / "system3_edge_decay_profile_303.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_threshold_tuner_304.md"
PROPOSALS_JSON = STORAGE_META / "system3_threshold_proposals_304.json"


def load_json_safe(path: Path) -> Dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def run_phase304(**kwargs) -> Dict[str, Any]:
    """Run Phase 304: Dynamic Threshold Tuner (Safe Mode)."""
    errors = []

    try:
        # Load inputs
        candidates_data = load_json_safe(THRESHOLD_CANDIDATES_JSON)
        perf_301 = load_json_safe(PERFORMANCE_301_JSON)
        regime_302 = load_json_safe(REGIME_302_JSON)
        decay_303 = load_json_safe(DECAY_303_JSON)

        if not candidates_data:
            return {
                "phase": 304,
                "status": "WARN",
                "details": "Threshold candidates not found (run Phase 223 first)",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(PROPOSALS_JSON)},
                "errors": [],
            }

        # Extract candidates
        candidates = candidates_data.get("candidates", [])
        if not candidates:
            candidates = candidates_data.get("thresholds", [])

        if not candidates:
            return {
                "phase": 304,
                "status": "WARN",
                "details": "No threshold candidates available",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(PROPOSALS_JSON)},
                "errors": [],
            }

        # Evaluate each candidate
        evaluated = []
        for candidate in candidates[:20]:  # Limit to first 20
            buy_thr = candidate.get("buy_threshold", 0.0)
            sell_thr = candidate.get("sell_threshold", 0.0)

            # Estimate risk/benefit
            buy_count = candidate.get("buy_count", 0)
            sell_count = candidate.get("sell_count", 0)
            total_count = buy_count + sell_count

            # Get EV from Phase 301 if available
            ev_estimate = 0.0
            hit_rate_estimate = 50.0
            if perf_301:
                global_totals = perf_301.get("global_totals", {})
                if "BUY" in global_totals and "mean_fwd1" in global_totals["BUY"]:
                    ev_estimate = global_totals["BUY"]["mean_fwd1"]
                if "BUY" in global_totals and "hit_rate_fwd1" in global_totals["BUY"]:
                    hit_rate_estimate = global_totals["BUY"]["hit_rate_fwd1"]

            # Safety checks
            is_safe = True
            safety_notes = []

            if total_count > 1000 and ev_estimate < 0.001:
                is_safe = False
                safety_notes.append("High trade count with poor EV")

            if buy_count > 0 and sell_count > 0:
                ratio = buy_count / sell_count if sell_count > 0 else 999
                if ratio > 5 or ratio < 0.2:
                    is_safe = False
                    safety_notes.append(f"Extreme asymmetry: buy/sell ratio = {ratio:.2f}")

            if is_safe:
                evaluated.append(
                    {
                        "buy_threshold": buy_thr,
                        "sell_threshold": sell_thr,
                        "expected_trade_count": total_count,
                        "expected_ev": ev_estimate,
                        "expected_hit_rate": hit_rate_estimate,
                        "safety_notes": safety_notes,
                    }
                )

        # Select 3 candidates: CONSERVATIVE, BALANCED, AGGRESSIVE
        proposals = []

        if evaluated:
            # Sort by trade count
            sorted_candidates = sorted(evaluated, key=lambda x: x["expected_trade_count"])

            # CONSERVATIVE: lowest trade count, good EV
            conservative = min(evaluated, key=lambda x: x["expected_trade_count"])
            conservative["mode"] = "CONSERVATIVE"
            proposals.append(conservative)

            # BALANCED: middle ground
            if len(evaluated) > 1:
                balanced = evaluated[len(evaluated) // 2]
                balanced["mode"] = "BALANCED"
                proposals.append(balanced)

            # AGGRESSIVE: higher trade count, good EV
            aggressive = max(evaluated, key=lambda x: x["expected_trade_count"])
            aggressive["mode"] = "AGGRESSIVE"
            proposals.append(aggressive)

        # Generate report
        report_lines = [
            "# System3 Threshold Tuner Report (Safe Mode)\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "**Note**: These are PROPOSALS only. No live config changes are made.\n\n",
        ]

        for proposal in proposals:
            report_lines.append(f"## {proposal['mode']} Mode\n\n")
            report_lines.append(f"- Buy Threshold: {proposal['buy_threshold']:.3f}\n")
            report_lines.append(f"- Sell Threshold: {proposal['sell_threshold']:.3f}\n")
            report_lines.append(f"- Expected Trade Count: {proposal['expected_trade_count']}\n")
            report_lines.append(f"- Expected EV: {proposal['expected_ev']:.4f}\n")
            report_lines.append(f"- Expected Hit Rate: {proposal['expected_hit_rate']:.1f}%\n")
            if proposal.get("safety_notes"):
                report_lines.append(f"- Safety Notes: {', '.join(proposal['safety_notes'])}\n")
            report_lines.append("\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        json_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "proposals": proposals,
            "note": "These are proposals only. No live config changes are made.",
        }

        with PROPOSALS_JSON.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {
            "phase": 304,
            "status": "OK",
            "details": f"Generated {len(proposals)} threshold proposals (DRY-RUN only)",
            "outputs": {
                "proposals_generated": len(proposals),
                "report_file": str(REPORT_PATH),
                "json_file": str(PROPOSALS_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 304,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(PROPOSALS_JSON)},
            "errors": errors,
        }
