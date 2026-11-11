"""Comprehensive Forensic Scanner for Genesis System3 Environment Variables.
Scans the entire repository for environment variable references across Python,
TypeScript/JavaScript, Shell scripts, JSON, and YAML configs.
"""
import os
import re
import json
from collections import defaultdict

ENV_VAR_REGEX = re.compile(
    r'(?:'
    r'os\.environ\.get\s*\(\s*[\'"]([A-Z0-9_]+)[\'"]|'
    r'os\.getenv\s*\(\s*[\'"]([A-Z0-9_]+)[\'"]|'
    r'os\.environ\[\s*[\'"]([A-Z0-9_]+)[\'"]|'
    r'process\.env\.([A-Z0-9_]+)|'
    r'import\.meta\.env\.([A-Z0-9_]+)|'
    r'\b([A-Z][A-Z0-9_]{3,})\b\s*=\s*(?:os\.getenv|os\.environ\.get)'
    r')'
)

EXCLUDED_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build', '.agy-proof'}
ROOT_DIR = r'C:\Genesis_System3_clean'

env_findings = defaultdict(lambda: {'count': 0, 'files': set()})

for root, dirs, files in os.walk(ROOT_DIR):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
    for file in files:
        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.sh', '.ps1', '.json', '.yml', '.yaml', '.example', '.env')):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, ROOT_DIR).replace('\\', '/')
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = ENV_VAR_REGEX.findall(content)
                    for groups in matches:
                        for item in groups:
                            if item:
                                env_findings[item]['count'] += 1
                                env_findings[item]['files'].add(relpath)
            except Exception as e:
                pass

print(f"Total Unique Environment Variables Found: {len(env_findings)}")
report = []
for k in sorted(env_findings.keys()):
    files_list = sorted(list(env_findings[k]['files']))
    report.append({
        'variable': k,
        'count': env_findings[k]['count'],
        'file_count': len(files_list),
        'files': files_list
    })

output_path = os.path.join(ROOT_DIR, 'reports', 'latest', 'env_forensic_inventory.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as out_f:
    json.dump(report, out_f, indent=2)

print(f"Forensic Inventory Saved to: {output_path}")

# Print categorized summary of the top variables
print("\n--- Categorized Top Variables ---")
for item in report[:40]:
    print(f"{item['variable']}: {item['file_count']} files, {item['count']} refs")
