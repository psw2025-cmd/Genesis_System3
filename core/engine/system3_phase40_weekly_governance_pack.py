"""
System3 Ultra - Phase 40: Weekly Ultra vs Baseline Governance Pack

Aggregate a full week of outputs into one weekly pack for manual review (no automation changes).

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 103
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
WEEKLY_PACKS_DIR = ULTRA_DIR / "weekly_packs"
LOGS_ULTRA_DIR = PROJECT_ROOT / "storage" / "logs_ultra"

WEEKLY_PACKS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_ULTRA_DIR / "system3_phases_39_45.log"


def _log(message: str) -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Phase40] {message}\n"
    print(f"[Phase40] {message}")

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Phase40][WARN] Failed to write log: {e}")


def _get_iso_week(date: datetime) -> str:
    """Get ISO week string (YYYY-WW)."""
    iso_year, iso_week, _ = date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _find_files_last_7_days(base_path: Path, pattern: str) -> List[Path]:
    """Find files matching pattern modified in last 7 days."""
    cutoff = datetime.now() - timedelta(days=7)
    files = []

    if not base_path.exists():
        return files

    for file_path in base_path.glob(pattern):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime >= cutoff:
                files.append(file_path)
        except Exception:
            continue

    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def _aggregate_metrics() -> Dict[str, Any]:
    """Aggregate metrics from last 7 days."""
    metrics = {"comparisons": 0, "audits": 0, "shadow_summaries": 0, "governance_summaries": 0, "policy_dashboards": 0}

    # Find comparison files
    comparison_files = _find_files_last_7_days(ULTRA_DIR, "phase32_ultra_vs_baseline_comparison.csv")
    metrics["comparisons"] = len(comparison_files)

    # Find audit files
    audit_files = _find_files_last_7_days(ULTRA_DIR, "phase35_decision_audit.csv")
    metrics["audits"] = len(audit_files)

    # Find shadow campaign summaries
    shadow_summaries = _find_files_last_7_days(ULTRA_DIR, "phase39_shadow_campaign_summary_*.md")
    metrics["shadow_summaries"] = len(shadow_summaries)

    # Find governance summaries
    gov_summaries = _find_files_last_7_days(ULTRA_DIR, "phase38_governance_summary.md")
    metrics["governance_summaries"] = len(gov_summaries)

    # Find policy dashboards
    policy_dashboards = _find_files_last_7_days(ULTRA_DIR, "phase37_policy_risk_dashboard.md")
    metrics["policy_dashboards"] = len(policy_dashboards)

    return metrics


def _read_latest_comparison() -> Optional[Dict[str, Any]]:
    """Read latest comparison summary."""
    summary_file = ULTRA_DIR / "phase32_ultra_vs_baseline_summary.md"
    if summary_file.exists():
        try:
            content = summary_file.read_text(encoding="utf-8")
            # Extract key metrics (simple parsing)
            return {"file": str(summary_file), "content_preview": content[:500]}
        except Exception:
            pass
    return None


def _read_latest_audit() -> Optional[Dict[str, Any]]:
    """Read latest audit results."""
    audit_file = ULTRA_DIR / "phase35_decision_audit.csv"
    if audit_file.exists():
        try:
            df = pd.read_csv(audit_file)
            ok_count = len(df[df["audit_status"] == "OK"])
            warn_count = len(df[df["audit_status"] == "WARN"])
            block_count = len(df[df["audit_status"] == "BLOCK"])
            return {"total": len(df), "ok": ok_count, "warn": warn_count, "block": block_count}
        except Exception:
            pass
    return None


def _read_latest_promotion_plan() -> Optional[Dict[str, Any]]:
    """Read latest promotion plan."""
    plan_file = ULTRA_DIR / "phase33_promotion_plan.json"
    if plan_file.exists():
        try:
            with plan_file.open("r", encoding="utf-8") as f:
                plan = json.load(f)
            eligible = sum(1 for u in plan.values() if isinstance(u, dict) and u.get("eligible", False))
            return {"eligible_count": eligible, "total_underlyings": len(plan)}
        except Exception:
            pass
    return None


def run_phase40_weekly_pack() -> None:
    """Generate weekly governance pack."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 40: WEEKLY GOVERNANCE PACK")
    print("=" * 60)
    print("\n[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Pack is read-only: no promotion, no config changes\n")

    now = datetime.now()
    week_str = _get_iso_week(now)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    _log(f"Collecting files for week {week_str}")

    # Create week directory
    week_dir = WEEKLY_PACKS_DIR / week_str
    week_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate metrics
    metrics = _aggregate_metrics()
    _log(
        f"Found {metrics['comparisons']} comparisons, {metrics['audits']} audits, {metrics['shadow_summaries']} shadow summaries"
    )

    # Read latest data
    comparison_data = _read_latest_comparison()
    audit_data = _read_latest_audit()
    promotion_data = _read_latest_promotion_plan()

    # Build markdown report
    md_lines = []
    md_lines.append(f"# Weekly Ultra Governance Pack - {week_str}")
    md_lines.append("")
    md_lines.append(f"**Week**: {week_str}")
    md_lines.append(f"**Date Range**: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    md_lines.append(f"**Generated**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    md_lines.append("")
    md_lines.append("## Week Summary")
    md_lines.append("")
    md_lines.append(f"- **Comparison Files**: {metrics['comparisons']}")
    md_lines.append(f"- **Audit Files**: {metrics['audits']}")
    md_lines.append(f"- **Shadow Campaign Summaries**: {metrics['shadow_summaries']}")
    md_lines.append(f"- **Governance Summaries**: {metrics['governance_summaries']}")
    md_lines.append(f"- **Policy Dashboards**: {metrics['policy_dashboards']}")
    md_lines.append("")

    md_lines.append("## Ultra vs Baseline Performance Summary")
    md_lines.append("")
    if comparison_data:
        md_lines.append("Latest comparison data available.")
        md_lines.append(f"File: {comparison_data['file']}")
    else:
        md_lines.append("No comparison data found for this week.")
    md_lines.append("")

    md_lines.append("## Shadow Activity Summary")
    md_lines.append("")
    md_lines.append(f"Shadow campaign summaries found: {metrics['shadow_summaries']}")
    md_lines.append("")

    md_lines.append("## Decision Safety Summary")
    md_lines.append("")
    if audit_data:
        md_lines.append(f"- **Total Decisions Audited**: {audit_data['total']}")
        md_lines.append(f"- **OK**: {audit_data['ok']}")
        md_lines.append(f"- **WARN**: {audit_data['warn']}")
        md_lines.append(f"- **BLOCK**: {audit_data['block']}")
    else:
        md_lines.append("No audit data found for this week.")
    md_lines.append("")

    md_lines.append("## Promotion Readiness")
    md_lines.append("")
    if promotion_data:
        md_lines.append(
            f"- **Eligible Underlyings**: {promotion_data['eligible_count']}/{promotion_data['total_underlyings']}"
        )
        if promotion_data["eligible_count"] > 0:
            md_lines.append("- **Note**: Review promotion plan for details.")
    else:
        md_lines.append("No promotion plan data found.")
    md_lines.append("")

    md_lines.append("## Notes")
    md_lines.append("")
    md_lines.append("- This pack is read-only")
    md_lines.append("- No automatic promotion or config changes")
    md_lines.append("- Manual review required for any actions")

    # Write markdown
    md_file = week_dir / "weekly_governance_pack.md"
    with md_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Write metadata JSON
    meta = {
        "week": week_str,
        "date_range": {"start": week_start.strftime("%Y-%m-%d"), "end": week_end.strftime("%Y-%m-%d")},
        "counts": metrics,
        "generated": now.isoformat(),
    }

    meta_file = week_dir / "weekly_governance_pack_meta.json"
    with meta_file.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Write file list
    files_list = []
    if comparison_data:
        files_list.append(comparison_data["file"])
    if audit_data:
        files_list.append(str(ULTRA_DIR / "phase35_decision_audit.csv"))

    files_txt = week_dir / "weekly_governance_pack_files.txt"
    with files_txt.open("w", encoding="utf-8") as f:
        f.write("\n".join(files_list))

    _log(f"Weekly pack written to {md_file}")
    print(f"\n[OK] Phase 40 Weekly Governance Pack completed")
    print(f"[SAVE] Pack saved to: {week_dir}")
    print(f"[SAVE] Markdown: {md_file.name}")
    print(f"[SAVE] Metadata: {meta_file.name}")


def main() -> None:
    """CLI entry point."""
    run_phase40_weekly_pack()


if __name__ == "__main__":
    main()
