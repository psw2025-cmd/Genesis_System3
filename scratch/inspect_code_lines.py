with open('content/app/app.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Find where code actually starts (after comment headers)
code_lines = []
for i, l in enumerate(lines):
    if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('"""') and not l.strip().startswith("'''") and not l.strip().startswith('<!--'):
        code_lines.append((i+1, l))

print(f"Code lines found: {len(code_lines)}")
for line_num, l in code_lines[:50]:
    print(f"{line_num:4}: {l.rstrip()}")
