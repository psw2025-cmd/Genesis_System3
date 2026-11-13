import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://genesis-system3-web-802404398783.asia-south1.run.app/api/auto_gates'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
        data = json.loads(r.read().decode())
        print('HTTP status:', r.status)
        print('Keys:', list(data.keys()))
        if 'gates' in data:
            print('Gates count:', len(data['gates']))
            for k, v in data['gates'].items():
                print(f'{k}: pass={v.get("pass")} status={v.get("status")}')
except Exception as e:
    print('ERROR:', e)
