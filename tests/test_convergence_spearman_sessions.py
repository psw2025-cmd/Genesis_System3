import json
from datetime import datetime, timezone
import pytest
from scripts.system3_gate_evaluator import eval_spearman_gate

NOW = datetime(2026,9,11,11,0,tzinfo=timezone.utc)

@pytest.mark.parametrize('days,rho,coverage,expected', [
    ([9,10,11], .1, True, False),
    ([1,3,7,9,11], .8, True, False),
    ([7,8,9,10,11], .7, True, True),
    ([7,8,9,10,11], .7, False, False),
    ([4,7,8,9,10], .8, True, False),
])
def test_threshold_requires_latest_consecutive_covered_sessions(tmp_path,days,rho,coverage,expected):
    out = tmp_path/'state/market_validations'
    out.mkdir(parents=True)
    for day in days:
        stamp = f'2026-09-{day:02}'
        (out/(stamp+'.json')).write_text(json.dumps(dict(date=stamp,rho=rho,status='PASS',
            coverage_complete=coverage,covered_underlyings=['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY'],
            source='state/gain_rank_history.json')))
    result = eval_spearman_gate(tmp_path, NOW)
    assert result['pass'] is expected
    assert result['threshold'] == .7
    assert result['days_required'] == 5

def test_seeded_days_cannot_qualify(tmp_path):
    out=tmp_path/'state/market_validations'
    out.mkdir(parents=True)
    for day in range(7,12):
        stamp=f'2026-09-{day:02}'
        (out/(stamp+'.json')).write_text(json.dumps(dict(date=stamp,rho=.99,status='PASS',seeded=True,
            coverage_complete=True,covered_underlyings=['NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY'],
            source='state/gain_rank_history.json')))
    assert eval_spearman_gate(tmp_path,NOW)['pass'] is False
