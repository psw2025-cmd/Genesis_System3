import sys
from pathlib import Path

app_path = Path(r"c:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

old_snippet = """@app.get("/api/v1/placeorder", name="_get_compat_placeorder", include_in_schema=False)
async def openalgo_place_order_get():
    \"\"\"Browser GET inspector for Single Order Gateway (prevents 405 Method Not Allowed when opened via GET).\"\"\"
    ts = utcnow()
    data = {
        "endpoint": "/api/v1/placeorder",
        "execution_method": "POST",
        "gateway_status": "ONLINE_SAFETY_LOCKED",
        "paper_mode": True,
        "live_trading_enabled": False,
        "live_order_authority": 0,
        "safety_gate": "Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)",
        "schema": {
            "symbol": "NIFTY",
            "exchange": "NSE",
            "action": "BUY | SELL",
            "quantity": 50,
            "pricetype": "MARKET | LIMIT",
            "product": "MIS | CNC"
        },
        "ui_dashboard_url": "http://127.0.0.1:8008/ui"
    }
    return make_envelope(data, ts, real=True)"""

# In app.py, there may be extra newlines between lines.
# Let's locate @app.get("/api/v1/placeorder" and the matching return statement.
start_idx = text.find('@app.get("/api/v1/placeorder"')
if start_idx == -1:
    print("Could not find start_idx!")
    sys.exit(1)

# Find the next endpoint after this function
next_route_idx = text.find('@app.get("/api/telegram/test-alert"', start_idx)
if next_route_idx == -1:
    print("Could not find next_route_idx!")
    sys.exit(1)

target_chunk = text[start_idx:next_route_idx]
print(f"Target chunk length: {len(target_chunk)}")

new_chunk = '''@app.get("/api/v1/placeorder", name="_get_compat_placeorder", include_in_schema=False)
async def openalgo_place_order_get(request: Request):
    """Browser GET inspector for Single Order Gateway (prevents 405 Method Not Allowed when opened via GET)."""
    ts = utcnow()
    data = {
        "endpoint": "/api/v1/placeorder",
        "execution_method": "POST",
        "gateway_status": "ONLINE_SAFETY_LOCKED",
        "paper_mode": True,
        "live_trading_enabled": False,
        "live_order_authority": 0,
        "safety_gate": "Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)",
        "schema": {
            "symbol": "NIFTY",
            "exchange": "NSE",
            "action": "BUY | SELL",
            "quantity": 50,
            "pricetype": "MARKET | LIMIT",
            "product": "MIS | CNC"
        },
        "ui_dashboard_url": "http://127.0.0.1:8008/ui"
    }

    user_agent = request.headers.get("user-agent", "")
    accept = request.headers.get("accept", "")
    is_browser = "Mozilla" in user_agent or "Chrome" in user_agent or "text/html" in accept

    if is_browser and "Python-urllib" not in user_agent:
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Genesis System3 — Institutional Order Gateway</title>
  <style>
    body { background: #0c0f14; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; margin: 0; padding: 24px; }
    .container { max-width: 650px; margin: 0 auto; background: #141820; border: 1px solid #2d3748; border-radius: 8px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-lock { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid #ef4444; }
    .btn-dashboard { display: block; text-align: center; background: #00ff88; color: #000; font-weight: bold; padding: 12px; border-radius: 6px; text-decoration: none; margin: 18px 0; font-size: 14px; letter-spacing: 0.5px; }
    .btn-dashboard:hover { background: #00dd77; }
    .ticket { background: #1a202c; border: 1px solid #374151; border-radius: 6px; padding: 16px; margin-top: 16px; }
    .row { display: flex; gap: 12px; margin-bottom: 12px; }
    .col { flex: 1; }
    label { display: block; font-size: 11px; color: #94a3b8; margin-bottom: 4px; font-weight: 600; }
    input, select { width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 8px; border-radius: 4px; font-size: 13px; box-sizing: border-box; }
    .btn-submit { width: 100%; background: #3b82f6; color: #fff; font-weight: bold; border: none; padding: 10px; border-radius: 4px; font-size: 13px; cursor: pointer; }
    .btn-submit:hover { background: #2563eb; }
    #result-box { margin-top: 12px; padding: 10px; border-radius: 4px; font-size: 12px; display: none; word-break: break-all; }
  </style>
</head>
<body>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h2 style="margin: 0; font-size: 18px; color: #fff;">⚡ Institutional Order Gateway</h2>
      <span class="badge badge-lock">ONLINE_SAFETY_LOCKED</span>
    </div>

    <p style="font-size: 13px; color: #94a3b8; line-height: 1.5;">
      You navigated directly to the Backend Order API (<code>/api/v1/placeorder</code>).
      In automated execution, this endpoint accepts JSON <code>POST</code> orders.
      For interactive trading charts, live Option Chain, and market heatmaps, use the Trading Terminal:
    </p>

    <a href="/ui" class="btn-dashboard">⚡ Open Live Trading Dashboard (/ui) ⚡</a>

    <div class="ticket">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 12px; color: #38bdf8;">Paper Order Placement Simulator</div>
      <form id="orderForm" onsubmit="submitOrder(event)">
        <div class="row">
          <div class="col">
            <label>TRADING SYMBOL / CONTRACT</label>
            <input type="text" id="symbol" value="NIFTY 05NOV2026 23450 CE" required>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <label>ACTION / SIDE</label>
            <select id="action">
              <option value="BUY" selected>BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div class="col">
            <label>QUANTITY (LOTS/UNITS)</label>
            <input type="number" id="qty" value="75" min="1" required>
          </div>
          <div class="col">
            <label>PRICE TYPE</label>
            <select id="pricetype">
              <option value="MARKET" selected>MARKET</option>
              <option value="LIMIT">LIMIT</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn-submit">🚀 Submit Paper Order</button>
      </form>
      <div id="result-box"></div>
    </div>

    <div style="margin-top: 16px; font-size: 11px; color: #64748b; line-height: 1.4;">
      <strong>Safety Locks Active:</strong> PAPER_MODE=1 · LIVE_TRADING_ENABLED=0 · REAL_BROKER_ORDERS=0 (Zero broker risk).
    </div>
  </div>

  <script>
    async function submitOrder(e) {
      e.preventDefault();
      const resBox = document.getElementById('result-box');
      resBox.style.display = 'block';
      resBox.style.background = '#1e293b';
      resBox.style.color = '#38bdf8';
      resBox.innerText = 'Transmitting order to gateway...';
      try {
        const payload = {
          symbol: document.getElementById('symbol').value,
          action: document.getElementById('action').value,
          quantity: parseInt(document.getElementById('qty').value, 10),
          pricetype: document.getElementById('pricetype').value,
          paper_only: true
        };
        const resp = await fetch('/api/v1/placeorder', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json().catch(() => ({}));
        if (resp.status === 403 || !resp.ok) {
          resBox.style.background = 'rgba(239,68,68,0.2)';
          resBox.style.color = '#ef4444';
          resBox.innerText = 'Gate Enforcement: ' + (data.detail || 'Live trading locked by safety gate');
        } else {
          resBox.style.background = 'rgba(34,197,94,0.2)';
          resBox.style.color = '#22c55e';
          resBox.innerText = 'Paper Order Placed: ' + JSON.stringify(data);
        }
      } catch(err) {
        resBox.style.background = 'rgba(239,68,68,0.2)';
        resBox.style.color = '#ef4444';
        resBox.innerText = 'Error: ' + err.message;
      }
    }
  </script>
</body>
</html>"""
        return HTMLResponse(content=html_content, status_code=200)

    return make_envelope(data, ts, real=True)

'''

text = text[:start_idx] + new_chunk + text[next_route_idx:]
app_path.write_text(text, encoding="utf-8")
print("Successfully patched openalgo_place_order_get in app.py!")
