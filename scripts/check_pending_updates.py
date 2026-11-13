import urllib.request
import json

token = '8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI'
url = f'https://api.telegram.org/bot{token}/getUpdates'

req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    results = data.get('result', [])
    print(f'Pending updates count: {len(results)}')
    for u in results:
        msg = u.get('message', {})
        text = msg.get('text')
        user = msg.get('from', {}).get('first_name')
        uid = u.get('update_id')
        print(f'Update ID {uid}: From {user} -> {text}')
