"""
System3 Ultra - Phase 38: Ultra Governance Summary

Build a "board-level" one-pager summarizing:
- Ultra vs Baseline performance
- Risk status
- Promotion readiness
- Open issues

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 101
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def _load_comparison_summary() -> Optional[str]:
    """Load Phase 32 summary MD."""
    summary_md = ULTRA_DIR / "phase32_ultra_vs_baseline_summary.md"
    if summary_md.exists():
        try:
            return summary_md.read_text(encoding="utf-8")
        except Exception:
            pass
    return None


def _load_promotion_plan() -> Optional[Dict[str, Any]]:
    """Load Phase 33 promotion plan."""
    plan_json = ULTRA_DIR / "phase33_promotion_plan.json"
    if plan_json.exists():
        try:
            with plan_json.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def _load_audit_results() -> Optional[pd.DataFrame]:
    """Load Phase 35 audit results."""
    audit_csv = ULTRA_DIR / "phase35_decision_audit.csv"
    if not audit_csv.exists():
        return None
    try:
        return pd.read_csv(audit_csv)
    except Exception:
        return None


def _load_policy_dashboard() -> Optional[str]:
    """Load Phase 37 policy dashboard."""
    dashboard_md = ULTRA_DIR / "phase37_policy_risk_dashboard.md"
    if dashboard_md.exists():
        try:
            return dashboard_md.read_text(encoding="utf-8")
        except Exception:
            pass
    return None


def run_phase38_governance_summary() -> str:
    """
    Run Phase 38: Ultra Governance Summary.

    Returns:
        Path to governance summary MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 38: ULTRA GOVERNANCE SUMMARY ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load all inputs
    comparison_summary = _load_comparison_summary()
    promotion_plan = _load_promotion_plan()
    df_audit = _load_audit_results()
    policy_dashboard = _load_policy_dashboard()

    print("[LOAD] Loading governance inputs...")
    if comparison_summary:
        print("  - Comparison summary: ✓")
    if promotion_plan:
        print("  - Promotion plan: ✓")
    if df_audit is not None:
        print("  - Audit results: ✓")
    if policy_dashboard:
        print("  - Policy dashboard: ✓")

    # Generate governance summary
    summary_md = ULTRA_DIR / "phase38_governance_summary.md"
    with summary_md.open("w", encoding="utf-8") as f:
        f.write("# Ultra Governance Summary\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
        f.write("## Executive Summary\n\n")
        f.write("This document provides a board-level overview of Ultra system status, ")
        f.write("performance, risk, and promotion readiness.\n\n")

        # Section 1: Performance
        f.write("## Section 1: Performance\n\n")
        if comparison_summary:
            # Extract key metrics from summary
            f.write("### Ultra vs Baseline Performance\n\n")
            f.write("See detailed comparison in Phase 32 summary.\n\n")
            f.write("**Key Metrics**:\n")
            f.write("- Comparison data available\n")
            f.write("- Detailed metrics in `phase32_ultra_vs_baseline_summary.md`\n\n")
        else:
            f.write("**Status**: No comparison data available. Run Phase 32 first.\n\n")

        # Section 2: Risk
        f.write("## Section 2: Risk Status\n\n")
        if df_audit is not None and not df_audit.empty:
            status_counts = df_audit["status"].value_counts()
            ok_count = status_counts.get("OK", 0)
            warn_count = status_counts.get("WARN", 0)
            block_count = status_counts.get("BLOCK", 0)

            f.write("### Decision Audit Results\n\n")
            f.write(f"- **OK**: {ok_count} decisions\n")
            f.write(f"- **WARN**: {warn_count} decisions\n")
            f.write(f"- **BLOCK**: {block_count} decisions\n\n")

            if block_count > 0:
                f.write("⚠️ **RISK ALERT**: {block_count} decisions are BLOCKED and should not be executed.\n\n")
            elif warn_count > 0:
                f.write("⚠️ **CAUTION**: {warn_count} decisions have warnings and should be reviewed.\n\n")
            else:
                f.write("✅ **RISK STATUS**: All decisions are OK.\n\n")
        else:
            f.write("**Status**: No audit results available. Run Phase 35 first.\n\n")

        # Section 3: Promotion Readiness
        f.write("## Section 3: Promotion Readiness\n\n")
        if promotion_plan:
            eligible_count = sum(1 for p in promotion_plan.values() if p.get("eligible", False))
            total_count = len(promotion_plan)

            f.write(f"**Eligible for Promotion**: {eligible_count}/{total_count} underlyings\n\n")

            if eligible_count > 0:
                f.write("### Eligible Underlyings\n\n")
                for underlying, plan in promotion_plan.items():
                    if plan.get("eligible", False):
                        f.write(f"- **{underlying}**: Eligible\n")
                        f.write(f"  - Reason: {plan.get('reason', 'N/A')}\n")
                        f.write(f"  - Recommended changes: {', '.join(plan.get('recommended_changes', []))}\n\n")

                f.write("### Recommendation\n\n")
                f.write("**PROMOTION POSSIBLE AFTER**:\n")
                f.write("1. Manual review of eligible underlyings\n")
                f.write("2. Verification of Ultra performance metrics\n")
                f.write("3. 7-day monitoring period\n")
                f.write("4. Explicit manual approval\n\n")
            else:
                f.write("### Recommendation\n\n")
                f.write("**DO NOT PROMOTE YET**\n\n")
                f.write("Ultra does not meet promotion criteria for any underlying.\n\n")
        else:
            f.write("**Status**: No promotion plan available. Run Phase 33 first.\n\n")
            f.write("### Recommendation\n\n")
            f.write("**DO NOT PROMOTE YET**\n\n")
            f.write("Insufficient data to evaluate promotion readiness.\n\n")

        # Open Issues
        f.write("## Section 4: Open Issues\n\n")
        issues = []

        if not comparison_summary:
            issues.append("Phase 32 comparison not run - performance data unavailable")
        if not promotion_plan:
            issues.append("Phase 33 promotion plan not generated")
        if df_audit is None or df_audit.empty:
            issues.append("Phase 35 audit not run - risk assessment unavailable")
        if df_audit is not None and not df_audit.empty:
            block_count = len(df_audit[df_audit["status"] == "BLOCK"])
            if block_count > 0:
                issues.append(f"{block_count} decisions are BLOCKED and require attention")

        if issues:
            f.write("**Open Issues**:\n\n")
            for i, issue in enumerate(issues, 1):
                f.write(f"{i}. {issue}\n")
        else:
            f.write("**No open issues identified.**\n")
        f.write("\n")

        # Final Recommendation
        f.write("## Final Recommendation\n\n")
        if promotion_plan:
            eligible_count = sum(1 for p in promotion_plan.values() if p.get("eligible", False))
            if eligible_count > 0:
                f.write("**STATUS**: PROMOTION POSSIBLE AFTER CONDITIONS MET\n\n")
                f.write("Ultra shows promise but requires:\n")
                f.write("- Manual review and approval\n")
                f.write("- 7-day monitoring period\n")
                f.write("- Explicit confirmation before any changes\n")
            else:
                f.write("**STATUS**: DO NOT PROMOTE YET\n\n")
                f.write("Ultra does not meet promotion criteria. Continue monitoring.\n")
        else:
            f.write("**STATUS**: INSUFFICIENT DATA\n\n")
            f.write("Run Phases 32, 33, and 35 to generate promotion readiness assessment.\n")

        f.write("\n---\n\n")
        f.write("**Note**: This summary is read-only. No automatic promotion or config changes have occurred.\n")

    print(f"[SAVE] Governance summary saved to: {summary_md}")
    print("\n[OK] Phase 38 Ultra Governance Summary completed")
    return str(summary_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase38_governance_summary()
        print(f"\n[PHASE 38] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 38][ERROR] {e}")
        error_path = ULTRA_DIR / "phase38_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 38 Error\n\n{str(e)}\n")
        print(f"[PHASE 38] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
