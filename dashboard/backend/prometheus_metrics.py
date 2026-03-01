"""
P2.3: Prometheus metrics endpoint for monitoring/alerting.
Exposes /metrics in Prometheus text format.
"""

import time

# In-memory counters (reset on restart); incremented by app middleware
_request_count = 0
_start_time = time.time()


def get_metrics_payload() -> str:
    """Generate Prometheus text format."""
    uptime = time.time() - _start_time
    lines = [
        "# HELP system3_http_requests_total Total HTTP API requests",
        "# TYPE system3_http_requests_total counter",
        f"system3_http_requests_total {_request_count}",
        "# HELP system3_uptime_seconds Process uptime in seconds",
        "# TYPE system3_uptime_seconds gauge",
        f"system3_uptime_seconds {uptime:.1f}",
    ]
    return "\n".join(lines) + "\n"
