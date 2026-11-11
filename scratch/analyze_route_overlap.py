import re
import os

with open('scratch_all_routes.txt', 'r', encoding='utf-8') as f:
    text = f.read()

parts = text.split('=== DASHBOARD ROUTES ===')
content_part = parts[0].replace('=== CONTENT ROUTES ===', '').strip()
dash_part = parts[1].strip()

def parse_lines(section):
    routes = []
    for line in section.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(GET|POST|PUT|DELETE|PATCH)\s+(\S+)\s+(\S+)\s+(\S+):(\d+)', line)
        if m:
            routes.append({
                'method': m.group(1),
                'path': m.group(2),
                'func': m.group(3),
                'file': m.group(4),
                'line': int(m.group(5))
            })
    return routes

c_routes = parse_lines(content_part)
d_routes = parse_lines(dash_part)

print(f"Parsed {len(c_routes)} content routes and {len(d_routes)} dashboard routes.")

# Let's inspect route collisions / overlaps
c_map = {(r['method'], r['path']): r for r in c_routes}
d_map = {(r['method'], r['path']): r for r in d_routes}

overlap = set(c_map.keys()).intersection(set(d_map.keys()))
print(f"Exact (method, path) matches: {len(overlap)}")
for m, p in sorted(overlap):
    print(f"  {m:6} {p:35} -> Content: {c_map[(m,p)]['file']}:{c_map[(m,p)]['line']} | Dash: {d_map[(m,p)]['file']}:{d_map[(m,p)]['line']}")

# Let's inspect paths where method might differ or similar paths
c_paths = set(r['path'] for r in c_routes)
d_paths = set(r['path'] for r in d_routes)
print(f"\nPath overlap: {len(c_paths.intersection(d_paths))}")
