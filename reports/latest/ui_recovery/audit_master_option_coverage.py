import csv,collections,json,datetime,pathlib
root=pathlib.Path(r'C:\Genesis_System3_clean')
src=root/'storage/instruments/api-scrip-master-detailed.csv'
with src.open(encoding='utf-8-sig',newline='') as f:
 r=csv.DictReader(f); counts=collections.Counter(); names=collections.defaultdict(set); examples=[]
 for row in r:
  instr=(row.get('INSTRUMENT') or '').upper()
  seg=(row.get('SEGMENT') or '').upper()
  exch=(row.get('EXCH_ID') or '').upper()
  if 'OPT' not in instr:continue
  counts[(exch,seg,instr)]+=1
  sym=(row.get('UNDERLYING_SYMBOL') or '').strip()
  if sym:names[(exch,seg,instr)].add(sym)
  if len(examples)<8:examples.append({k:row.get(k) for k in ['EXCH_ID','SEGMENT','INSTRUMENT','UNDERLYING_SYMBOL','SECURITY_ID','SM_EXPIRY_DATE','STRIKE_PRICE','OPTION_TYPE']})
data={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':[{'exchange':k[0],'segment':k[1],'instrument':k[2],'contracts':v,'underlyings':len(names[k]),'symbols':sorted(names[k])} for k,v in counts.items()],'examples':examples}
out=root/'reports/latest/ui_recovery/MASTER_OPTION_COVERAGE.json'
out.write_text(json.dumps(data,indent=2),encoding='utf-8')
for x in data['groups']:print(x['exchange'],x['segment'],x['instrument'],'CONTRACTS',x['contracts'],'SYMBOLS',x['underlyings'],'FIRST',','.join(x['symbols'][:8]))
print('OUTPUT',out)
