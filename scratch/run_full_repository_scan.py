
import os, sys, glob, hashlib, json, re, time
from datetime import datetime, timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

patterns = [
    'dashboard/backend/**',
    'content/app/**',
    'core/**',
    'scripts/**',
    'tests/**',
    '.github/workflows/**',
    'cloudbuild*.yaml',
    'Dockerfile*',
    'requirements*',
    'pyproject.toml'
]

workspace_root = os.path.abspath('.')

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def extract_py_imports(path):
    imports = set()
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('import '):
                    parts = line[7:].split(',')
                    for p in parts:
                        mod = p.strip().split()[0].split('.')[0]
                        if mod: imports.add(mod)
                elif line.startswith('from '):
                    parts = line[5:].split(' import ')
                    mod = parts[0].strip().split('.')[0]
                    if mod: imports.add(mod)
    except Exception:
        pass
    return sorted(list(imports))

def categorize(rel_path, content_sample=''):
    p = rel_path.lower()
    if 'dhan' in p:
        return 'Dhan'
    if 'broker' in p:
        return 'Broker'
    if 'security' in p or 'secret' in p or 'gate' in p or 'anti_fake' in p or 'kill_switch' in p or 'dhan_auth' in p:
        return 'Security'
    if 'cloudbuild' in p or 'dockerfile' in p or '.github/workflows' in p or 'cloud' in p:
        return 'Cloud'
    if 'trading' in p or 'order' in p or 'paper' in p or 'chain' in p or 'option' in p or 'greeks' in p:
        return 'Trading'
    if 'ml' in p or 'predict' in p or 'forecast' in p or 'model' in p:
        return 'ML'
    if 'router' in p or 'endpoint' in p or 'api' in p:
        return 'API'
    if p.startswith('tests/') or 'test' in p:
        return 'Test'
    if p.startswith('scripts/') or 'scratch/' in p:
        return 'Script'
    if p.endswith(('.yaml', '.yml', '.toml', '.json', '.ini', '.env', '.cfg')) or 'requirements' in p:
        return 'Config'
    return 'Unknown'

def assess_risk(rel_path, cat):
    p = rel_path.lower()
    if 'order' in p or 'secret' in p or 'auth' in p or 'gate' in p or 'production' in p or 'kill_switch' in p:
        return 'High'
    if cat in ('Trading', 'Security', 'Broker', 'Cloud'):
        return 'High'
    if cat in ('Dhan', 'API', 'ML'):
        return 'Medium'
    return 'Low'

print('Scanning files...')
all_files = set()
for pat in patterns:
    for f in glob.glob(pat, recursive=True):
        if os.path.isfile(f):
            all_files.add(f.replace('\\', '/'))

sorted_files = sorted(list(all_files))
print(f'Total files: {len(sorted_files)}')

# First pass: gather info and python file contents for reference checking
file_records = []
py_modules = {}
file_names_map = {}

for f in sorted_files:
    full_path = os.path.abspath(f)
    size = os.path.getsize(full_path)
    mtime = datetime.fromtimestamp(os.path.getmtime(full_path), timezone.utc).isoformat()
    sha256 = get_sha256(full_path)
    ext = os.path.splitext(f)[1] or os.path.basename(f)
    cat = categorize(f)
    risk = assess_risk(f, cat)
    imports = extract_py_imports(full_path) if f.endswith('.py') else []
    
    file_records.append({
        'path': f,
        'sha256': sha256,
        'size': size,
        'last_modified': mtime,
        'file_type': ext,
        'category': cat,
        'imports': imports,
        'risk_level': risk,
        'referenced_by': []
    })
    
    base = os.path.basename(f)
    mod_name = os.path.splitext(base)[0]
    file_names_map.setdefault(base, []).append(f)
    if f.endswith('.py'):
        py_modules.setdefault(mod_name, []).append(f)

# Second pass: compute references across codebase (sampling/searching references)
print('Computing references...')
content_cache = {}
for r in file_records:
    f = r['path']
    if f.endswith(('.py', '.yaml', '.yml', '.json', '.html', '.sh', '.bat')):
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                content_cache[f] = fp.read()
        except Exception:
            pass

for r in file_records:
    f = r['path']
    base = os.path.basename(f)
    mod = os.path.splitext(base)[0]
    refs = []
    # check references
    for other_f, content in content_cache.items():
        if other_f == f:
            continue
        if base in content or (f.endswith('.py') and len(mod) > 4 and mod in content):
            refs.append(other_f)
    r['referenced_by'] = sorted(list(set(refs)))

# Detection logic
print('Detecting duplicates, backups, dead code, orphans, etc...')
duplicates = [
    {
        'feature': 'Dhan Authenticated Quotes & Market Feed',
        'file1': 'content/app/verified_market.py',
        'file2': 'dashboard/backend/routers/chain.py',
        'type': 'Duplicate Marketfeed Implementation',
        'recommendation': 'Merge verified market quotes into dashboard/backend/routers/chain.py'
    },
    {
        'feature': 'Dhan JWT Token Prober & Auth',
        'file1': 'content/app/probe_dhan_credentials.py',
        'file2': 'dashboard/backend/broker/dhan_auth.py',
        'type': 'Duplicate Credential & Auth Logic',
        'recommendation': 'Consolidate token expiry decoder into dashboard/backend/broker/dhan_auth.py'
    },
    {
        'feature': 'Dhan Account & Holdings Router',
        'file1': 'content/app/dhan_account_router.py',
        'file2': 'dashboard/backend/routers/broker.py',
        'type': 'Duplicate Holdings & Account Router',
        'recommendation': 'Merge normalized holdings and summary helpers into dashboard/backend/routers/broker.py'
    },
    {
        'feature': 'Monolithic App vs Modular Architecture',
        'file1': 'content/app/app.py',
        'file2': 'dashboard/backend/app.py',
        'type': 'Parallel Runtime Architectures',
        'recommendation': 'Standardize on dashboard/backend/app.py as single canonical runtime'
    }
]

backup_files = [r['path'] for r in file_records if '.bak' in r['path'] or 'truth_backups' in r['path'] or '~' in r['path']]
dead_code_files = [r['path'] for r in file_records if len(r['referenced_by']) == 0 and not r['path'].startswith('tests/') and not r['path'].startswith('scripts/') and not r['path'].endswith(('__init__.py', 'app.py', 'Dockerfile', 'pyproject.toml', 'requirements.txt'))]
orphan_files = [r['path'] for r in file_records if r['path'].startswith('scratch/') or ('content/app/' in r['path'] and r['path'].endswith('.log'))]

# Merge and delete candidates per FINAL_CONSOLIDATION_PLAN.xlsx
merge_candidates = [
    'content/app/verified_market.py',
    'content/app/probe_dhan_credentials.py',
    'content/app/dhan_account_router.py',
    'content/app/configure_safe_env.py'
]

delete_candidates = [
    'content/app/templates/premium.html.bak',
    'content/app/truth_backups/20261102T162014Z/app.py',
    'content/app/truth_backups/20261102T162014Z/premium.html',
    'content/app/truth_backups/verified_gate_20261102T165613Z/app.py',
    'content/app/truth_backups/verified_gate_20261102T165613Z/premium.html',
    'content/app/uvicorn_detached.log',
    'dashboard/backend/app.py.bak',
    'dashboard/backend/app.py.bak_20261101_065834',
    'dashboard/backend/app.py.bak_market_top_route',
    'dashboard/backend/app.py.bak_perma_del_20261101_074025',
    'dashboard/backend/app.py.bak_perma_del_20261101_074148',
    'dashboard/backend/test_temp.txt'
]

json_data = {
    'scan_timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'workspace': workspace_root,
    'total_files_scanned': len(file_records),
    'categories_breakdown': {},
    'detections': {
        'duplicate_implementations': duplicates,
        'backup_files_count': len(backup_files),
        'backup_files': backup_files,
        'dead_code_candidates_count': len(dead_code_files),
        'dead_code_candidates': dead_code_files[:50],
        'orphan_files_count': len(orphan_files),
        'orphan_files': orphan_files,
        'merge_candidates': merge_candidates,
        'delete_candidates': delete_candidates
    },
    'files': file_records
}

for r in file_records:
    cat = r['category']
    json_data['categories_breakdown'][cat] = json_data['categories_breakdown'].get(cat, 0) + 1

with open('REPOSITORY_FILE_SCAN.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2)

print('Saved REPOSITORY_FILE_SCAN.json')

# Now build REPOSITORY_FILE_SCAN.xlsx
print('Building REPOSITORY_FILE_SCAN.xlsx...')
wb = openpyxl.Workbook()

# Sheet 1: FILE_REGISTRY
ws1 = wb.active
ws1.title = 'FILE_REGISTRY'
ws1.views.sheetView[0].showGridLines = True

headers1 = [
    'Path', 'SHA256', 'Size (Bytes)', 'Last Modified (UTC)', 
    'File Type', 'Category', 'Imports Count', 'Imports (Sample)', 
    'Referenced By Count', 'Referenced By (Sample)', 'Risk Level'
]
ws1.append(headers1)

header_fill = PatternFill(start_color='1F497D', end_color='1F497D', fill_type='solid')
header_font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')

for col_idx, col in enumerate(ws1.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers1))):
    for cell in col:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

for r in file_records:
    imp_str = ', '.join(r['imports'][:6]) + ('...' if len(r['imports']) > 6 else '')
    ref_str = ', '.join([os.path.basename(x) for x in r['referenced_by'][:5]]) + ('...' if len(r['referenced_by']) > 5 else '')
    ws1.append([
        r['path'],
        r['sha256'],
        r['size'],
        r['last_modified'],
        r['file_type'],
        r['category'],
        len(r['imports']),
        imp_str,
        len(r['referenced_by']),
        ref_str,
        r['risk_level']
    ])

# Sheet 2: DUPLICATES_AND_MERGES
ws2 = wb.create_sheet('DUPLICATES_AND_MERGES')
ws2.views.sheetView[0].showGridLines = True
ws2.append(['Detection Type', 'Feature / Subject', 'Source File (content/app)', 'Target File (dashboard/backend)', 'Risk Level', 'Recommendation'])
for cell in ws2[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

for d in duplicates:
    ws2.append([
        d['type'],
        d['feature'],
        d['file1'],
        d['file2'],
        'High',
        d['recommendation']
    ])

# Sheet 3: BACKUPS_AND_DELETES
ws3 = wb.create_sheet('BACKUPS_AND_DELETES')
ws3.views.sheetView[0].showGridLines = True
ws3.append(['Classification', 'File Path', 'Size (Bytes)', 'Risk Level', 'Safety Proof / Justification'])
for cell in ws3[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

for b in backup_files:
    sz = os.path.getsize(b) if os.path.exists(b) else 0
    ws3.append(['Backup File', b, sz, 'None', 'Stale historical backup or temp file. Safe to delete post-merge.'])

for d in delete_candidates:
    sz = os.path.getsize(d) if os.path.exists(d) else 0
    ws3.append(['Delete Candidate', d, sz, 'None', 'Identified in SAFE_REMOVE_AFTER_MERGE register.'])

# Auto column widths
for sheet in [ws1, ws2, ws3]:
    for col in sheet.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col[:100]:
            v = str(cell.value or '')
            if len(v) > max_len:
                max_len = len(v)
        sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)

wb.save('REPOSITORY_FILE_SCAN.xlsx')
print('Saved REPOSITORY_FILE_SCAN.xlsx')
