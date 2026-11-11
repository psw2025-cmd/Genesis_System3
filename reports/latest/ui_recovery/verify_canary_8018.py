import json,urllib.request,datetime,pathlib,sys
out=pathlib.Path(r'C:\Genesis_System3_clean\reports\latest\ui_recovery')
def get(port,path):
 with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=10) as r:
  assert r.status==200
  return json.load(r)
checks=[]
def check(name,condition,detail):
 checks.append({'name':name,'pass':bool(condition),'detail':detail})
old_h=get(8008,'/api/health');new_h=get(8018,'/api/health')
old_i=get(8008,'/api/market/inventory');new_i=get(8018,'/api/market/inventory')
old_m=get(8008,'/api/market');new_m=get(8018,'/api/market')
old_r=get(8008,'/api/route-health');new_r=get(8018,'/api/route-health')
check('health_inventory_equal',new_h['data']['verified_chain_contracts']==new_i['data']['verified_chain_contracts_count'],[new_h['data']['verified_chain_contracts'],new_i['data']['verified_chain_contracts_count']])
check('inventory_no_false_live',new_i['real'] is False and new_i['provenance']['exchange_feed_verified'] is False,new_i['provenance']['classification'])
check('market_no_false_live',new_m['real'] is False,new_m['real'])
check('route_health_no_fake_telemetry',new_r['real'] is False and new_r['data']['overall_health']=='NOT_VERIFIED',new_r['data']['overall_health'])
check('paper_safety',new_h['data']['paper_mode'] is True and new_h['data']['live_trading_enabled'] is False and new_h['data']['live_order_authority']==0,'paper=true live=false authority=0')
check('old_mismatch_reproduced',old_h['data']['verified_chain_contracts']!=old_i['data']['verified_chain_contracts_count'],[old_h['data']['verified_chain_contracts'],old_i['data']['verified_chain_contracts_count']])
check('old_mislabel_reproduced',old_i['real'] is True and old_m['real'] is True and old_r['real'] is True,'old three routes real=true')
report={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canary_port':8018,'old_port':8008,'checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks)}
f=out/'CANARY_8018_BEFORE_AFTER_PROOF.json';f.write_text(json.dumps(report,indent=2),encoding='utf-8')
for c in checks:print(('PASS' if c['pass'] else 'FAIL'),c['name'],c['detail'])
print('EVIDENCE',f)
sys.exit(0 if report['passed']==report['total'] else 1)
