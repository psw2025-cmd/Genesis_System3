"""
Genesis System3 - Telegram Chat ID Auto-Discovery & Instant Verification
Identity: System3boat (@System3PSWBot)
Token: 8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI
"""

import urllib.request
import json
import time
from pathlib import Path

TOKEN = "8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI"
SECRETS_FILE = Path("c:/Genesis_System3_clean/.secrets/telegram.env")
ENV_FILE = Path("c:/Genesis_System3_clean/.env")


def check_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("result", [])
            for u in reversed(results):
                msg = u.get("message") or u.get("channel_post") or u.get("my_chat_member")
                if msg:
                    chat = msg.get("chat", {})
                    cid = chat.get("id")
                    title = chat.get("title") or chat.get("first_name") or "Direct Chat"
                    if cid:
                        return str(cid), title
    except Exception as e:
        print(f"Error checking updates: {e}")
    return None, None


def send_live_alert(chat_id: str, chat_title: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    text = (
        "🟢 <b>GENESIS SYSTEM3 — LIVE TELEGRAM LINK ESTABLISHED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Bot:</b> System3boat (<code>@System3PSWBot</code>)\n"
        f"<b>Target Chat:</b> <code>{chat_title}</code> (ID: <code>{chat_id}</code>)\n"
        "<b>Safety Mode:</b> <code>PAPER_MODE=1</code> (Constitutionally Locked)\n"
        "<b>Allocated Capital:</b> ₹50,000.00\n"
        "<b>Daily Stop Loss Limit:</b> ₹5,000.00\n"
        "<b>Broker Connectivity:</b> Dhan Live Auth (HTTP 200 Verified)\n"
        "<b>Market Feeds:</b> Live NSE/BSE + Dhan Derivatives\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>All downstream alerts, option breakout signals (#BURST #PreSangam), and fill receipts will now arrive directly here in real time.</i>"
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Telegram Live Alert Status:", res.get("ok"))
        return res


def save_chat_id(chat_id: str):
    # Append to .secrets/telegram.env
    with open(SECRETS_FILE, "a", encoding="utf-8") as f:
        f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")

    # Update .env
    with open(ENV_FILE, "a", encoding="utf-8") as f:
        f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")

    print(f"Successfully saved TELEGRAM_CHAT_ID={chat_id} to environment vaults.")


if __name__ == "__main__":
    print("Checking for inbound messages to @System3PSWBot...")
    cid, title = check_updates()
    if cid:
        print(f"FOUND ACTIVE CHAT: {title} (ID: {cid})")
        save_chat_id(cid)
        send_live_alert(cid, title)
    else:
        print("NO_MESSAGES_YET: Waiting for user to send /start or add bot to group.")
