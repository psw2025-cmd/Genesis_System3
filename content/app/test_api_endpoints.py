import urllib.request
import json

endpoints = [
    '/api/verified-market',
    '/api/options/gainers',
    '/api/paper/ledger',
    '/api/ml/prediction-audit',
    '/api/health'
]

for ep in endpoints:
    try:
        url = f"http://127.0.0.1:8008{ep}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"=== {ep} [HTTP {resp.status}] ===")
        if ep == '/api/verified-market':
            print("State:", data.get("state"), "| Verified:", data.get("exchange_quotes_verified"))
            quotes = data.get("quotes", {})
            for sym, q in quotes.items():
                print(f"  {sym}: Price={q.get('price')} Status={q.get('status')} IST={q.get('last_trade_ist')} Age={q.get('age_seconds')}s")
        elif ep == '/api/options/gainers':
            envelope_data = data.get("data", {})
            print("CE Count:", envelope_data.get("total_ce"), "PE Count:", envelope_data.get("total_pe"))
            print("Snapshot Type:", envelope_data.get("snapshot_type"), "Source:", envelope_data.get("source"))
            ce_list = envelope_data.get("ce_gainers", [])
            pe_list = envelope_data.get("pe_gainers", [])
            if ce_list:
                print("  Top CE 1:", ce_list[0].get("contract"), "LTP:", ce_list[0].get("ltp"), "Gain%:", ce_list[0].get("change_pct"), "Prov:", ce_list[0].get("data_provenance"))
            if pe_list:
                print("  Top PE 1:", pe_list[0].get("contract"), "LTP:", pe_list[0].get("ltp"), "Gain%:", pe_list[0].get("change_pct"), "Prov:", pe_list[0].get("data_provenance"))
        elif ep == '/api/paper/ledger':
            envelope_data = data.get("data", {})
            print("Summary:", envelope_data.get("closed_summary"))
        elif ep == '/api/ml/prediction-audit':
            envelope_data = data.get("data", {})
            print("ML Metrics:", envelope_data)
        elif ep == '/api/health':
            envelope_data = data.get("data", {})
            print("Health Status:", envelope_data.get("status"), "Uptime:", envelope_data.get("uptime_sec"))
    except Exception as e:
        print(f"ERROR on {ep}: {e}")
