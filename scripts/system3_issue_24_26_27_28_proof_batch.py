#!/usr/bin/env python3
"""System3 proof-first batch for Issues #24, #26, #27, #28.

Read-only generator. It does not delete files, trade, login to broker, or enable live mode.
It creates proof/status files and a ZIP pack under reports/latest.
"""
from __future__ import annotations

import csv, hashlib, json, os, shutil, subprocess, zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
DATE = datetime.now(timezone.utc).strftime('%Y%m%d')
LATEST = ROOT / 'reports' / 'latest'
ARCHIVE = ROOT / 'reports' / 'archive'
TEXT_EXT = {'.py','.md','.txt','.json','.yml','.yaml','.toml','.ini','.cfg','.ps1','.sh','.ts','.tsx','.js','.jsx','.html','.css','.csv'}


def rel(p: Path) -> str:
    try: return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception: return p.as_posix()

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def write_json(path: Path, data) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True, default=str) + '\n')

def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k: r.get(k,'') for k in fields})

def cmd(args: list[str], timeout=60) -> dict:
    try:
        p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {'cmd': args, 'returncode': p.returncode, 'stdout': p.stdout[-4000:], 'stderr': p.stderr[-4000:]}
    except Exception as e:
        return {'cmd': args, 'returncode': None, 'error': repr(e), 'stdout':'', 'stderr':''}

def files() -> list[str]:
    r = cmd(['git','ls-files'], 30)
    if r.get('returncode') == 0 and r.get('stdout'):
        return sorted(x for x in r['stdout'].splitlines() if x.strip())
    return sorted(rel(p) for p in ROOT.rglob('*') if p.is_file() and '.git/' not in rel(p))

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def read(path: str, n=300000) -> str:
    try: return (ROOT/path).read_text(encoding='utf-8', errors='replace')[:n]
    except Exception: return ''

def search(all_files, terms):
    out=[]; terms=[t.lower() for t in terms]
    for f in all_files:
        lf=f.lower(); hit=[]
        if any(t in lf for t in terms): hit.append('path')
        p=ROOT/f
        if p.suffix.lower() in TEXT_EXT and p.exists() and p.stat().st_size < 2_000_000:
            txt=read(f).lower()
            if any(t in txt for t in terms): hit.append('content')
        if hit: out.append({'file':f,'hit':'+'.join(hit)})
    return out[:300]

def archive(latest_dir: Path, name: str):
    if not latest_dir.exists(): return
    dst = ARCHIVE / name / DATE
    if dst.exists(): shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(latest_dir, dst)

def status(phase, issue, st, reason, outputs=None, blockers=None, warnings=None):
    return {'phase':phase,'issue':issue,'status':st,'reason':reason,'outputs':outputs or [],'blockers':blockers or [],'warnings':warnings or []}

def repo_authority(all_files):
    d=LATEST/'repo_authority'; d.mkdir(parents=True, exist_ok=True)
    inv=[]; hashes=[]; names={}
    for f in all_files:
        p=ROOT/f; name=p.name.lower(); names.setdefault(name,[]).append(f)
        cls='GENERATED_REPORT' if f.startswith('reports/') else 'NEEDS_HUMAN_REVIEW' if any(x in f.lower() for x in ['old','backup','copy','archive','bak']) else 'KEEP_ACTIVE'
        inv.append({'path':f,'size':p.stat().st_size if p.exists() else '', 'suffix':p.suffix.lower(), 'classification':cls})
        if p.exists() and p.suffix.lower() in TEXT_EXT and p.stat().st_size < 5_000_000:
            try: hashes.append({'path':f,'sha256':sha256(p)})
            except Exception as e: hashes.append({'path':f,'sha256':'','error':repr(e)})
    dups=[{'basename':k,'count':len(v),'paths':' | '.join(v)} for k,v in names.items() if len(v)>1]
    stale=[r for r in inv if r['classification']=='NEEDS_HUMAN_REVIEW']
    runtime=[f for f in all_files if f in ['render.yaml','dashboard/backend/app.py','dashboard/frontend/package.json','scripts/system3_master_proof_orchestrator.py']]
    write_csv(d/'file_inventory.csv', inv, ['path','size','suffix','classification'])
    write_csv(d/'file_hashes.csv', hashes, ['path','sha256','error'])
    write_csv(d/'duplicate_candidates.csv', dups, ['basename','count','paths'])
    write_csv(d/'stale_backup_candidates.csv', stale, ['path','size','suffix','classification'])
    write_text(d/'runtime_authority_map.md', '# Runtime Authority Map\n\n'+'\n'.join(f'- `{x}`' for x in runtime)+'\n')
    write_text(d/'dependency_trace.md', 'Dependency trace placeholder: lightweight proof pack generated. Use AST/import trace in next phase for deeper proof.\n')
    write_text(d/'quarantine_plan.md', '# Quarantine Plan\n\nNo deletion performed. Review NEEDS_HUMAN_REVIEW and duplicate_candidates before any quarantine.\n')
    st='PASS' if inv and hashes else 'PARTIAL'
    summ={'status':st,'file_count':len(inv),'hash_count':len(hashes),'duplicate_basename_count':len(dups),'stale_review_count':len(stale),'deleted_files':0}
    write_json(d/'cleanup_summary.json', summ); archive(d,'repo_authority')
    return status('repo_authority','#28',st,'Repo authority proof pack created. No deletion performed.',[rel(x) for x in d.iterdir()],warnings=['deep dependency trace still needs enhancement'])

def benchmark(all_files):
    d=LATEST/'performance_benchmark'; d.mkdir(parents=True, exist_ok=True)
    pred=search(all_files,['prediction','signal','top5','rank','confidence','probability'])
    actual=search(all_files,['ohlc','candle','market data','top mover','gainer','quote'])
    blocked=[]
    if not pred: blocked.append('prediction_source_not_found')
    if not actual: blocked.append('actual_market_result_source_not_found')
    st='BLOCKED' if blocked else 'PARTIAL'
    write_csv(d/'prediction_vs_actual.csv', [], ['symbol','prediction_time','predicted_rank','actual_rank','direction_ok','notes'])
    write_csv(d/'top_mover_match.csv', [], ['symbol','predicted_top','actual_top','match','notes'])
    write_text(d/'missed_opportunities.md', '# Missed Opportunities\n\nNo computed rows yet. Source discovery required.\n')
    write_json(d/'source_manifest.json', {'prediction_candidates':pred[:80],'actual_candidates':actual[:80]})
    write_json(d/'status.json', {'status':st,'blockers':blocked,'prediction_candidate_count':len(pred),'actual_candidate_count':len(actual)})
    write_text(d/'benchmark_summary.md', f'# Performance Benchmark\n\nStatus: {st}\n\nBlockers: {blocked}\n\nNo performance claim is made.\n')
    archive(d,'performance_benchmark')
    return status('prediction_benchmark','#26',st,'Benchmark source discovery completed; no fake metrics generated.',[rel(x) for x in d.iterdir()],blocked)

def lifecycle(all_files):
    d=LATEST/'lifecycle_reconciliation'; d.mkdir(parents=True, exist_ok=True)
    cand=search(all_files,['lifecycle','paper','analyzer','sandbox','order','trade','position','fill','pnl'])
    st='PARTIAL' if cand else 'BLOCKED'
    blockers=[] if cand else ['lifecycle_source_not_found']
    write_csv(d/'signal_order_trade_join.csv', [], ['signal_id','symbol','order_id','trade_id','status','notes'])
    write_csv(d/'pnl_reconciliation.csv', [], ['symbol','entry','exit','qty','pnl','source','notes'])
    write_csv(d/'open_closed_positions.csv', [], ['symbol','position_status','qty','source','notes'])
    write_text(d/'mismatch_report.md', '# Mismatch Report\n\nNo computed mismatches yet. Source joins required.\n')
    write_json(d/'source_manifest.json', {'lifecycle_candidates':cand[:120]})
    write_json(d/'status.json', {'status':st,'blockers':blockers,'candidate_count':len(cand),'analyzer_paper_only':True})
    write_text(d/'lifecycle_summary.md', f'# Lifecycle Reconciliation\n\nStatus: {st}\n\nAnalyzer/Paper only. No live action.\n')
    archive(d,'lifecycle_reconciliation')
    return status('lifecycle_reconciliation','#27',st,'Lifecycle source discovery completed; no inferred fills used.',[rel(x) for x in d.iterdir()],blockers)

def dashboard(all_files):
    d=LATEST/'dashboard_browser_api_proof'; d.mkdir(parents=True, exist_ok=True)
    frontend=[f for f in all_files if f.startswith('dashboard/frontend/')]
    localhost=[]
    backtest=[]
    for f in frontend:
        txt=read(f).lower()
        if 'localhost' in txt: localhost.append(f)
        if 'backtest' in txt: backtest.append(f)
    api_files=search(all_files,['api_smoke','health/status','broker/status','/api/state','dashboard endpoint'])
    st='BLOCKED'
    blockers=['browser_screenshot_not_generated_in_github_static_run','local_backend_frontend_run_not_proven']
    if localhost: blockers.append('localhost_references_present')
    if not backtest: blockers.append('backtest_ui_reference_not_found')
    write_text(d/'localhost_reference_scan.txt','\n'.join(localhost) if localhost else 'No localhost references found in frontend scan.\n')
    write_text(d/'backtest_ui_proof.md','# Backtest UI Proof\n\n'+('\n'.join(f'- `{x}`' for x in backtest) if backtest else 'Backtest UI reference not found.'))
    write_json(d/'api_smoke_results.json', {'status':'BLOCKED','reason':'local backend/frontend browser run not executed by static script','api_candidates':api_files[:80]})
    write_json(d/'screenshot_manifest.json', {'status':'BLOCKED','screenshots':[],'reason':'browser screenshot capture requires local/browser runtime'})
    write_text(d/'frontend_build.log','Frontend build not run by this static GitHub-created proof script. Run locally for full proof.\n')
    write_text(d/'npm_audit_summary.md','# npm audit summary\n\nNot run by this static script. Run locally in dashboard/frontend.\n')
    write_json(d/'status.json', {'status':st,'blockers':blockers,'localhost_count':len(localhost),'backtest_reference_count':len(backtest)})
    write_text(d/'dashboard_browser_api_summary.md', f'# Dashboard Browser/API Proof\n\nStatus: {st}\n\nBlockers: {blockers}\n')
    archive(d,'dashboard_browser_api_proof')
    return status('dashboard_browser_api','#24',st,'Static dashboard scan completed; browser/API proof remains blocked until local run.',[rel(x) for x in d.iterdir()],blockers)

def main():
    all_files=files(); batch=LATEST/'implementation_batch'; batch.mkdir(parents=True, exist_ok=True)
    statuses=[]
    groups={
        'repo_authority':['runtime map','repo authority','duplicate','quarantine','hash'],
        'prediction_benchmark':['prediction_vs_actual','performance_benchmark','top_mover','missed_opportunity'],
        'lifecycle':['lifecycle_reconciliation','signal_order_trade','pnl_reconciliation','paper','analyzer'],
        'dashboard':['dashboard_browser_api','api_smoke','screenshot','localhost','backtest'],
    }
    findings={k:search(all_files,v) for k,v in groups.items()}
    write_json(batch/'search_findings.json', findings)
    write_text(batch/'search_findings.md', '# Search Findings\n\n'+'\n'.join(f'## {k}\nMatches: {len(v)}\n' for k,v in findings.items()))
    statuses.append(status('global_search','#25','PASS','Global search completed.',[rel(batch/'search_findings.md'),rel(batch/'search_findings.json')]))
    statuses.append(repo_authority(all_files))
    statuses.append(benchmark(all_files))
    statuses.append(lifecycle(all_files))
    statuses.append(dashboard(all_files))
    changed=cmd(['git','status','--short'])
    write_json(batch/'status_matrix.json', {'generated_utc':datetime.now(timezone.utc).isoformat(),'statuses':statuses})
    write_text(batch/'commands_run.md', '# Commands Run\n\n- git ls-files\n- git status --short\n')
    write_text(batch/'files_changed.md', '# Files Changed\n\n```\n'+(changed.get('stdout') or '')+'\n```\n')
    write_json(batch/'evidence_manifest.json', {'outputs':[s['outputs'] for s in statuses]})
    write_text(batch/'unresolved_blockers.md', '# Unresolved Blockers\n\n'+'\n'.join(f"## {s['phase']}\n"+'\n'.join(f"- {b}" for b in s['blockers']) for s in statuses if s['blockers']))
    write_text(batch/'implementation_summary.md', '# System3 Proof Batch Summary\n\nNo deletion. Analyzer/Paper only. No readiness/performance claim.\n')
    archive(batch,'implementation_batch')
    zip_path=LATEST/f'system3_proof_pack_{STAMP}.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for folder in ['repo_authority','performance_benchmark','lifecycle_reconciliation','dashboard_browser_api_proof','implementation_batch']:
            base=LATEST/folder
            if base.exists():
                for p in base.rglob('*'):
                    if p.is_file(): z.write(p, rel(p))
    print(json.dumps({'status':'COMPLETE_WITH_BLOCKERS','zip':rel(zip_path),'statuses':statuses}, indent=2))

if __name__ == '__main__':
    main()
