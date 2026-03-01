#!/usr/bin/env python3
"""
Chart Test Script - Genesis System3
Fetches data from the backend API and generates charts viewable in Cursor.
Output: outputs/chart_test_output.html (open in Simple Browser or as file)
"""

import json
import sys
from pathlib import Path

# Add project root
ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import requests
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install requests plotly")
    sys.exit(1)

API_BASE = "http://127.0.0.1:8000"
OUTPUT_PATH = ROOT / "outputs" / "chart_test_output.html"


def fetch_api(path: str) -> dict | None:
    """Fetch JSON from backend API."""
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [WARN] {path}: {e}")
        return None


def main():
    print("Chart Test Script - Genesis System3")
    print("=" * 50)
    print(f"API: {API_BASE}")
    print(f"Output: {OUTPUT_PATH}")
    print()

    # Fetch data
    health = fetch_api("/api/health")
    perf = fetch_api("/api/perf")
    state = fetch_api("/api/state")

    # Build chart data
    perf_history = []
    if perf and isinstance(perf.get("history"), list):
        perf_history = perf.get("history", [])[:30]
    elif perf and isinstance(perf.get("current"), dict):
        cur = perf.get("current", {})
        perf_history = [
            {
                "timestamp": "current",
                "cycle_duration": cur.get("cycle_duration_sec", 0),
                "fetch_duration": cur.get("fetch_duration_sec", 0),
                "strategy_duration": cur.get("strategy_duration_sec", 0),
            }
        ]

    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Performance SLA (Cycle Duration)",
            "Fetch vs Strategy Duration",
            "Health Status Summary",
            "Data Source",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "indicator"}, {"type": "indicator"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12,
    )

    # 1. Performance SLA line chart
    if perf_history:
        timestamps = [h.get("timestamp", str(i))[:19] for i, h in enumerate(perf_history)]
        cycle_dur = [h.get("cycle_duration") or 0 for h in perf_history]
        fig.add_trace(
            go.Scatter(x=timestamps, y=cycle_dur, name="Cycle (s)", line=dict(color="#22c55e")),
            row=1,
            col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(x=["N/A"], y=[0], name="No data", mode="markers", marker=dict(size=1, opacity=0)),
            row=1,
            col=1,
        )

    # 2. Fetch vs Strategy bar chart
    if perf_history:
        timestamps = [h.get("timestamp", str(i))[:19] for i, h in enumerate(perf_history)]
        fetch_dur = [h.get("fetch_duration") or 0 for h in perf_history]
        strat_dur = [h.get("strategy_duration") or 0 for h in perf_history]
        fig.add_trace(
            go.Bar(x=timestamps, y=fetch_dur, name="Fetch (s)", marker_color="#3b82f6"),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Bar(x=timestamps, y=strat_dur, name="Strategy (s)", marker_color="#f59e0b"),
            row=1,
            col=2,
        )

    # 3. Health status indicator
    status = "unknown"
    if health and isinstance(health, dict):
        status = health.get("status", "unknown")
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=1 if status == "ok" else 0,
            title={"text": "Backend Status"},
            gauge={"axis": {"range": [0, 1]}, "bar": {"color": "#22c55e" if status == "ok" else "#ef4444"}},
            number={"suffix": " (ok=1)"},
        ),
        row=2,
        col=1,
    )

    # 4. Data source indicator
    ds = "not_ready"
    if health and isinstance(health, dict):
        ds = health.get("data_source", "not_ready")
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=1 if ds == "live" else (0.5 if ds == "synthetic" else 0),
            title={"text": f"Data Source: {ds}"},
            number={"suffix": ""},
        ),
        row=2,
        col=2,
    )

    fig.update_layout(
        title="Genesis System3 - Chart Test (Backend API Data)",
        height=600,
        template="plotly_white",
        showlegend=True,
    )

    # Write HTML
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_PATH))
    print(f"[OK] Chart saved to: {OUTPUT_PATH}")
    print()
    print("To view in Cursor:")
    print("  1. Ctrl+Shift+P -> Simple Browser: Show")
    print(f"  2. Enter file URL: file:///{OUTPUT_PATH.as_posix()}")
    print("  Or open the file directly in Cursor (HTML preview).")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
