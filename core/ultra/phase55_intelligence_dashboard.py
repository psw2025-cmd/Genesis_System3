"""
System3 Ultra - Phase 55: Ultra Intelligence Dashboard

Comprehensive dashboard combining all Ultra intelligence.
Aggregates metrics from all phases and generates unified view.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 117
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_phase_outputs() -> Dict[str, Any]:
    """Load outputs from all Ultra phases."""
    outputs = {}

    # Phase 31: Fused decisions
    phase31_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if phase31_csv.exists():
        try:
            df = pd.read_csv(phase31_csv)
            outputs["phase31"] = {
                "total_decisions": len(df),
                "actions": df["final_action"].value_counts().to_dict() if "final_action" in df.columns else {},
                "avg_confidence": df["final_confidence"].mean() if "final_confidence" in df.columns else 0.0,
            }
        except Exception:
            pass

    # Phase 35: Audit results
    phase35_csv = ULTRA_DIR / "phase35_decision_audit.csv"
    if phase35_csv.exists():
        try:
            df = pd.read_csv(phase35_csv)
            outputs["phase35"] = {
                "total_audited": len(df),
                "ok_count": len(df[df.get("audit_status", "") == "OK"]) if "audit_status" in df.columns else 0,
                "warn_count": len(df[df.get("audit_status", "") == "WARN"]) if "audit_status" in df.columns else 0,
                "block_count": len(df[df.get("audit_status", "") == "BLOCK"]) if "audit_status" in df.columns else 0,
            }
        except Exception:
            pass

    # Phase 46: Meta fusion
    phase46_csv = OUTPUT_DIR / "phase46_meta_fusion_predictions.csv"
    if phase46_csv.exists():
        try:
            df = pd.read_csv(phase46_csv)
            outputs["phase46"] = {
                "total_meta_predictions": len(df),
                "avg_meta_confidence": df["meta_confidence"].mean() if "meta_confidence" in df.columns else 0.0,
            }
        except Exception:
            pass

    # Phase 47: Confidence vectors
    phase47_csv = OUTPUT_DIR / "phase47_confidence_vector_7d.csv"
    if phase47_csv.exists():
        try:
            df = pd.read_csv(phase47_csv)
            outputs["phase47"] = {
                "vectors_computed": len(df),
                "trends": df["trend"].value_counts().to_dict() if "trend" in df.columns else {},
            }
        except Exception:
            pass

    # Phase 48: Error scan
    phase48_csv = OUTPUT_DIR / "phase48_error_scan_report.csv"
    if phase48_csv.exists():
        try:
            df = pd.read_csv(phase48_csv)
            outputs["phase48"] = {
                "total_errors": len(df[df["error_type"] != "NONE"]) if "error_type" in df.columns else 0,
                "error_types": df["error_type"].value_counts().to_dict() if "error_type" in df.columns else {},
            }
        except Exception:
            pass

    # Phase 49: Risk suggestions
    phase49_json = OUTPUT_DIR / "phase49_risk_suggestions.json"
    if phase49_json.exists():
        try:
            with phase49_json.open("r", encoding="utf-8") as f:
                data = json.load(f)
                outputs["phase49"] = {
                    "suggestions_count": len(data.get("suggestions", [])),
                    "high_priority": sum(1 for s in data.get("suggestions", []) if s.get("priority") == "HIGH"),
                }
        except Exception:
            pass

    # Phase 50: Explanations
    phase50_csv = OUTPUT_DIR / "phase50_prediction_explanations.csv"
    if phase50_csv.exists():
        try:
            df = pd.read_csv(phase50_csv)
            outputs["phase50"] = {
                "total_explanations": len(df),
            }
        except Exception:
            pass

    # Phase 51: Probabilities
    phase51_csv = OUTPUT_DIR / "phase51_probability_distributions.csv"
    if phase51_csv.exists():
        try:
            df = pd.read_csv(phase51_csv)
            outputs["phase51"] = {
                "total_distributions": len(df),
                "avg_prob_buy_ce": df["prob_buy_ce"].mean() if "prob_buy_ce" in df.columns else 0.0,
                "avg_prob_buy_pe": df["prob_buy_pe"].mean() if "prob_buy_pe" in df.columns else 0.0,
                "avg_prob_hold": df["prob_hold"].mean() if "prob_hold" in df.columns else 0.0,
            }
        except Exception:
            pass

    # Phase 53: Monitoring
    phase53_json = OUTPUT_DIR / "phase53_agent_suggestions.json"
    if phase53_json.exists():
        try:
            with phase53_json.open("r", encoding="utf-8") as f:
                data = json.load(f)
                outputs["phase53"] = {
                    "system_status": data.get("health", {}).get("overall_status", "UNKNOWN"),
                    "suggestions_count": len(data.get("suggestions", [])),
                }
        except Exception:
            pass

    return outputs


def generate_dashboard(phase_outputs: Dict[str, Any]) -> str:
    """Generate comprehensive dashboard markdown."""
    md_parts = [
        "# System3 Ultra Intelligence Dashboard\n\n",
        f"**Generated**: {datetime.now().isoformat()}\n\n",
        "## Overview\n\n",
        "This dashboard aggregates intelligence from all Ultra phases (31-55).\n\n",
        "## Phase Metrics\n\n",
    ]

    # Phase 31-38 (Integration & Governance)
    md_parts.append("### Integration & Governance Phases (31-38)\n\n")
    if "phase31" in phase_outputs:
        p31 = phase_outputs["phase31"]
        md_parts.append(f"- **Phase 31 (Decision Fusion)**: {p31.get('total_decisions', 0)} decisions fused\n")
        md_parts.append(f"  - Average confidence: {p31.get('avg_confidence', 0.0):.2%}\n")

    if "phase35" in phase_outputs:
        p35 = phase_outputs["phase35"]
        md_parts.append(f"- **Phase 35 (Decision Auditor)**: {p35.get('total_audited', 0)} decisions audited\n")
        md_parts.append(
            f"  - OK: {p35.get('ok_count', 0)}, WARN: {p35.get('warn_count', 0)}, BLOCK: {p35.get('block_count', 0)}\n"
        )

    # Phase 46-55 (Final Evolution)
    md_parts.append("\n### Final Evolution Phases (46-55)\n\n")

    if "phase46" in phase_outputs:
        p46 = phase_outputs["phase46"]
        md_parts.append(f"- **Phase 46 (Meta Fusion)**: {p46.get('total_meta_predictions', 0)} meta predictions\n")

    if "phase47" in phase_outputs:
        p47 = phase_outputs["phase47"]
        md_parts.append(f"- **Phase 47 (Confidence Vector)**: {p47.get('vectors_computed', 0)} vectors computed\n")
        if p47.get("trends"):
            md_parts.append(f"  - Trends: {', '.join(f'{k}={v}' for k, v in p47['trends'].items())}\n")

    if "phase48" in phase_outputs:
        p48 = phase_outputs["phase48"]
        md_parts.append(f"- **Phase 48 (Error Scanner)**: {p48.get('total_errors', 0)} errors detected\n")

    if "phase49" in phase_outputs:
        p49 = phase_outputs["phase49"]
        md_parts.append(f"- **Phase 49 (Risk Regulator)**: {p49.get('suggestions_count', 0)} suggestions generated\n")
        md_parts.append(f"  - High priority: {p49.get('high_priority', 0)}\n")

    if "phase50" in phase_outputs:
        p50 = phase_outputs["phase50"]
        md_parts.append(
            f"- **Phase 50 (Prediction Explainer)**: {p50.get('total_explanations', 0)} explanations generated\n"
        )

    if "phase51" in phase_outputs:
        p51 = phase_outputs["phase51"]
        md_parts.append(
            f"- **Phase 51 (Probability Engine)**: {p51.get('total_distributions', 0)} distributions computed\n"
        )
        md_parts.append(
            f"  - Avg probabilities: BUY_CE={p51.get('avg_prob_buy_ce', 0.0):.2%}, "
            f"BUY_PE={p51.get('avg_prob_buy_pe', 0.0):.2%}, HOLD={p51.get('avg_prob_hold', 0.0):.2%}\n"
        )

    if "phase53" in phase_outputs:
        p53 = phase_outputs["phase53"]
        md_parts.append(f"- **Phase 53 (Monitoring Agent)**: System status: {p53.get('system_status', 'UNKNOWN')}\n")
        md_parts.append(f"  - Suggestions: {p53.get('suggestions_count', 0)}\n")

    # Summary
    md_parts.append("\n## System Status Summary\n\n")
    total_phases = len(phase_outputs)
    md_parts.append(f"- **Active Phases**: {total_phases}\n")
    md_parts.append(f"- **Dashboard Status**: {'✅ OPERATIONAL' if total_phases > 0 else '⚠️ NO DATA'}\n")

    md_parts.append("\n## Important Notes\n\n")
    md_parts.append("- All Ultra operations are read-only and shadow-only\n")
    md_parts.append("- No baseline modifications are made\n")
    md_parts.append("- All suggestions require manual review and approval\n")
    md_parts.append("- No auto-execution or auto-updates are performed\n")

    return "".join(md_parts)


def run_phase55_intelligence_dashboard() -> None:
    """Run Phase 55: Ultra Intelligence Dashboard."""
    print("=== SYSTEM3 ULTRA - PHASE 55: ULTRA INTELLIGENCE DASHBOARD ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load phase outputs
    print("[LOAD] Aggregating intelligence from all Ultra phases...")
    phase_outputs = load_phase_outputs()

    print(f"[LOAD] Loaded data from {len(phase_outputs)} phases")

    # Generate dashboard
    dashboard_md = generate_dashboard(phase_outputs)

    # Save dashboard
    dashboard_path = OUTPUT_DIR / "phase55_intelligence_dashboard.md"
    with dashboard_path.open("w", encoding="utf-8") as f:
        f.write(dashboard_md)
    print(f"[SAVE] Intelligence dashboard saved to: {dashboard_path}")

    # Save dashboard data JSON
    dashboard_data_json = OUTPUT_DIR / "phase55_dashboard_data.json"
    with dashboard_data_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "phase_outputs": phase_outputs,
                "generated_at": datetime.now().isoformat(),
                "total_phases": len(phase_outputs),
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Dashboard data saved to: {dashboard_data_json}")

    # Summary
    print(f"\n=== INTELLIGENCE DASHBOARD SUMMARY ===")
    print(f"Phases aggregated: {len(phase_outputs)}")
    print(f"\nPhase Status:")
    for phase_name, phase_data in phase_outputs.items():
        print(f"  {phase_name}: ✅ Data available")

    print("\n[OK] Phase 55 Ultra Intelligence Dashboard completed")
    print(f"[NOTE] Dashboard available at: {dashboard_path}")


def main() -> None:
    """Main entry point."""
    run_phase55_intelligence_dashboard()


if __name__ == "__main__":
    main()
