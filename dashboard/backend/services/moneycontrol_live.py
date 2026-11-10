import os, json, time, requests
from datetime import datetime
FILE='/tmp/moneycontrol_option_gainers.json'
TTL=300
def get_live_data():
    try:
        if os.path.exists(FILE) and time.time() - os.path.getmtime(FILE) < TTL:
            return json.load(open(FILE))
    except: pass
    try:
        live=requests.get('https://api.moneycontrol.com/option_gainers', timeout=10).json()
    except:
        live={'gainers':[], 'error':'api_failed_fallback'}
    live['_fetched_at']=datetime.utcnow().isoformat()
    live['_source']='LIVE_API_PATH_B'
    live['_ttl_seconds']=TTL
    try:
        json.dump(live, open(FILE,'w'))
    except: pass
    return live
