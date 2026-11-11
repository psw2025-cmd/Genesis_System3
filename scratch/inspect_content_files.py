import os

files = [
    'content/app/configure_safe_env.py',
    'content/app/dhan_account_router.py',
    'content/app/fetch_dhan_master.py',
    'content/app/inspect_market_master.py',
    'content/app/inspect_master_names.py',
    'content/app/install_verified_gate.py',
    'content/app/patch_truth.py',
    'content/app/probe_dhan_credentials.py',
    'content/app/test_api_endpoints.py',
    'content/app/verified_market.py',
    'content/app/verified_sources/audit_master_ids.py'
]

for fpath in files:
    if os.path.exists(fpath):
        print(f"\n==================== {fpath} ====================")
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        # Print first 25 non-empty lines
        count = 0
        for l in lines:
            if l.strip() and not l.strip().startswith('#'):
                print(l.rstrip()[:120])
                count += 1
                if count >= 20:
                    break
