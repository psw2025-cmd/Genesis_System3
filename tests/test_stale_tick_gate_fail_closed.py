"""A stale reported PASS cannot satisfy the real-time tick gate."""
import json
from datetime import datetime, timedelta, timezone

from scripts.system3_gate_evaluator import eval_tick_health_gate


def test_stale_tick_pass_bit_rejected(tmp_path):
    path = tmp_path / 'reports' / 'latest' / 'websocket_tick_health' / 'summary.json'
    path.parent.mkdir(parents=True)
    past = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    path.write_text(json.dumps({'pass': True, 'generated_utc': past, 'evidence': {
        'last_tick_age_sec': 5, 'refresh_interval_sec': 5, 'broker_connected': True
    }}), encoding='utf-8')
    result = eval_tick_health_gate(tmp_path)
    assert result['pass'] is False
    assert result['blocker_id'] == 'TICK_HEALTH_BLOCKER'


def test_missing_origin_timestamp_rejected(tmp_path):
    path = tmp_path / 'reports' / 'latest' / 'websocket_tick_health' / 'summary.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'pass': True, 'evidence': {
        'last_tick_age_sec': 5, 'refresh_interval_sec': 5, 'broker_connected': True
    }}), encoding='utf-8')
    assert eval_tick_health_gate(tmp_path)['pass'] is False
