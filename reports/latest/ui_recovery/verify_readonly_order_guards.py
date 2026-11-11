import os,json,datetime,pathlib,sys
root=pathlib.Path(r'C:\Genesis_System3_clean')
sys.path.insert(0,str(root))
from core.brokers.dhan.dhan_readonly import DhanReadOnly
names=('place_order','modify_order','cancel_order','place_super_order','modify_super_order','cancel_super_order','place_forever','modify_forever','cancel_forever','place_slice_order','kill_switch')
checks={}
for name in names:
 try:
  getattr(DhanReadOnly,name)(object())
  checks[name]='FAIL_RETURNED'
 except RuntimeError:
  checks[name]='PASS_BLOCKED'
 except Exception as exc:
  checks[name]='FAIL_'+type(exc).__name__
env={}
for line in (root/'.env').read_text(encoding='utf-8-sig').splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  k,v=line.split('=',1)
  if k in ('PAPER_MODE','LIVE_TRADING_ENABLED','LIVE_ORDER_AUTHORITY','REAL_BROKER_ORDERS','AUTO_EXECUTE_TRADES'):env[k]=v.strip()
expected={'PAPER_MODE':'1','LIVE_TRADING_ENABLED':'0','LIVE_ORDER_AUTHORITY':'0','REAL_BROKER_ORDERS':'0','AUTO_EXECUTE_TRADES':'0'}
report={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'env_checks':{k:env.get(k)==v for k,v in expected.items()},'readonly_order_guards':checks,'scope':'DhanReadOnly adapter methods only; not all broker paths or deployed cloud'}
out=root/'reports/latest/ui_recovery/READONLY_ORDER_GUARDS.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ENV',sum(report['env_checks'].values()),'/',len(expected),'ORDER_GUARDS',sum(v=='PASS_BLOCKED' for v in checks.values()),'/',len(checks),'REPORT',out)
assert all(report['env_checks'].values()) and all(v=='PASS_BLOCKED' for v in checks.values())
