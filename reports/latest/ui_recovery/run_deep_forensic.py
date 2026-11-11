import os,subprocess,hashlib,ast,json,re,collections,datetime,pathlib
ROOT=pathlib.Path(r'C:\Genesis_System3_clean'); OUT=ROOT/'reports/latest/ui_recovery'
raw=subprocess.run(['git','-C',str(ROOT),'-c','core.quotepath=false','ls-files','-z'],capture_output=True).stdout
paths=[x.decode('utf-8','surrogateescape') for x in raw.split(b'\0') if x]
records=[]; errors=[]
for rel in paths:
 try:
  p=ROOT/rel
  if not p.is_file(): continue
  if any(x in rel.lower() for x in ('.secrets/','node_modules/','.venv/')):continue
  if p.suffix.lower() not in ('.py','.ts','.tsx','.md','.json','.yml','.yaml','.ps1'):continue
  if re.search(r'(^|/)(\.env|secret|credential|private_key)',rel,re.I):continue
  size=p.stat().st_size
  digest=hashlib.sha256(p.read_bytes()).hexdigest() if size<=2097152 else None
  records.append({'path':rel,'name':p.name,'size':size,'sha256':digest})
 except Exception as e: errors.append({'path':rel,'error':type(e).__name__})
groups=collections.defaultdict(list)
for r in records:
 if r['sha256'] and r['size']>0:groups[r['sha256']].append(r['path'])
duplicates=[v for v in groups.values() if len(v)>1]
namegroups=collections.defaultdict(list)
for r in records:namegroups[r['name'].lower()].append(r['path'])
names=[v for k,v in namegroups.items() if len(v)>1 and k!='__init__.py']
ast_errors=[];imports=[];danger=[];tokens=[];data_refs=[]
targets=[r for r in records if r['path'].endswith('.py') and (r['path'].startswith(('core/','dashboard/backend/','scripts/','src/')))]
for r in targets:
 p=ROOT/r['path']
 try:
  src=p.read_text(encoding='utf-8-sig',errors='replace')
  tree=ast.parse(src,filename=r['path'])
  for n in ast.walk(tree):
   if isinstance(n,ast.ImportFrom) and n.module:imports.append({'file':r['path'],'module':n.module,'line':n.lineno})
   if isinstance(n,ast.Call):
    fun=n.func
    name=fun.attr if isinstance(fun,ast.Attribute) else fun.id if isinstance(fun,ast.Name) else ''
    if name in ('place_order','cancel_order','modify_order','generateSession','read_csv','read_json','to_csv','to_json','getenv'):
     if name=='getenv':continue
     danger.append({'file':r['path'],'line':n.lineno,'call':name})
 except (SyntaxError,IndentationError) as e:ast_errors.append({'file':r['path'],'line':e.lineno,'error':str(e.msg)})
 except Exception as e:errors.append({'path':r['path'],'error':type(e).__name__})
result={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_tracked_count':len(paths),'scanned_files':len(records),'python_parsed':len(targets)-len(ast_errors),'python_parse_errors':ast_errors,'exact_duplicate_groups':duplicates,'repeated_non_init_basenames':names,'sensitive_call_sites':danger,'errors':errors}
(OUT/'GENESIS_DEEP_FORENSIC_AST_HASH.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# Deep forensic: Git NUL-path, SHA256, Python AST','',f'Tracked paths: {len(paths)}; scanned files: {len(records)}; Python parsed: {result["python_parsed"]}; parse failures: {len(ast_errors)}; exact duplicate content groups: {len(duplicates)}; repeated non-init basenames: {len(names)}; sensitive call sites: {len(danger)}; scan errors: {len(errors)}.','','## Exact SHA-256 duplicate groups']
for i,g in enumerate(duplicates,1):lines+=['','### DUP-'+str(i),*['- '+v for v in g]]
lines+=['','## Repeated filenames (non __init__.py)']
for i,g in enumerate(names,1):lines+=['','### NAME-'+str(i),*['- '+v for v in g]]
lines+=['','## Python syntax parse errors']
for x in ast_errors:lines.append('- '+x['file']+':'+str(x['line'])+' '+x['error'])
lines+=['','## Sensitive call site sample (full JSON includes all)']
for x in danger[:100]:lines.append('- '+x['file']+':'+str(x['line'])+' '+x['call'])
lines+=['','## Scan errors']
for x in errors[:50]:lines.append('- '+x['path']+' '+x['error'])
(OUT/'GENESIS_DEEP_FORENSIC_AST_HASH.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k in ('git_tracked_count','scanned_files','python_parsed')},ensure_ascii=False))
print('AST_ERRORS',len(ast_errors),'DUPLICATE_HASH_GROUPS',len(duplicates),'REPEATED_NAMES',len(names),'CALL_SITES',len(danger),'SCAN_ERRORS',len(errors))
print('TOP_DUPLICATES',json.dumps(duplicates[:8],ensure_ascii=False)[:2800])
print('AST_ERRORS_SAMPLE',json.dumps(ast_errors[:10],ensure_ascii=False)[:1500])
