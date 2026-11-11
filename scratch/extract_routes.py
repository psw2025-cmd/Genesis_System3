import os
import re

def parse_fastapi_routes(file_path):
    routes = []
    if not os.path.exists(file_path):
        return routes
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    current_decorator = None
    decorator_line = 0
    route_regex = re.compile(r'@(?:app|router|api_router)\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)

    for i, line in enumerate(lines):
        m = route_regex.search(line)
        if m:
            method = m.group(1).upper()
            path = m.group(2)
            # Find the function definition
            func_name = "unknown"
            docstring = ""
            for j in range(i+1, min(i+15, len(lines))):
                fn_m = re.match(r'^(?:async\s+def|def)\s+([a-zA-Z0-9_]+)\s*\(', lines[j].strip())
                if fn_m:
                    func_name = fn_m.group(1)
                    # check for docstring
                    for k in range(j+1, min(j+10, len(lines))):
                        if '"""' in lines[k] or "'''" in lines[k]:
                            docstring = lines[k].strip().strip('"""').strip("'''")
                            break
                    break
            routes.append({
                'method': method,
                'path': path,
                'func': func_name,
                'line': i + 1,
                'doc': docstring,
                'file': file_path
            })
    return routes

# Scan content/app
content_routes = []
for root, dirs, files in os.walk('content/app'):
    if 'truth_backups' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            content_routes.extend(parse_fastapi_routes(os.path.join(root, f)))

# Scan dashboard/backend
dashboard_routes = []
for root, dirs, files in os.walk('dashboard/backend'):
    if '__pycache__' in root or '.bak' in root:
        continue
    for f in files:
        if f.endswith('.py') and not 'bak' in f:
            dashboard_routes.extend(parse_fastapi_routes(os.path.join(root, f)))

print(f"Content routes: {len(content_routes)}")
print(f"Dashboard routes: {len(dashboard_routes)}")

with open('scratch_all_routes.txt', 'w', encoding='utf-8') as out:
    out.write("=== CONTENT ROUTES ===\n")
    for r in sorted(content_routes, key=lambda x: (x['path'], x['method'])):
        out.write(f"{r['method']:6} {r['path']:40} {r['func']:30} {r['file']}:{r['line']}\n")
    out.write("\n=== DASHBOARD ROUTES ===\n")
    for r in sorted(dashboard_routes, key=lambda x: (x['path'], x['method'])):
        out.write(f"{r['method']:6} {r['path']:40} {r['func']:30} {r['file']}:{r['line']}\n")

print("Saved scratch_all_routes.txt")
