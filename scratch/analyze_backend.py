import os
import re

def analyze_backend():
    with open('dashboard/backend/app.py', 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    print("=== Analyzing dashboard/backend/app.py ===")
    print("Length:", len(code), "bytes,", code.count('\n'), "lines")
    
    # Imports
    imports = re.findall(r'^(?:from\s+[\w\.]+\s+import.*|import\s+[\w\.,\s]+)', code, re.MULTILINE)
    print("\nImports count:", len(imports))
    for imp in imports[:30]:
        print(" ", imp.strip())

    # Routers included
    router_includes = re.findall(r'app\.include_router\(([^)]+)\)', code)
    print("\nRouter includes:", len(router_includes))
    for r in router_includes:
        print("  include_router:", r.strip().replace('\n', ' '))

    # Routes in app.py directly
    route_matches = re.findall(r'@(?:app|api_router)\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']', code)
    print(f"\nDirect routes in app.py: {len(route_matches)}")
    for r in route_matches[:25]:
        print(f"  {r[0].upper():6} {r[1]}")

if __name__ == '__main__':
    analyze_backend()
