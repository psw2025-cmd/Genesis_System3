from pathlib import Path

root = Path(r'C:\Genesis_System3_clean').resolve()
subject_files = [
    'content/app/verified_market.py',
    'content/app/templates/premium.html',
    'content/app/app.py',
    'tests/test_ui_p0_recovery_mission.py',
    'state/market_top_ce_pe.json'
]

def within(p, r):
    try:
        p.resolve().relative_to(r.resolve())
        return True
    except ValueError:
        return False

for sf in subject_files:
    p = (root / sf).resolve()
    print(f'{sf}: exists={p.exists()}, is_file={p.is_file()}, within={within(p, root)}')
