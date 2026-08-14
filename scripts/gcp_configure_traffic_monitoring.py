#!/usr/bin/env python3
"""Idempotently configure 24x7 Cloud Monitoring traffic/saturation alerts.

Uses only built-in Cloud Run metrics; no log-based metric or secret payload is
required. Important coverage detail: Cloud Run's request_count excludes requests
rejected before they reach a container (including some max-instance 429s), so
pending_queue/pending_requests and instance saturation are separate mandatory
conditions in addition to container-served 429/5xx.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Iterable, List

from google.auth import default as google_auth_default
from google.auth.transport.requests import AuthorizedSession

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
MAX_INSTANCES = max(1, int(os.environ.get("SYSTEM3_CLOUD_RUN_MAX_INSTANCES", "2") or 2))
REQUIRE_CHANNEL = str(os.environ.get("SYSTEM3_MONITORING_REQUIRE_CHANNEL", "0")).lower() in {"1", "true", "yes"}
PREFIX = "Genesis System3 Traffic"


def _base_filter(metric: str) -> str:
    return (
        'resource.type="cloud_run_revision" '
        f'AND resource.label."service_name"="{SERVICE}" '
        f'AND metric.type="{metric}"'
    )


def _condition(
    name: str,
    metric: str,
    *,
    threshold: float,
    aligner: str,
    metric_filter: str = "",
    duration: str = "0s",
    reducer: str = "REDUCE_SUM",
) -> Dict[str, Any]:
    filt = _base_filter(metric) + (f" AND {metric_filter}" if metric_filter else "")
    aggregation: Dict[str, Any] = {
        "alignmentPeriod": "60s",
        "perSeriesAligner": aligner,
    }
    if reducer:
        aggregation.update(
            {
                "crossSeriesReducer": reducer,
                "groupByFields": ['resource.label."service_name"'],
            }
        )
    return {
        "displayName": name,
        "conditionThreshold": {
            "filter": filt,
            "comparison": "COMPARISON_GT",
            "thresholdValue": threshold,
            "duration": duration,
            "aggregations": [aggregation],
            "trigger": {"count": 1},
        },
    }


def desired_policies(notification_channels: Iterable[str] = ()) -> List[Dict[str, Any]]:
    channels = [str(x) for x in notification_channels if str(x)]
    common = {
        "combiner": "OR",
        "enabled": True,
        "notificationChannels": channels,
        "alertStrategy": {
            "autoClose": "1800s",
            "notificationRateLimit": {"period": "300s"},
        },
    }
    docs = {
        "content": (
            "Genesis System3 analyzer/PAPER traffic protection incident. LIVE trading remains OFF. "
            "Check /api/traffic/health, Cloud Run pending requests/instances, recent response codes, "
            "and Dhan read-only pressure before changing scaling. Do not bypass safety gates."
        ),
        "mimeType": "text/markdown",
    }
    return [
        {
            **common,
            "displayName": f"{PREFIX} - pending queue",
            "documentation": docs,
            "conditions": [
                _condition(
                    "Pending requests > 0",
                    "run.googleapis.com/pending_queue/pending_requests",
                    threshold=0,
                    aligner="ALIGN_MAX",
                    duration="60s",
                )
            ],
        },
        {
            **common,
            "displayName": f"{PREFIX} - HTTP 429 in container",
            "documentation": docs,
            "conditions": [
                _condition(
                    "Container-served HTTP 429",
                    "run.googleapis.com/request_count",
                    threshold=0,
                    aligner="ALIGN_SUM",
                    metric_filter='metric.label."response_code"="429"',
                )
            ],
        },
        {
            **common,
            "displayName": f"{PREFIX} - HTTP 5xx",
            "documentation": docs,
            "conditions": [
                _condition(
                    "HTTP 5xx responses",
                    "run.googleapis.com/request_count",
                    threshold=0,
                    aligner="ALIGN_SUM",
                    metric_filter='metric.label."response_code_class"="5xx"',
                )
            ],
        },
        {
            **common,
            "displayName": f"{PREFIX} - instance saturation",
            "documentation": docs,
            "conditions": [
                _condition(
                    f"Active instances at configured max {MAX_INSTANCES}",
                    "run.googleapis.com/container/instance_count",
                    threshold=max(0.5, MAX_INSTANCES - 0.5),
                    aligner="ALIGN_MAX",
                    metric_filter='metric.label."state"="active"',
                    duration="60s",
                )
            ],
        },
        {
            **common,
            "displayName": f"{PREFIX} - pending latency p95",
            "documentation": docs,
            "conditions": [
                _condition(
                    "Pending latency p95 > 2 seconds",
                    "run.googleapis.com/request_latency/pending",
                    threshold=2000,
                    aligner="ALIGN_PERCENTILE_95",
                    duration="60s",
                    reducer="REDUCE_MAX",
                )
            ],
        },
    ]


def _session() -> AuthorizedSession:
    creds, _ = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(creds)


def _pages(session: AuthorizedSession, path: str, key: str) -> list:
    rows: list = []
    token = ""
    while True:
        params = {"pageSize": 1000}
        if token:
            params["pageToken"] = token
        response = session.get(f"https://monitoring.googleapis.com/v3/projects/{PROJECT}/{path}", params=params, timeout=30)
        response.raise_for_status()
        body = response.json()
        page = body.get(key, [])
        if not isinstance(page, list):
            raise RuntimeError(f"Malformed Monitoring {key} response")
        rows.extend(page)
        token = str(body.get("nextPageToken") or "")
        if not token:
            return rows


def _enabled_channels(session: AuthorizedSession) -> List[str]:
    channels = _pages(session, "notificationChannels", "notificationChannels")
    return sorted(
        str(row.get("name"))
        for row in channels
        if row.get("name") and row.get("enabled", True) is not False
    )


def _upsert(session: AuthorizedSession, policy: Dict[str, Any], existing: Dict[str, Any] | None) -> str:
    if existing and existing.get("name"):
        name = str(existing["name"])
        payload = {**policy, "name": name}
        response = session.patch(
            f"https://monitoring.googleapis.com/v3/{name}",
            params={
                "updateMask": "display_name,documentation,conditions,combiner,enabled,notification_channels,alert_strategy"
            },
            json=payload,
            timeout=30,
        )
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Monitoring policy update failed {response.status_code}: {response.text[:300]}")
        return "updated"

    response = session.post(
        f"https://monitoring.googleapis.com/v3/projects/{PROJECT}/alertPolicies",
        json=policy,
        timeout=30,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Monitoring policy create failed {response.status_code}: {response.text[:300]}")
    return "created"


def main() -> int:
    session = _session()
    channels = _enabled_channels(session)
    existing_rows = _pages(session, "alertPolicies", "alertPolicies")
    by_display = {str(row.get("displayName") or ""): row for row in existing_rows}
    desired = desired_policies(channels)
    results = []
    for policy in desired:
        action = _upsert(session, policy, by_display.get(policy["displayName"]))
        results.append({"display_name": policy["displayName"], "action": action})

    proof = {
        "status": "PASS" if (channels or not REQUIRE_CHANNEL) else "BLOCKED_NO_NOTIFICATION_CHANNEL",
        "project": PROJECT,
        "service": SERVICE,
        "policy_count": len(desired),
        "notification_channel_count": len(channels),
        "notification_channels": channels,
        "policies": results,
        "coverage": {
            "pending_queue": True,
            "container_http_429": True,
            "http_5xx": True,
            "instance_saturation": True,
            "pending_latency_p95": True,
            "platform_429_indirectly_covered_by_pending_queue": True,
        },
        "live_trading_enabled": False,
    }
    print("SYSTEM3_TRAFFIC_MONITORING " + json.dumps(proof, sort_keys=True))
    if proof["status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
