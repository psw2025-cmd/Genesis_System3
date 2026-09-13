import ast
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from scripts import system3_gate_evaluator as evaluator
from dashboard.backend import auto_gates_service as service


def publish(root, **changes):
    payload = dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        gates={gid:{'gate_id':gid,'pass':False,'blocker_id':gid} for gid in evaluator.GATE_IDS},
        gates_passing=0, gates_total=len(evaluator.GATE_IDS), trade_ready=False, analyzer_ready=False,
        open_blockers=[], recommended_auto_actions=[])
    payload.update(changes)
    evaluator.write_reports(root, payload)
    return root/'reports/latest/system3_auto_gates/summary.json'


def test_reader_uses_same_snapshot_without_mutation_even_refresh(tmp_path,monkeypatch):
    path=publish(tmp_path)
    monkeypatch.setattr(service,'GATES_JSON',path)
    before=path.read_bytes(),path.stat().st_mtime_ns
    a=service.build_auto_gates_report(refresh=False)
    b=service.build_auto_gates_report(refresh=True,live_state={'broker':{'connected':True}})
    assert a['snapshot_id'] == b['snapshot_id']
    assert a['gates'] == b['gates']
    assert a['status'] == 'ok'
    assert (path.read_bytes(),path.stat().st_mtime_ns) == before
    assert not a['trade_ready'] and not a['order_placement_allowed']


@pytest.mark.parametrize('kind',['missing','stale','future','tamper','legacy','list','bad_manifest'])
def test_invalid_snapshot_is_unknown_not_empty_success(tmp_path,monkeypatch,kind):
    path=publish(tmp_path)
    if kind == 'missing':
        path.unlink()
    elif kind in ('stale','future'):
        offset=-301 if kind=='stale' else 60
        publish(tmp_path, generated_utc=(datetime.now(timezone.utc)+timedelta(seconds=offset)).isoformat())
    else:
        payload=json.loads(path.read_text())
        if kind=='tamper':
            payload['gates'][evaluator.GATE_IDS[0]]['pass']=True
        elif kind=='legacy':
            payload.pop('snapshot_manifest')
        elif kind=='list':
            payload=[]
        else:
            payload['snapshot_manifest']=[]
        path.write_text(json.dumps(payload))
    monkeypatch.setattr(service,'GATES_JSON',path)
    result=service.build_auto_gates_report(refresh=True)
    assert result['status']=='UNKNOWN'
    assert result['gates_total']==len(evaluator.GATE_IDS)
    assert result['gates_passing']==0
    assert result['trade_ready'] is False
    assert result['open_blockers']


def test_failed_atomic_replace_retains_previous_snapshot(tmp_path,monkeypatch):
    path=publish(tmp_path)
    previous=path.read_bytes()
    def fail(*args):
        raise PermissionError('test replacement failure')
    monkeypatch.setattr(evaluator.os,'replace',fail)
    with pytest.raises(PermissionError):
        publish(tmp_path)
    assert path.read_bytes()==previous
    assert not list(path.parent.glob('.summary-*.tmp'))


def test_http_handler_delegates_without_state_read_or_proof_generation(monkeypatch):
    # Exercise the real function body without importing app startup/broker workers.
    import asyncio
    path=Path(service.ROOT)/'dashboard/backend/app.py'
    module=ast.parse(path.read_text(encoding='utf-8'))
    fn=next(n for n in module.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='get_auto_gates')
    fn.decorator_list=[]
    namespace={}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec'),namespace)
    monkeypatch.setattr(service,'build_auto_gates_report',lambda:{'snapshot_id':'test-snapshot'})
    assert asyncio.run(namespace['get_auto_gates'](refresh=True)) == {'snapshot_id':'test-snapshot'}


def test_cached_batch_reloads_same_gate_snapshot_and_preserves_identity(tmp_path,monkeypatch):
    import asyncio
    from typing import Any, Dict
    path=publish(tmp_path)
    monkeypatch.setattr(service,'GATES_JSON',path)
    source=Path(service.ROOT)/'dashboard/backend/app.py'
    module=ast.parse(source.read_text(encoding='utf-8'))
    selected=[]
    for name in ('get_auto_gates','_slim_gates','batch_market_data'):
        fn=next(n for n in module.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
        fn.decorator_list=[]
        selected.append(fn)
    ns={'Any':Any,'Dict':Dict,'_TTL_BATCH':8,'_cache_get':lambda *args:{'auto_gates':{'snapshot_id':'old'}}}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),ns)
    batch=asyncio.run(ns['batch_market_data']())
    direct=service.build_auto_gates_report()
    assert batch['auto_gates']['snapshot_id']==direct['snapshot_id']
    assert batch['auto_gates']['snapshot_sha256']==direct['snapshot_sha256']
    assert batch['auto_gates']['gates_passing']==direct['gates_passing']
    assert ns['_slim_gates'](None)['gates_total'] is None
