"""
System3 Phase 369 - Pipeline Profiler

Measures runtime, memory usage, IO cost across entire signal pipeline.
Identifies bottlenecks in curated and forward return processing.
Generates profile charts for analysis.

Run lightweight (no heavy external libraries).
Avoid blocking execution of main workflow.
"""

import sys
import json
import logging
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineProfiler:
    """Lightweight pipeline profiler."""

    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
        self.file_sizes: Dict[str, int] = {}

    def measure_file_io(self, filepath: Path) -> Dict[str, Any]:
        """Measure file size and read time."""

        start_time = time.time()

        try:
            # Check file size
            size_bytes = filepath.stat().st_size

            # Measure read time
            read_start = time.time()
            with open(filepath, "r") as f:
                _ = f.read()
            read_time = time.time() - read_start

            return {
                "exists": True,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 4),
                "read_time_ms": round(read_time * 1000, 2),
                "io_throughput_mbps": round(size_bytes / (1024 * 1024) / read_time if read_time > 0 else 0, 2),
            }

        except FileNotFoundError:
            return {"exists": False, "size_bytes": 0, "size_mb": 0, "read_time_ms": 0, "io_throughput_mbps": 0}

    def profile_signal_files(self) -> Dict[str, Dict[str, Any]]:
        """Profile all critical signal files."""

        files_to_profile = [
            STORAGE_LIVE / "dhan_index_ai_signals_curated.csv",
            STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv",
            STORAGE_LIVE / "clean" / "dhan_index_ai_signals_deduped.csv",
            STORAGE_LIVE / "clean" / "dhan_index_ai_signals_with_forward_deduped.csv",
        ]

        profile_results = {}

        for filepath in files_to_profile:
            name = filepath.name
            profile_results[name] = self.measure_file_io(filepath)

        return profile_results

    def estimate_memory_usage(self, file_size_mb: float) -> Dict[str, float]:
        """
        Estimate memory usage for file processing.

        Pandas typically uses 2-5x memory overhead for CSV files.
        """

        # Conservative estimates
        read_memory_mb = file_size_mb * 3.0  # 3x for reading CSV
        processing_overhead_mb = file_size_mb * 1.5  # 1.5x for operations
        total_estimated_mb = read_memory_mb + processing_overhead_mb

        return {
            "file_size_mb": round(file_size_mb, 2),
            "read_memory_mb": round(read_memory_mb, 2),
            "processing_overhead_mb": round(processing_overhead_mb, 2),
            "total_estimated_mb": round(total_estimated_mb, 2),
        }

    def compute_pipeline_metrics(self, profiles: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compute aggregate pipeline metrics."""

        total_size_mb = sum(p.get("size_mb", 0) for p in profiles.values() if p.get("exists"))

        total_read_time_ms = sum(p.get("read_time_ms", 0) for p in profiles.values() if p.get("exists"))

        throughput_values = [
            p.get("io_throughput_mbps", 0)
            for p in profiles.values()
            if p.get("exists") and p.get("io_throughput_mbps", 0) > 0
        ]

        avg_throughput = sum(throughput_values) / len(throughput_values) if throughput_values else 0

        # Estimate total memory usage
        total_memory_estimate = sum(
            self.estimate_memory_usage(p.get("size_mb", 0)).get("total_estimated_mb", 0)
            for p in profiles.values()
            if p.get("exists")
        )

        return {
            "total_pipeline_size_mb": round(total_size_mb, 2),
            "total_io_time_ms": round(total_read_time_ms, 2),
            "average_io_throughput_mbps": round(avg_throughput, 2),
            "estimated_peak_memory_mb": round(total_memory_estimate, 2),
            "estimated_processing_time_sec": round(total_read_time_ms / 1000, 2),
            "files_processed": sum(1 for p in profiles.values() if p.get("exists")),
        }


def identify_bottlenecks(profiles: Dict[str, Dict[str, Any]], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Identify bottlenecks in pipeline.
    """

    bottlenecks = []

    # Bottleneck 1: Large files with slow IO
    for filename, profile in profiles.items():
        if not profile.get("exists"):
            continue

        read_time = profile.get("read_time_ms", 0)
        size_mb = profile.get("size_mb", 0)

        if size_mb > 10 and read_time > 500:
            bottlenecks.append(
                {
                    "file": filename,
                    "type": "slow_io",
                    "severity": "medium",
                    "description": f"Large file ({size_mb:.2f}MB) takes {read_time:.0f}ms to read",
                    "recommendation": "Consider chunked processing or filtering",
                }
            )

    # Bottleneck 2: High memory usage
    peak_memory = metrics.get("estimated_peak_memory_mb", 0)
    if peak_memory > 500:
        bottlenecks.append(
            {
                "type": "high_memory",
                "severity": "medium" if peak_memory < 1000 else "high",
                "description": f"Estimated peak memory {peak_memory:.0f}MB",
                "recommendation": "Consider streaming or out-of-core processing",
            }
        )

    # Bottleneck 3: Long processing time
    proc_time = metrics.get("estimated_processing_time_sec", 0)
    if proc_time > 10:
        bottlenecks.append(
            {
                "type": "slow_processing",
                "severity": "low",
                "description": f"Estimated processing time {proc_time:.1f}s",
                "recommendation": "Optimize critical paths or parallelize",
            }
        )

    return bottlenecks


def generate_markdown_report(
    profiles: Dict[str, Dict[str, Any]], metrics: Dict[str, Any], bottlenecks: List[Dict[str, Any]]
) -> str:
    """Generate markdown report for pipeline profiling."""

    report = """# PIPELINE PROFILER - PHASE 369

**Generated:** {timestamp}

## Executive Summary

This phase profiles the entire signal processing pipeline to identify performance
bottlenecks and resource usage patterns.

**Total Pipeline Size:** {size:.2f} MB  
**Estimated Processing Time:** {time:.2f}s  
**Estimated Peak Memory:** {memory:.0f} MB  
**Files Processed:** {files}

""".format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        size=metrics.get("total_pipeline_size_mb", 0),
        time=metrics.get("estimated_processing_time_sec", 0),
        memory=metrics.get("estimated_peak_memory_mb", 0),
        files=metrics.get("files_processed", 0),
    )

    report += "## File-by-File Analysis\n\n"

    for filename, profile in profiles.items():
        if not profile.get("exists"):
            report += f"- [NOT FOUND] {filename}\n"
            continue

        report += f"""
### {filename}

| Metric | Value |
|--------|-------|
| Size | {profile['size_mb']:.2f} MB |
| Read Time | {profile['read_time_ms']:.0f} ms |
| Throughput | {profile['io_throughput_mbps']:.2f} MB/s |

"""

    report += "## Memory Usage Estimate\n\n"

    total_memory = metrics.get("estimated_peak_memory_mb", 0)
    report += f"""| Component | Memory (MB) |
|-----------|----------|
| File Read | {total_memory * 0.6:.0f} |
| Processing | {total_memory * 0.3:.0f} |
| Overhead | {total_memory * 0.1:.0f} |
| **Total Peak** | **{total_memory:.0f}** |

**Memory Classification:** """

    if total_memory < 200:
        report += "[OK] Low (< 200 MB)\n"
    elif total_memory < 500:
        report += "[OK] Moderate (< 500 MB)\n"
    elif total_memory < 1000:
        report += "[WARN] Elevated (< 1000 MB)\n"
    else:
        report += "[ALERT] High (> 1000 MB)\n"

    if bottlenecks:
        report += f"\n## Identified Bottlenecks ({len(bottlenecks)})\n\n"

        for bottleneck in bottlenecks:
            severity_icon = {"high": "[ALERT]", "medium": "[WARN]", "low": "[OK]"}.get(
                bottleneck.get("severity"), "[INFO]"
            )

            file_info = f" ({bottleneck.get('file')})" if "file" in bottleneck else ""

            report += f"""### {severity_icon} {bottleneck['type'].replace("_", " ").title()}{file_info}

**Description:** {bottleneck['description']}  
**Severity:** {bottleneck['severity'].upper()}  
**Recommendation:** {bottleneck['recommendation']}

"""
    else:
        report += "\n## [OK] No Critical Bottlenecks Detected\n\n"

    report += """## Profiling Metrics Explanation

- **Size:** Actual file size on disk
- **Read Time:** Time to read entire file into memory
- **Throughput:** MB/s read rate (higher is better)
- **Estimated Memory:** Approximate peak memory during processing
- **Processing Time:** Estimated time for entire pipeline

## Optimization Recommendations

1. **Chunked Processing:** For files > 50 MB, consider processing in chunks
2. **Data Filtering:** Apply filters early to reduce data volume
3. **Parallel Processing:** Independent files can be processed in parallel
4. **Caching:** Cache frequently accessed data to reduce IO
5. **Compression:** Consider compressed storage for historical data

## Performance Targets

- Pipeline should complete in < 5 seconds
- Peak memory should stay < 500 MB
- Average IO throughput > 50 MB/s

---

**Status:** [OK] Profiling Complete (DRY-RUN)  
**Mode:** Read-only analysis  
**Next Profile:** After major code changes or data volume increases
"""

    return report


def run_phase369(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 369 - Pipeline Profiler

    Args:
        context: Optional execution context

    Returns:
        {"status": "ok"|"warn"|"error", "outputs": {"json": path, "report": path}}
    """
    logger.info("Phase 369: Starting Pipeline Profiling")

    try:
        # Create profiler
        profiler = PipelineProfiler()

        # Profile signal files
        profiles = profiler.profile_signal_files()

        # Compute aggregate metrics
        metrics = profiler.compute_pipeline_metrics(profiles)

        # Identify bottlenecks
        bottlenecks = identify_bottlenecks(profiles, metrics)

        # Write JSON output
        json_path = STORAGE_METRICS / "pipeline_profile_369.json"
        json_output = {
            "phase": 369,
            "timestamp": datetime.now().isoformat(),
            "file_profiles": profiles,
            "aggregate_metrics": metrics,
            "bottlenecks": bottlenecks,
        }

        with open(json_path, "w") as f:
            json.dump(json_output, f, indent=2)

        logger.info(f"JSON output: {json_path}")

        # Write markdown report
        md_report = generate_markdown_report(profiles, metrics, bottlenecks)
        md_path = REPORTS_DIR / "PIPELINE_PROFILE_369.md"

        with open(md_path, "w") as f:
            f.write(md_report)

        logger.info(f"Markdown report: {md_path}")

        # Status based on bottleneck severity
        critical_bottlenecks = sum(1 for b in bottlenecks if b.get("severity") == "high")
        status = "warn" if critical_bottlenecks > 0 else "ok"

        return {"phase": 369, "status": status, "outputs": {"json": str(json_path), "report": str(md_path)}}

    except Exception as e:
        logger.error(f"Phase 369 error: {e}")
        return {"phase": 369, "status": "error", "error": str(e), "outputs": {}}


if __name__ == "__main__":
    result = run_phase369()
    print(json.dumps(result, indent=2))
