from scripts.gcp_configure_traffic_monitoring import PREFIX, desired_policies


def test_traffic_monitoring_covers_platform_and_container_failure_modes():
    policies = desired_policies(["projects/p/notificationChannels/123"])
    assert len(policies) == 5
    names = {row["displayName"] for row in policies}
    assert f"{PREFIX} - pending queue" in names
    assert f"{PREFIX} - HTTP 429 in container" in names
    assert f"{PREFIX} - HTTP 5xx" in names
    assert f"{PREFIX} - instance saturation" in names
    assert f"{PREFIX} - pending latency p95" in names

    blob = str(policies)
    assert "run.googleapis.com/pending_queue/pending_requests" in blob
    assert "run.googleapis.com/request_count" in blob
    assert 'response_code\\\'="429"' not in blob  # avoid malformed escaped filters
    assert 'response_code\"=\"429' in blob
    assert "run.googleapis.com/container/instance_count" in blob
    assert "run.googleapis.com/request_latency/pending" in blob
    assert "ALIGN_PERCENTILE_95" in blob


def test_all_traffic_policies_attach_existing_notification_channels():
    channel = "projects/p/notificationChannels/123"
    policies = desired_policies([channel])
    assert all(row["notificationChannels"] == [channel] for row in policies)
    assert all(row["enabled"] is True for row in policies)


def test_alert_documentation_preserves_analyzer_safety():
    policies = desired_policies([])
    for policy in policies:
        text = policy["documentation"]["content"]
        assert "LIVE trading remains OFF" in text
        assert "Do not bypass safety gates" in text
