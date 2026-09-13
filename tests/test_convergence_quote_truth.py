from datetime import datetime, timezone
import pytest
from scripts.system3_option_visibility_audit import pick_contract, load_state_signals, quote_proof
from dashboard.backend.chain_adapter import _normalize_chain_source, fetch_chain_for_api
import pandas as pd
import json
from scripts.system3_gate_evaluator import eval_option_visibility

NOW = datetime(2026, 9, 11, 5, 0, tzinfo=timezone.utc)

def quote(**changes):
    return dict(dict(source='dhan', provenance_status='VERIFIED_DHAN', source_timestamp=NOW.isoformat(),
        observed_at=NOW.isoformat(), market_session='OPEN', security_id='1234', trading_symbol='TEST_CONTRACT',
        expiry='2026-09-17', strike=24000, option_type='CE', ltp=101, bid=100, ask=102), **changes)

def test_missing_master_quote_never_becomes_125():
    assert pick_contract([{'option_type':'CE', 'security_id':'1234'}], 'CE')[3:] == (None,None,None)

def test_missing_signals_do_not_generate_baselines(tmp_path):
    assert load_state_signals(tmp_path, None) == ([], 'NO_SIGNAL_SOURCE')

@pytest.mark.parametrize('source', ['', 'real', 'datasource_manager', None])
def test_unknown_source_never_becomes_dhan(source):
    assert _normalize_chain_source(source) == 'UNKNOWN'
    assert quote_proof(quote(source=source), NOW)['quote_status'] == 'BLOCKED'

@pytest.mark.parametrize('changes', [dict(ltp=125,bid=124.5,ask=125.5), dict(source_timestamp=''),
    dict(source_timestamp='2026-09-10T05:00:00+00:00'), dict(source_timestamp='2026-09-11T05:01:00+00:00'),
    dict(ltp=float('nan')), dict(bid=None), dict(market_session='CLOSED'), dict(security_id='')])
def test_invalid_proof_fails_closed(changes):
    assert quote_proof(quote(**changes), NOW)['quote_status'] == 'BLOCKED'

def test_complete_broker_quote_can_pass():
    assert quote_proof(quote(), NOW)['quote_status'] == 'PASS'

def test_holiday_does_not_become_live():
    holiday = datetime(2026,9,14,5,0,tzinfo=timezone.utc)
    assert quote_proof(quote(source_timestamp=holiday.isoformat()), holiday)['quote_status'] == 'BLOCKED'

def test_chain_cache_preserves_source_time_and_security():
    class DSM:
        def fetch_option_chain(self, *args, **kwargs):
            return pd.DataFrame([dict(option_type='CE',strike=24000,oi=100,volume=100,ltp=100,
                source='dhan',security_id='1234',source_timestamp='2026-09-01T05:00:00+00:00',expiry='2026-09-17')]), 24000
    result = fetch_chain_for_api(DSM(), 'NIFTY')
    assert result['source_observed_at'] == '2026-09-01T05:00:00+00:00'
    assert result['data_mode'] != 'LIVE'
    assert result['contracts'][0]['security_id'] == '1234'
    assert result['cache_received_at'] != result['source_observed_at']

@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'synthetic', 'summary_only', None])
def test_each_required_index_needs_independent_proof(tmp_path, defect):
    symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
    rows = [dict(quote(security_id=str(100+i)), underlying=s, paper_trade_allowed=True) for i,s in enumerate(symbols)]
    if defect == 'missing':
        rows.pop()
    elif defect == 'duplicate':
        rows[-1]['security_id'] = rows[0]['security_id']
    elif defect == 'synthetic':
        rows[-1].update(ltp=125,bid=124.5,ask=125.5)
    elif defect == 'summary_only':
        rows = []
    report = tmp_path / 'reports/latest/option_strike_visibility.json'
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps({'summary': {'paper_trade_allowed_count': 99}, 'rows': rows}))
    result = eval_option_visibility(tmp_path, {'market': {'is_open':True}, 'positions':[{'strike':1,'option_type':'CE'}]}, now=NOW)
    assert result['pass'] is (defect is None)
    assert len(result['required_symbols']) == 4
    assert len(result['supported_symbols']) == 6
