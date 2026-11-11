import csv,json,time,datetime,pathlib,urllib.request
root=pathlib.Path(r'C:\Genesis_System3_clean')
out=root/'reports/latest/ui_recovery/EQUITY_219_PAPER_READINESS.json'
from core.brokers.dhan.equity_fo_universe import resolve_equity_security_master
master=resolve_equity_security_master()
with master.open(encoding='utf-8-sig',newline='') as f:
 r=csv.DictReader(f)
 columns=r.fieldnames or []
 rows=list(r)
print('MASTER',str(master),'ROWS',len(rows),'COLUMNS',columns[:20])
chains=root/'state/chain_cache'
files=list(chains.glob('*.json'))
fresh=[p for p in files if 0<=time.time()-p.stat().st_mtime<=180]
def api(path):
 try:
  with urllib.request.urlopen('http://127.0.0.1:8021'+path,timeout=15) as r:return json.load(r)
 except Exception as e:return {'error':type(e).__name__}
inventory=api('/api/market/inventory')
health=api('/api/health')
ledger=api('/api/paper/ledger')
report={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'master_path':str(master),'master_rows':len(rows),'master_columns':columns,'cached_chain_symbols':[p.stem for p in files],'fresh_cache_symbols':[p.stem for p in fresh],'equity_cached_symbols':[p.stem for p in files if p.stem not in {'NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY','SENSEX','BANKEX'}],'inventory':inventory.get('data',{}),'paper_safety':{k:health.get('data',{}).get(k) for k in ('paper_mode','live_trading_enabled','live_order_authority')},'paper_ledger':{'keys':list(ledger.get('data',{})) if isinstance(ledger.get('data'),dict) else [],'status':ledger.get('data',{}).get('status') if isinstance(ledger.get('data'),dict) else None}}
out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print('CACHED_EQUITY',report['equity_cached_symbols'],'FRESH',len(fresh),'SAFETY',report['paper_safety'],'LEDGER',report['paper_ledger'],'OUTPUT',out)
