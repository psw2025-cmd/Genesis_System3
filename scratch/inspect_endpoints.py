import sys

with open('c:/Genesis_System3_clean/dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoints = [
    '/api/backtest/results',
    '/api/alerts',
    '/api/qc/runtime',
    '/api/system/readiness',
    '/api/proof_ledger',
    '/api/option-chain',
    '/api/accuracy_trend',
    '/api/auto_gates',
    '/api/audit/option-visibility',
    '/api/ml/validations',
    '/api/ml/performance',
    '/api/status',
    '/api/pnl',
]

for ep in endpoints:
    pos = text.find(f'"{ep}"')
    if pos != -1:
        line_num = text[:pos].count('\n') + 1
        print(f"=== ENDPOINT: {ep} (line {line_num}) ===")
        # print next 25 lines
        snippet = '\n'.join(text[pos:].splitlines()[:25])
        print(snippet)
        print("\n" + "="*40 + "\n")
    else:
        print(f"=== NOT FOUND: {ep} ===")
