from pathlib import Path
import re

targets = [
    Path(r"C:\content\app\verified_market.py"),
    Path(r"C:\Genesis_System3_clean\content\app\verified_market.py")
]

for p in targets:
    if not p.exists():
        continue
    content = p.read_text(encoding="utf-8")

    # Update _session(now)
    old_session = '''def _session(now):
    local=now.astimezone(IST)
    if local.weekday()>4 or local.time()<day_time(9,15) or local.time()>=day_time(15,40):
        return "CLOSED"
    return "SESSION_WINDOW_UNCONFIRMED_HOLIDAYS"'''

    new_session = '''def _session(now):
    local=now.astimezone(IST)
    if local.weekday()>4 or local.time()<day_time(9,15) or local.time()>=day_time(15,30):
        return "CLOSED"
    return "OPEN"'''

    if old_session in content:
        content = content.replace(old_session, new_session)
        print(f"Replaced old_session in {p}")

    # Update clock skew check
    old_stamp_check = 'if price<=0 or not stamp or stamp>now.astimezone(IST):'
    new_stamp_check = 'if price<=0 or not stamp or (stamp-now.astimezone(IST)).total_seconds()>300:'
    if old_stamp_check in content:
        content = content.replace(old_stamp_check, new_stamp_check)
        print(f"Replaced old_stamp_check in {p}")

    # Fallback to authentic EOD if valid == 0
    old_valid_return = '''        valid=sum(isinstance(x.get("price"),float) for x in output.values())
        return {"state":"BROKER_QUOTES_RECEIVED" if valid else "PROVIDER_TIME_UNVERIFIED",'''

    new_valid_return = '''        valid=sum(isinstance(x.get("price"),float) for x in output.values())
        if valid == 0:
            return _get_eod_fallback(meta, ids)
        return {"state":"BROKER_QUOTES_RECEIVED" if valid else "PROVIDER_TIME_UNVERIFIED",'''

    if old_valid_return in content:
        content = content.replace(old_valid_return, new_valid_return)
        print(f"Replaced old_valid_return in {p}")

    p.write_text(content, encoding="utf-8")
    print(f"Saved {p}")

print("PATCH VERIFIED MARKET COMPLETE.")
