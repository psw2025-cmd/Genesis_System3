import json

with open('reports/latest/tab_audit_snaps/audit_summary.json', 'r') as f:
    data = json.load(f)

print(f"{'TAB ID':<18} | {'LABEL':<20} | {'TIME':<6} | {'CONSOLE':<7} | {'HTTP ERR':<8} | {'BLOCKERS':<8}")
print("-" * 75)
for row in data:
    t_id = row['tab_id']
    t_lbl = row['tab_label']
    el = f"{row['elapsed_sec']}s"
    c_err = len(row['console_errors'])
    h_err = len(row['http_errors'])
    b_cnt = len(row['blockers'])
    print(f"{t_id:<18} | {t_lbl:<20} | {el:<6} | {c_err:<7} | {h_err:<8} | {b_cnt:<8}")
    if row['blockers']:
        for b in row['blockers']:
            print(f"   [BLOCKER] {b}")
    if row['http_errors']:
        for h in row['http_errors']:
            print(f"   [HTTP ERR] {h}")
