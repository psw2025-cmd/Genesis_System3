"""
System3 Phase 385: Scoring Telemetry

Purpose: Track how often Ultra vs Delta scoring is used in live runs
Outputs: JSON metrics + Markdown report

Safety: DRY-RUN only, read-only log parsing, no live trading
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

# Paths
LOGS_DIR = ROOT_DIR / "logs"
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_logs_for_scoring_telemetry(hours_back: int = 24) -> dict:
    """
    Parse recent logs to count Ultra vs Delta usage.

    Looks for log patterns:
    - "USING_ULTRA_MODEL for NIFTY"
    - "USING_DELTA_FALLBACK for BANKNIFTY"

    Args:
        hours_back: How many hours of logs to analyze

    Returns:
        {
            "ultra_used": 85,
            "delta_fallback": 35,
            "by_underlying": {...}
        }
    """
    telemetry = {"ultra_used": 0, "delta_fallback": 0, "by_underlying": {}}

    if not LOGS_DIR.exists():
        logger.warning(f"Logs directory not found: {LOGS_DIR}")
        return telemetry

    # Find log files from last N hours
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    log_files = []

    for log_file in LOGS_DIR.rglob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime >= cutoff_time:
                log_files.append(log_file)
        except:
            continue

    logger.info(f"Found {len(log_files)} log files from last {hours_back} hours")

    # Parse logs
    ultra_pattern = re.compile(r"USING_ULTRA_MODEL for (\w+)")
    delta_pattern = re.compile(r"USING_DELTA_FALLBACK for (\w+)")

    for log_file in log_files:
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    # Check for Ultra usage
                    ultra_match = ultra_pattern.search(line)
                    if ultra_match:
                        underlying = ultra_match.group(1)
                        telemetry["ultra_used"] += 1
                        if underlying not in telemetry["by_underlying"]:
                            telemetry["by_underlying"][underlying] = {"ultra": 0, "delta": 0}
                        telemetry["by_underlying"][underlying]["ultra"] += 1

                    # Check for Delta fallback
                    delta_match = delta_pattern.search(line)
                    if delta_match:
                        underlying = delta_match.group(1)
                        telemetry["delta_fallback"] += 1
                        if underlying not in telemetry["by_underlying"]:
                            telemetry["by_underlying"][underlying] = {"ultra": 0, "delta": 0}
                        telemetry["by_underlying"][underlying]["delta"] += 1
        except Exception as e:
            logger.warning(f"Could not parse {log_file}: {e}")

    return telemetry


def run_phase_385() -> dict:
    """
    Phase 385: Scoring Path Telemetry

    Counts how many signals used Ultra vs delta fallback in the last N runs.

    Writes:
    - storage/metrics/scoring_telemetry_385.json
    - reports/SCORING_TELEMETRY_385.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 385: SCORING TELEMETRY")
    logger.info("=" * 60)

    try:
        # Parse logs (last 24 hours)
        logger.info("Parsing logs for scoring telemetry...")
        telemetry = parse_logs_for_scoring_telemetry(hours_back=24)

        total_signals = telemetry["ultra_used"] + telemetry["delta_fallback"]
        ultra_percentage = (telemetry["ultra_used"] / total_signals * 100) if total_signals > 0 else 0

        telemetry_metrics = {
            "telemetry_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "period": "last_24_hours",
            "total_signals": total_signals,
            "ultra_used": telemetry["ultra_used"],
            "delta_fallback": telemetry["delta_fallback"],
            "ultra_percentage": round(ultra_percentage, 1),
            "by_underlying": telemetry["by_underlying"],
        }

        # Write JSON metrics
        metrics_file = METRICS_DIR / "scoring_telemetry_385.json"
        with open(metrics_file, "w") as f:
            json.dump(telemetry_metrics, f, indent=2)
        logger.info(f"✓ Metrics written: {metrics_file}")

        # Write Markdown report
        report_file = REPORTS_DIR / "SCORING_TELEMETRY_385.md"
        with open(report_file, "w") as f:
            f.write("# SCORING TELEMETRY (PHASE 385)\n\n")
            f.write(f"**Telemetry Timestamp:** {telemetry_metrics['telemetry_timestamp']}\n")
            f.write(f"**Period:** {telemetry_metrics['period']}\n")
            f.write(f"**Total Signals:** {telemetry_metrics['total_signals']}\n\n")

            f.write("## Usage Statistics\n\n")
            f.write(
                f"- **Ultra Models Used:** {telemetry_metrics['ultra_used']} ({telemetry_metrics['ultra_percentage']:.1f}%)\n"
            )
            f.write(
                f"- **Delta Fallback Used:** {telemetry_metrics['delta_fallback']} ({100-telemetry_metrics['ultra_percentage']:.1f}%)\n\n"
            )

            if telemetry_metrics["by_underlying"]:
                f.write("## Usage by Underlying\n\n")
                f.write("| Underlying | Ultra Used | Delta Fallback | Ultra % |\n")
                f.write("|------------|-----------|----------------|----------|\n")

                for underlying, counts in telemetry_metrics["by_underlying"].items():
                    total_u = counts["ultra"] + counts["delta"]
                    ultra_pct = (counts["ultra"] / total_u * 100) if total_u > 0 else 0
                    f.write(f"| {underlying} | {counts['ultra']} | {counts['delta']} | {ultra_pct:.1f}% |\n")
            else:
                f.write("⚠️ **Note:** No telemetry data found in logs (no scoring activity detected)\n")

            f.write("\n## Summary\n\n")
            if total_signals == 0:
                f.write("⚠️ **Status:** No scoring activity detected in logs\n")
                f.write("\n**Recommendation:** Run signal engine to generate telemetry data\n")
            elif ultra_percentage > 70:
                f.write(f"✅ **Status:** High Ultra model usage ({ultra_percentage:.1f}%)\n")
                f.write("\n**Recommendation:** Proceed to Phase 386 (Fail-Safe Guard)\n")
            elif ultra_percentage > 30:
                f.write(
                    f"⚠️ **Status:** Mixed usage ({ultra_percentage:.1f}% Ultra, {100-ultra_percentage:.1f}% Delta)\n"
                )
                f.write("\n**Recommendation:** Review why some underlyings use delta fallback\n")
            else:
                f.write(f"⚠️ **Status:** Low Ultra usage ({ultra_percentage:.1f}%)\n")
                f.write("\n**Recommendation:** Verify Ultra models are loading correctly\n")

        logger.info(f"✓ Report written: {report_file}")

        # Determine phase status
        if total_signals > 0:
            status = "ok"
            message = f"Telemetry tracked: {telemetry_metrics['ultra_used']} Ultra, {telemetry_metrics['delta_fallback']} Delta"
        else:
            status = "warn"
            message = "No scoring activity detected (no telemetry data)"

        logger.info(f"Phase 385 Status: {status.upper()} - {message}")
        logger.info("=" * 60)

        return {"status": status, "message": message, "metrics": telemetry_metrics}

    except Exception as e:
        logger.error(f"Phase 385 ERROR: {e}")
        return {"status": "error", "message": f"Phase 385 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_385()
    print(f"\nPhase 385 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
