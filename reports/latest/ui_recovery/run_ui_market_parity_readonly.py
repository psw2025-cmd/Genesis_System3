import json,urllib.request,datetime,pathlib,hashlib,collections
root=pathlib.Path(r'C:\Genesis_System3_clean'); out=root/'reports/latest/ui_recovery'; base='http://127.0.0.1:8008'
routes=['/api/health','/api/market/inventory','/api/data/provenance','/api/chain/NIFTY','/api/market/top-gainers','/api/options/gainers','/api/ml/prediction-audit','/api/paper/ledger','/api/verified-market']
def compact(o,depth=0):
 if depth>2:return type(o).__name__
 if isinstance(o,dict):return {k:compact(v,depth+1) for k,v in o.items() if k.lower() not in ('client_id','access_token','token','account_number','account_id','holdings','positions','orders','demat','funds','cash','email','phone')}
 if isinstance(o,list):return {'count':len(o),'first_item_shape':compact(o[0],depth+1) if o else None}
 return o if isinstance(o,(int,float,bool,type(None))) else str(o)[:100]
results=[]
for route in routes:
 try:
  with urllib.request.urlopen(base+route,timeout=9) as resp:
   raw=resp.read(2_000_000);obj=json.loads(raw)
  dat=obj.get('data',{})
  entry={'route':route,'http':resp.status,'response_bytes':len(raw),'top_keys':list(obj),'real_flag':obj.get('real'),'timestamp':obj.get('timestamp'),'provenance':compact(obj.get('provenance',{})),'data_shape':compact(dat),'sha256':hashlib.sha256(raw).hexdigest()}
  if isinstance(dat,dict):entry['data_keys']=list(dat.keys());entry['numeric_counts']={k:v for k,v in dat.items() if isinstance(v,(int,float)) and any(x in k.lower() for x in ('count','total','symbol','instrument','contract','underlying'))}
  results.append(entry)
 except Exception as e:results.append({'route':route,'error':type(e).__name__+': '+str(e)[:150]})
path=out/'UI_MARKET_PARITY_READONLY_20261104.json';path.write_text(json.dumps({'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'routes':results},indent=2,ensure_ascii=False),encoding='utf-8')
for x in results:print(x['route'],x.get('http','ERR'),'real=',x.get('real_flag'),'timestamp=',x.get('timestamp'),'data_keys=',x.get('data_keys'),'counts=',x.get('numeric_counts'),'error=',x.get('error'))
print('EVIDENCE',path)
