import os
import re
import ast

def inspect_routes():
    pattern = re.compile(r'@(?:app|router|api_router)\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
    
    def scan_dir(base_dir, ignore_terms=None):
        if ignore_terms is None:
            ignore_terms = []
        routes = []
        for root, dirs, files in os.walk(base_dir):
            if any(term in root for term in ignore_terms):
                continue
            for f in files:
                if f.endswith('.py') and not any(term in f for term in ignore_terms):
                    p = os.path.join(root, f)
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    for m in pattern.finditer(content):
                        method = m.group(1).upper()
                        path = m.group(2)
                        pos = m.end()
                        fn_match = re.search(r'(?:async\s+def|def)\s+([a-zA-Z0-9_]+)', content[pos:pos+300])
                        fn = fn_match.group(1) if fn_match else 'unknown'
                        routes.append({
                            'method': method,
                            'path': path,
                            'func': fn,
                            'file': os.path.relpath(p, base_dir)
                        })
        return routes

    c_routes = scan_dir('content/app', ignore_terms=['truth_backups', '__pycache__', '.bak'])
    d_routes = scan_dir('dashboard/backend', ignore_terms=['__pycache__', '.bak', 'bak_'])

    print(f"Content/app routes count: {len(c_routes)}")
    print(f"Dashboard/backend routes count: {len(d_routes)}")

    # Sample routes
    print("\nContent/app unique paths:", len(set(r['path'] for r in c_routes)))
    print("Dashboard/backend unique paths:", len(set(r['path'] for r in d_routes)))

    # Find overlap
    c_paths = set(r['path'] for r in c_routes)
    d_paths = set(r['path'] for r in d_routes)

    overlap = c_paths.intersection(d_paths)
    print(f"\nPaths in both: {len(overlap)}")
    print(f"Paths in content only: {len(c_paths - d_paths)}")
    print(f"Paths in dashboard only: {len(d_paths - c_paths)}")

    with open('scratch_routes_summary.txt', 'w', encoding='utf-8') as out:
        out.write(f"Content/app total routes: {len(c_routes)}\n")
        out.write(f"Dashboard/backend total routes: {len(d_routes)}\n")
        out.write(f"Overlap: {len(overlap)}\n")
        out.write(f"Content only: {len(c_paths - d_paths)}\n")
        out.write(f"Dashboard only: {len(d_paths - c_paths)}\n\n")

        out.write("--- SAMPLE OVERLAP ---\n")
        for p in sorted(list(overlap))[:30]:
            out.write(f"{p}\n")
            
        out.write("\n--- SAMPLE CONTENT ONLY ---\n")
        for p in sorted(list(c_paths - d_paths))[:30]:
            out.write(f"{p}\n")

        out.write("\n--- SAMPLE DASHBOARD ONLY ---\n")
        for p in sorted(list(d_paths - c_paths))[:30]:
            out.write(f"{p}\n")

if __name__ == '__main__':
    inspect_routes()
