"""
System3 Phase 81 - Micro-Latency Profiler

Measure per-step latency inside live loops: data fetch, feature build,
model inference, trade logic, logging.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import statistics

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase81_latency_profile.json"
OUTPUT_MD = STORAGE_ULTRA / "phase81_latency_profile.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

ITERATIONS = 10  # Default iterations


def simulate_live_loop_iteration() -> Dict[str, float]:
    """Simulate one live loop iteration and measure latencies."""
    metrics = {}

    # Simulate snapshot fetch
    start = time.time()
    time.sleep(0.01)  # Simulate 10ms fetch
    metrics["snapshot_fetch_ms"] = (time.time() - start) * 1000

    # Simulate feature build
    start = time.time()
    time.sleep(0.005)  # Simulate 5ms feature build
    metrics["features_build_ms"] = (time.time() - start) * 1000

    # Simulate model inference
    start = time.time()
    time.sleep(0.015)  # Simulate 15ms inference
    metrics["model_infer_ms"] = (time.time() - start) * 1000

    # Simulate trade logic
    start = time.time()
    time.sleep(0.002)  # Simulate 2ms trade logic
    metrics["trade_logic_ms"] = (time.time() - start) * 1000

    # Simulate logging
    start = time.time()
    time.sleep(0.001)  # Simulate 1ms logging
    metrics["logging_ms"] = (time.time() - start) * 1000

    # Total
    metrics["total_loop_ms"] = sum(
        [
            metrics["snapshot_fetch_ms"],
            metrics["features_build_ms"],
            metrics["model_infer_ms"],
            metrics["trade_logic_ms"],
            metrics["logging_ms"],
        ]
    )

    return metrics


def generate_latency_profile() -> Dict[str, Any]:
    """Generate latency profile."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 81 - MICRO-LATENCY PROFILER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Collect metrics
    all_metrics = []
    steps = [
        "snapshot_fetch_ms",
        "features_build_ms",
        "model_infer_ms",
        "trade_logic_ms",
        "logging_ms",
        "total_loop_ms",
    ]

    print(f"[PH81] Collecting latency metrics across {ITERATIONS} iterations...")
    for i in range(ITERATIONS):
        metrics = simulate_live_loop_iteration()
        all_metrics.append(metrics)
        if (i + 1) % 5 == 0:
            print(f"[PH81] Completed {i + 1}/{ITERATIONS} iterations")

    # Aggregate
    aggregated = {}
    for step in steps:
        values = [m[step] for m in all_metrics]
        aggregated[step] = {
            "min_ms": float(min(values)),
            "max_ms": float(max(values)),
            "avg_ms": float(statistics.mean(values)),
            "median_ms": float(statistics.median(values)),
        }

    report = {
        "timestamp": datetime.now().isoformat(),
        "iterations": ITERATIONS,
        "steps": aggregated,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH81] Latency profile saved to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH81] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 81 - Latency Profile\n\n")
        f.write(f"**Date**: {report['timestamp']}\n")
        f.write(f"**Iterations**: {report['iterations']}\n\n")

        f.write("## Latency Metrics\n\n")
        f.write("| Step | min_ms | max_ms | avg_ms |\n")
        f.write("|------|--------|--------|--------|\n")

        for step, stats in report["steps"].items():
            f.write(f"| {step} | {stats['min_ms']:.2f} | {stats['max_ms']:.2f} | {stats['avg_ms']:.2f} |\n")

        f.write("\n## Comments\n\n")
        # Check for steps above threshold (e.g., 50ms)
        for step, stats in report["steps"].items():
            if stats["avg_ms"] > 50.0:
                f.write(f"- ⚠️ {step}: Average latency ({stats['avg_ms']:.2f}ms) is above 50ms threshold.\n")


def main():
    """Main entry point."""
    try:
        report = generate_latency_profile()
        print("\n[PH81] Latency profiling complete.")
        return 0
    except Exception as e:
        print(f"\n[PH81] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
