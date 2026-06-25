"""
Minimal Prometheus-text-format /metrics endpoint - hand-rolled rather
than adding prometheus-fastapi-instrumentator as a new dependency,
since this only needs a handful of counters/gauges, not the full
client library. No third-party dependency, no new attack surface.

Exposes:
  - system3_http_requests_total{method,path,status} (counter)
  - system3_http_request_duration_seconds (histogram, fixed buckets)
  - system3_up (gauge, always 1 - process liveness)
"""

import threading
import time
from collections import defaultdict
from typing import Dict, Tuple

_LOCK = threading.Lock()
_REQUEST_COUNTS: Dict[Tuple[str, str, int], int] = defaultdict(int)
_DURATION_BUCKETS = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_DURATION_BUCKET_COUNTS: Dict[float, int] = defaultdict(int)
_DURATION_SUM = 0.0
_DURATION_COUNT = 0
_PROCESS_START = time.time()


def record_request(method: str, path: str, status: int, duration_seconds: float) -> None:
    global _DURATION_SUM, _DURATION_COUNT
    with _LOCK:
        _REQUEST_COUNTS[(method, path, status)] += 1
        for bucket in _DURATION_BUCKETS:
            if duration_seconds <= bucket:
                _DURATION_BUCKET_COUNTS[bucket] += 1
        _DURATION_SUM += duration_seconds
        _DURATION_COUNT += 1


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_prometheus_text() -> str:
    """Render current metrics in Prometheus text exposition format."""
    lines = []

    lines.append("# HELP system3_up Process liveness (always 1 while serving this request)")
    lines.append("# TYPE system3_up gauge")
    lines.append("system3_up 1")

    lines.append("# HELP system3_process_uptime_seconds Seconds since process start")
    lines.append("# TYPE system3_process_uptime_seconds gauge")
    lines.append(f"system3_process_uptime_seconds {time.time() - _PROCESS_START:.3f}")

    with _LOCK:
        lines.append("# HELP system3_http_requests_total Total HTTP requests")
        lines.append("# TYPE system3_http_requests_total counter")
        for (method, path, status), count in sorted(_REQUEST_COUNTS.items()):
            labels = f'method="{_escape_label(method)}",path="{_escape_label(path)}",status="{status}"'
            lines.append(f"system3_http_requests_total{{{labels}}} {count}")

        lines.append("# HELP system3_http_request_duration_seconds Request duration")
        lines.append("# TYPE system3_http_request_duration_seconds histogram")
        cumulative = 0
        for bucket in _DURATION_BUCKETS:
            cumulative = _DURATION_BUCKET_COUNTS.get(bucket, 0)
            lines.append(f'system3_http_request_duration_seconds_bucket{{le="{bucket}"}} {cumulative}')
        lines.append(f'system3_http_request_duration_seconds_bucket{{le="+Inf"}} {_DURATION_COUNT}')
        lines.append(f"system3_http_request_duration_seconds_sum {_DURATION_SUM:.6f}")
        lines.append(f"system3_http_request_duration_seconds_count {_DURATION_COUNT}")

    return "\n".join(lines) + "\n"
