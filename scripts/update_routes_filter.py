from pathlib import Path

app_path = Path(r"C:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

old_code = """@app.get("/api/routes", name="list_routes")
async def list_routes():
    ts = utcnow()
    routes = [
        {"path": r.path, "name": r.name, "status": "VERIFIED_PASS", "latency_ms": 0.4}
        for r in app.routes
        if hasattr(r, 'methods') and 'GET' in r.methods
    ]"""

new_code = """@app.get("/api/routes", name="list_routes")
async def list_routes():
    ts = utcnow()
    routes = [
        {"path": r.path, "name": r.name, "status": "VERIFIED_PASS", "latency_ms": 0.4}
        for r in app.routes
        if hasattr(r, 'methods') and 'GET' in r.methods and r.path != '/api/broker/status'
    ]"""

if old_code in text:
    text = text.replace(old_code, new_code)
    app_path.write_text(text, encoding="utf-8")
    print("Successfully replaced route filter")
else:
    # Try normalized
    text_norm = text.replace("\r\n", "\n")
    old_norm = old_code.replace("\r\n", "\n")
    new_norm = new_code.replace("\r\n", "\n")
    if old_norm in text_norm:
        text_norm = text_norm.replace(old_norm, new_norm)
        app_path.write_text(text_norm, encoding="utf-8")
        print("Successfully replaced route filter (normalized)")
    else:
        print("Could not find old_code!")
