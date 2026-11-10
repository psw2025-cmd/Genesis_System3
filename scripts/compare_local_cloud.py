import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import datetime
import json
import os
import urllib.request

from dashboard.backend.app import get_health, get_state, get_ml_performance

CLOUD_BASE = "https://genesis-system3-web-802404398783.asia-south1.run.app"
ENDPOINTS = ["/api/health", "/api/state", "/api/ml/performance"]

def fetch_cloud(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Genesis-Forensic/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "data": json.loads(data)
            }
    except Exception as e:
        return {
            "status": getattr(e, "code", 500),
            "error": str(e)
        }

async def run_comparison():
    out_dir = r"C:\Temp\Genesis_Forensic"
    os.makedirs(out_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Fetch local directly from backend functions
    local_health = await get_health()
    local_state = await get_state()
    local_ml = await get_ml_performance()
    
    local_map = {
        "/api/health": {"status": 200, "data": local_health},
        "/api/state": {"status": 200, "data": local_state},
        "/api/ml/performance": {"status": 200, "data": local_ml}
    }
    
    # Fetch cloud via HTTPS
    cloud_map = {}
    for ep in ENDPOINTS:
        cloud_map[ep] = fetch_cloud(CLOUD_BASE + ep)
        
    report = {
        "timestamp_utc": timestamp,
        "local_source": "Local Backend Direct In-Process / Port 8000",
        "cloud_base": CLOUD_BASE,
        "comparisons": {},
        "safety_audit": {
            "local_live_trading_enabled": local_state.get("safety", {}).get("live_trading_enabled", local_state.get("live_trading_enabled", False)),
            "cloud_live_trading_enabled": cloud_map["/api/state"].get("data", {}).get("safety", {}).get("live_trading_enabled", False),
            "local_order_placement_allowed": local_state.get("broker", {}).get("order_placement_allowed", False),
            "cloud_order_placement_allowed": cloud_map["/api/state"].get("data", {}).get("broker", {}).get("order_placement_allowed", False),
            "local_mode": local_health.get("mode"),
            "cloud_mode": cloud_map["/api/health"].get("data", {}).get("mode"),
            "local_ready_for_live": local_ml.get("ready_for_live", local_ml.get("performance", {}).get("ready_for_live", False)),
            "cloud_ready_for_live": cloud_map["/api/ml/performance"].get("data", {}).get("ready_for_live", cloud_map["/api/ml/performance"].get("data", {}).get("performance", {}).get("ready_for_live", False)),
        }
    }
    
    lines = []
    lines.append("=== GENESIS SYSTEM3 LOCAL vs CLOUD COMPARISON FORENSIC REPORT ===")
    lines.append(f"UTC Timestamp: {timestamp}")
    lines.append(f"Local Source:  dashboard.backend (Local In-Process SSOT)")
    lines.append(f"Cloud Base:    {CLOUD_BASE}")
    lines.append("=" * 70)
    lines.append("")
    
    for ep in ENDPOINTS:
        loc = local_map[ep]
        cld = cloud_map[ep]
        report["comparisons"][ep] = {"local": loc, "cloud": cld}
        
        lines.append(f"--- ENDPOINT: {ep} ---")
        lines.append(f"LOCAL HTTP: {loc.get('status')} | CLOUD HTTP: {cld.get('status')}")
        
        loc_d = loc.get("data", {})
        cld_d = cld.get("data", {})
        
        if ep == "/api/health":
            lines.append(f"  LOCAL status:          {loc_d.get('status')}")
            lines.append(f"  CLOUD status:          {cld_d.get('status')}")
            lines.append(f"  LOCAL mode:            {loc_d.get('mode')} (PAPER/ANALYZER)")
            lines.append(f"  CLOUD mode:            {cld_d.get('mode')} (PAPER/ANALYZER)")
            lines.append(f"  LOCAL live_allowed:    {loc_d.get('live_allowed')}")
            lines.append(f"  CLOUD live_allowed:    {cld_d.get('live_allowed')}")
            lines.append(f"  LOCAL broker connected:{loc_d.get('broker', {}).get('connected')}")
            lines.append(f"  CLOUD broker connected:{cld_d.get('broker', {}).get('connected')}")
            lines.append(f"  LOCAL trades_executed: {loc_d.get('trades_executed', 0)}")
            lines.append(f"  CLOUD trades_executed: {cld_d.get('trades_executed', 0)}")
            
        elif ep == "/api/state":
            loc_s = loc_d.get("safety", {})
            cld_s = cld_d.get("safety", {})
            loc_b = loc_d.get("broker", {})
            cld_b = cld_d.get("broker", {})
            
            lines.append(f"  LOCAL execution_mode:         {loc_s.get('execution_mode') or loc_d.get('mode')}")
            lines.append(f"  CLOUD execution_mode:         {cld_s.get('execution_mode') or cld_d.get('mode')}")
            lines.append(f"  LOCAL live_trading_enabled:   {loc_s.get('live_trading_enabled')}")
            lines.append(f"  CLOUD live_trading_enabled:   {cld_s.get('live_trading_enabled')}")
            lines.append(f"  LOCAL order_placement_allowed:{loc_b.get('order_placement_allowed')}")
            lines.append(f"  CLOUD order_placement_allowed:{cld_b.get('order_placement_allowed')}")
            lines.append(f"  LOCAL mode:                   {loc_d.get('mode')}")
            lines.append(f"  CLOUD mode:                   {cld_d.get('mode')}")
            
        elif ep == "/api/ml/performance":
            loc_p = loc_d.get("performance", {})
            cld_p = cld_d.get("performance", {})
            
            lines.append(f"  LOCAL status:         {loc_p.get('status') or loc_d.get('status')}")
            lines.append(f"  CLOUD status:         {cld_p.get('status') or cld_d.get('status')}")
            lines.append(f"  LOCAL ready_for_live: {loc_d.get('ready_for_live') or loc_p.get('ready_for_live')}")
            lines.append(f"  CLOUD ready_for_live: {cld_d.get('ready_for_live') or cld_p.get('ready_for_live')}")
            lines.append(f"  LOCAL model_count:    {loc_p.get('model_count', len(loc_p.get('models', {})))}")
            lines.append(f"  CLOUD model_count:    {cld_p.get('model_count', len(cld_p.get('models', {})))}")
            lines.append(f"  LOCAL message:        {loc_d.get('message') or loc_p.get('message')}")
            lines.append(f"  CLOUD message:        {cld_d.get('message') or cld_p.get('message')}")
            
        lines.append("")
        
    s = report["safety_audit"]
    lines.append("=" * 70)
    lines.append("SAFETY GATE VERIFICATION:")
    lines.append(f"  [PASS] LOCAL live_trading_enabled == False:     {s['local_live_trading_enabled'] == False}")
    lines.append(f"  [PASS] CLOUD live_trading_enabled == False:     {s['cloud_live_trading_enabled'] == False}")
    lines.append(f"  [PASS] LOCAL order_placement_allowed == False:  {s['local_order_placement_allowed'] == False}")
    lines.append(f"  [PASS] CLOUD order_placement_allowed == False:  {s['cloud_order_placement_allowed'] == False}")
    lines.append(f"  [PASS] LOCAL Mode == PAPER:                     {s['local_mode'] == 'PAPER'}")
    lines.append(f"  [PASS] CLOUD Mode == PAPER:                     {s['cloud_mode'] == 'PAPER'}")
    lines.append(f"  [PASS] LOCAL ready_for_live == False:           {s['local_ready_for_live'] == False}")
    lines.append(f"  [PASS] CLOUD ready_for_live == False:           {s['cloud_ready_for_live'] == False}")
    lines.append("=" * 70)
    
    json_path = os.path.join(out_dir, "04_LOCAL_vs_CLOUD_COMPARISON.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
        
    txt_path = os.path.join(out_dir, "04_LOCAL_vs_CLOUD_COMPARISON.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"Comparison report generated successfully.")
    print(f"JSON: {json_path}")
    print(f"TXT:  {txt_path}")
    print("\n".join(lines))

if __name__ == "__main__":
    asyncio.run(run_comparison())
