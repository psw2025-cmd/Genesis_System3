import urllib.request
import json

url = 'https://genesis-system3-web-802404398783.asia-south1.run.app/api/ml/performance'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        print('status:', data.get('status'))
        print('rho:', data.get('rho'))
        print('hit_rate:', data.get('hit_rate'))
        print('ready_for_live:', data.get('ready_for_live'))
        print('ready_for_live_reason:', data.get('ready_for_live_reason'))
        print('proof_pass_count:', data.get('proof_pass_count'))
        print('validations_checklist:')
        for item in data.get('validations_checklist', []):
            label = item.get('label')
            res = item.get('result')
            det = item.get('detail')
            print(f'  - {label} -> {res} ({det})')
except Exception as e:
    print('Error:', e)
