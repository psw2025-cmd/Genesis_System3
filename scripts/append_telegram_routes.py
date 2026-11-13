import os

app_path = 'C:/content/app/app.py'

telegram_routes_code = '''

# ---------------------------------------------------------------------------
# Telegram Downstream Operations: Identity @System3PSWBot (System3boat)
# ---------------------------------------------------------------------------
try:
    from core.engine.telegram_notifier import default_telegram_notifier
except ImportError:
    import sys
    sys.path.insert(0, "c:/Genesis_System3_clean")
    from core.engine.telegram_notifier import default_telegram_notifier

@app.get("/api/telegram/status", name="telegram_bot_status")
async def get_telegram_status():
    ts = utcnow()
    status_data = default_telegram_notifier.get_status()
    return make_envelope(status_data, ts)

@app.get("/api/telegram/outbox", name="telegram_outbox_log")
async def get_telegram_outbox(limit: int = 10):
    ts = utcnow()
    outbox = default_telegram_notifier.get_recent_outbox(limit=limit)
    return make_envelope({"outbox": outbox, "count": len(outbox)}, ts)

@app.post("/api/telegram/test-alert", name="telegram_test_alert")
async def send_telegram_test_alert():
    ts = utcnow()
    test_msg = (
        "🚀 <b>GENESIS SYSTEM3 INSTANT VERIFICATION</b>\\n"
        "━━━━━━━━━━━━━━━━━━━━━━\\n"
        "<b>Bot:</b> System3boat (<code>@System3PSWBot</code>)\\n"
        "<b>Status:</b> DOWNSTREAM DISPATCH ACTIVE\\n"
        "<b>Paper Mode:</b> LOCKED (PAPER_MODE=1)\\n"
        "<b>Allocated Capital:</b> ₹50,000.00\\n"
        "<b>Daily Stop Loss:</b> ₹5,000.00\\n"
        "<b>Market Feeds:</b> Certified NSE/BSE + Dhan Auth\\n"
        "<b>Timestamp:</b> <code>" + ts + "</code>\\n"
        "━━━━━━━━━━━━━━━━━━━━━━\\n"
        "<i>All systems fully operational. Zero broker risk.</i>"
    )
    result = default_telegram_notifier.dispatch(text=test_msg, category="SYSTEM_VERIFICATION")
    return make_envelope(result, ts)

@app.post("/api/telegram/dispatch", name="telegram_dispatch_custom")
async def dispatch_telegram_custom(text: str = "Genesis System3 Ping", category: str = "MANUAL"):
    ts = utcnow()
    result = default_telegram_notifier.dispatch(text=text, category=category)
    return make_envelope(result, ts)

@app.post("/api/telegram/command", name="telegram_inbound_command")
async def handle_telegram_command(command: str = "/status"):
    ts = utcnow()
    reply = default_telegram_notifier.handle_command(command)
    return make_envelope({"command": command, "reply": reply}, ts)
'''

with open(app_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

if "/api/telegram/status" not in current_content:
    with open(app_path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(telegram_routes_code)
    print("SUCCESS: Added Telegram downstream routes to C:/content/app/app.py")
else:
    print("ALREADY PRESENT: Telegram routes exist in C:/content/app/app.py")
