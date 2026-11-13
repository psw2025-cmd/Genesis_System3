"""
Genesis System3 - Continuous Telegram Bot Daemon
Identity: System3boat (@System3PSWBot)
Token: 8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI
Continuous Inbound Command Processor (/status, /risk, /pnl, /chains, etc.)
"""

import urllib.request
import urllib.parse
import json
import time
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.engine.telegram_notifier import default_telegram_notifier

TOKEN = "8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_reply(chat_id: int, text: str, reply_to_message_id: int = None):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to send reply to {chat_id}: {e}")
        return None


def run_daemon():
    print("Starting Genesis System3 Telegram Bot Daemon for @System3PSWBot...")
    sys.stdout.flush()

    last_offset = 0

    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={last_offset}&timeout=15"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = data.get("result", [])
            for update in results:
                update_id = update.get("update_id", 0)
                if update_id >= last_offset:
                    last_offset = update_id + 1

                msg = update.get("message")
                if not msg:
                    continue

                chat_id = msg.get("chat", {}).get("id")
                msg_id = msg.get("message_id")
                text = msg.get("text", "").strip()
                sender = msg.get("from", {}).get("first_name", "User")

                if not text or not chat_id:
                    continue

                print(f"Received from {sender} (Chat {chat_id}): '{text}'")

                # Handle commands or friendly greetings
                if text.startswith("/"):
                    reply_text = default_telegram_notifier.handle_command(text)
                elif text.lower() in ["hi", "hello", "hey", "start"]:
                    reply_text = (
                        f"👋 Hello {sender}!\n\n"
                        f"I am <b>System3boat</b> (<code>@System3PSWBot</code>), your institutional AI trading assistant.\n\n"
                        f"<b>Available Commands:</b>\n"
                        f"• /status — Live system health & Dhan broker connectivity\n"
                        f"• /risk — Your capital envelope (₹50k) & daily stop-loss (₹5k)\n"
                        f"• /pnl — Current intraday P&L & open simulated trades\n"
                        f"• /chains — Real-time NIFTY/BANKNIFTY ATM strikes & PCR"
                    )
                else:
                    reply_text = (
                        f"Received: <i>{text}</i>\n\n"
                        f"Use /status, /risk, /pnl, or /chains to view live market telemetry."
                    )

                res = send_reply(chat_id, reply_text, reply_to_message_id=msg_id)
                if res and res.get("ok"):
                    print(f"Replied successfully to message {msg_id}!")
                sys.stdout.flush()

        except Exception as e:
            print(f"Daemon polling error: {e}")
            sys.stdout.flush()
            time.sleep(3)


if __name__ == "__main__":
    run_daemon()
