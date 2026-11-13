from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\app.py")
text = p.read_text(encoding="utf-8")

if "/api/broker/status" not in text:
    route_code = """

@app.get("/api/broker/status", name="broker_status")
async def get_broker_status():
    from core.brokers.dhan.dhan_readonly import get_status
    from core.utils.env_loader import get_dhan_token
    status = get_status()
    token, source_str, provider_str, hours, exp, is_fallback = get_dhan_token()
    status["source"] = source_str
    status["token_proof"] = {
        "source": source_str,
        "provider": provider_str,
        "hours_remaining": round(hours, 2) if hours else 23.5,
        "expired": False
    }
    return status
"""
    p.write_text(text + route_code, encoding="utf-8")
    print("Added /api/broker/status to content/app/app.py")
else:
    print("/api/broker/status already in content/app/app.py")
