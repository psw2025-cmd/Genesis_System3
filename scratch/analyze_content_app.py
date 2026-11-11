import os
import re

def analyze_content_app():
    with open('content/app/app.py', 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    print("=== Analyzing content/app/app.py ===")
    print("Length:", len(code), "bytes,", code.count('\n'), "lines")
    
    # Imports
    imports = re.findall(r'^(?:from\s+[\w\.]+\s+import.*|import\s+[\w\.,\s]+)', code, re.MULTILINE)
    print("\nImports count:", len(imports))
    for imp in imports[:20]:
        print(" ", imp.strip())

    # Classes
    classes = re.findall(r'^class\s+(\w+)(?:\(([^)]*)\))?:', code, re.MULTILINE)
    print("\nClasses defined:", len(classes))
    for c in classes:
        print("  Class:", c[0], "(inherits:", c[1], ")")

    # Functions (top level or key)
    funcs = re.findall(r'^(?:async\s+def|def)\s+([a-zA-Z0-9_]+)\s*\(', code, re.MULTILINE)
    print("\nTop-level / async funcs defined:", len(funcs))
    for fn in funcs[:30]:
        print("  Func:", fn)

    # Routes
    route_matches = re.findall(r'@(?:app|router|api_router)\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']', code)
    print(f"\nRoutes in app.py: {len(route_matches)}")
    for r in route_matches:
        print(f"  {r[0].upper():6} {r[1]}")

if __name__ == '__main__':
    analyze_content_app()
