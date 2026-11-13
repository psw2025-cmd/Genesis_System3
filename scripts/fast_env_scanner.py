"""Fast forensic scanner for Genesis System3 environment variables.
Scans source directories only: core, dashboard, content, config, scripts, tools, tests, deploy.
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
    r'import\.meta\.env\.([A-Z0-9_]+)'
    r')'
)

TARGET_DIRS = ['core', 'dashboard', 'content', 'config', 'scripts', 'tools', 'tests', 'deploy']
ROOT_DIR = r'C:\Genesis_System3_clean'

env_findings = defaultdict(lambda: {'count': 0, 'files': set()})

for target in TARGET_DIRS:
    target_path = os.path.join(ROOT_DIR, target)
    if not os.path.exists(target_path):
        continue
    for root, dirs, files in os.walk(target_path):
        # Exclude caches and build artifacts
        dirs[:] = [d for d in dirs if d not in {'__pycache__', 'dist', 'build', 'node_modules', '.venv'}]
        for file in files:
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.sh', '.json', '.yml', '.yaml')):
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
                except Exception:
                    pass

# Also check root-level scripts/configs
for root_file in ['.env.example', 'kill_switch.json', 'agent_policy.yaml']:
    filepath = os.path.join(ROOT_DIR, root_file)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = re.findall(r'^[A-Z0-9_]+(?==)', content, re.MULTILINE)
                for item in matches:
                    env_findings[item]['count'] += 1
                    env_findings[item]['files'].add(root_file)
        except Exception:
            pass

report = []
for k in sorted(env_findings.keys()):
    files_list = sorted(list(env_findings[k]['files']))
    report.append({
        'variable': k,
        'count': env_findings[k]['count'],
        'file_count': len(files_list),
        'files': files_list
    })

output_path = os.path.join(ROOT_DIR, 'reports', 'latest', 'fast_env_inventory.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as out_f:
    json.dump(report, out_f, indent=2)

print(f"Total Unique Environment Variables Found: {len(report)}")
for item in report:
    print(f"{item['variable']}: {item['file_count']} files, {item['count']} refs")
