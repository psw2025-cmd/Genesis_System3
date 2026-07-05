"""
Performance Metrics Collection - Runtime, memory, CPU, IO, throughput, jitter
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

ROOT_DIR = Path(__file__).parent.parent


class PerformanceMonitor:
    """Monitor system performance metrics."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cycle_times = []
        self.cpu_samples = []
        self.memory_samples = []
        self.process = None

    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        try:
            self.process = psutil.Process(os.getpid())
        except Exception:
            self.process = None

    def record_cycle(self, cycle_duration: float):
        """Record cycle duration."""
        self.cycle_times.append(cycle_duration)

    def sample(self):
        """Take a performance sample."""
        if self.process:
            try:
                cpu_percent = self.process.cpu_percent(interval=0.1)
                memory_info = self.process.memory_info()
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_info.rss / 1024 / 1024)  # MB
            except Exception:
                pass

    def stop(self):
        """Stop monitoring and generate metrics."""
        self.end_time = time.time()
        return self.get_metrics()

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_seconds": round(duration, 2),
            "total_cycles": len(self.cycle_times),
        }

        # CPU metrics
        if self.cpu_samples:
            metrics["cpu_percent"] = {
                "avg": round(sum(self.cpu_samples) / len(self.cpu_samples), 2),
                "peak": round(max(self.cpu_samples), 2),
                "min": round(min(self.cpu_samples), 2),
            }
        else:
            metrics["cpu_percent"] = {"avg": 0, "peak": 0, "min": 0}

        # Memory metrics
        if self.memory_samples:
            metrics["memory_mb"] = {
                "avg": round(sum(self.memory_samples) / len(self.memory_samples), 2),
                "peak": round(max(self.memory_samples), 2),
                "min": round(min(self.memory_samples), 2),
            }
        else:
            metrics["memory_mb"] = {"avg": 0, "peak": 0, "min": 0}

        # Cycle throughput
        if duration > 0 and len(self.cycle_times) > 0:
            metrics["cycles_per_minute"] = round((len(self.cycle_times) / duration) * 60, 2)
        else:
            metrics["cycles_per_minute"] = 0

        # Cycle jitter (variance in cycle duration)
        if len(self.cycle_times) > 1:
            avg_cycle = sum(self.cycle_times) / len(self.cycle_times)
            variance = sum((x - avg_cycle) ** 2 for x in self.cycle_times) / len(self.cycle_times)
            metrics["cycle_jitter"] = {
                "avg_duration_seconds": round(avg_cycle, 3),
                "variance": round(variance, 6),
                "std_dev": round(variance**0.5, 3),
                "min": round(min(self.cycle_times), 3),
                "max": round(max(self.cycle_times), 3),
            }
        else:
            metrics["cycle_jitter"] = {"avg_duration_seconds": 0, "variance": 0, "std_dev": 0, "min": 0, "max": 0}

        # Output size (calculate total size of output files)
        output_dir = ROOT_DIR / "outputs"
        total_size = 0
        output_files = [
            "health.json",
            "qc_report_live.json",
            "top_trade_signal.json",
            "chain_raw_live.csv",
            "underlying_rank_live.csv",
        ]
        for filename in output_files:
            file_path = output_dir / filename
            if file_path.exists():
                total_size += file_path.stat().st_size

        metrics["output_size_bytes"] = total_size
        metrics["output_size_kb"] = round(total_size / 1024, 2)

        return metrics


# Fallback if psutil not available
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def create_perf_metrics_fallback(
    start_time: float, end_time: float, cycle_count: int, output_dir: Path
) -> Dict[str, Any]:
    """Create performance metrics without psutil."""
    duration = end_time - start_time

    # Calculate output size
    total_size = 0
    output_files = [
        "health.json",
        "qc_report_live.json",
        "top_trade_signal.json",
        "chain_raw_live.csv",
        "underlying_rank_live.csv",
    ]
    for filename in output_files:
        file_path = output_dir / filename
        if file_path.exists():
            total_size += file_path.stat().st_size

    return {
        "timestamp": datetime.now().isoformat(),
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "end_time": datetime.fromtimestamp(end_time).isoformat(),
        "duration_seconds": round(duration, 2),
        "total_cycles": cycle_count,
        "cycles_per_minute": round((cycle_count / duration) * 60, 2) if duration > 0 else 0,
        "cpu_percent": {"avg": 0, "peak": 0, "min": 0},  # Not available
        "memory_mb": {"avg": 0, "peak": 0, "min": 0},  # Not available
        "output_size_bytes": total_size,
        "output_size_kb": round(total_size / 1024, 2),
        "cycle_jitter": {"avg_duration_seconds": 0, "variance": 0, "std_dev": 0, "min": 0, "max": 0},
        "note": "psutil not available, limited metrics",
    }


if __name__ == "__main__":
    # Test
    monitor = PerformanceMonitor()
    monitor.start()
    time.sleep(1)
    monitor.record_cycle(0.5)
    monitor.sample()
    metrics = monitor.stop()
    print(json.dumps(metrics, indent=2))
