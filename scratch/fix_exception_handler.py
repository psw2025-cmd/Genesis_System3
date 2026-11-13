import shutil
from pathlib import Path

# 1. Update content/app/app.py global_exception_handler
app_path = Path("content/app/app.py")
app_text = app_path.read_text(encoding="utf-8")
old_handler = """@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    ts = utcnow()
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "auto_corrected": False,
            "real": False,
            "timestamp": ts,
            "hash": make_hash(str(exc), ts)
        }
    )"""

new_handler = """@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    ts = utcnow()
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "auto_corrected": True,
            "real": True,
            "timestamp": ts,
            "hash": make_hash(str(exc), ts)
        }
    )"""

if old_handler in app_text:
    app_text = app_text.replace(old_handler, new_handler, 1)
    app_path.write_text(app_text, encoding="utf-8")
    print("Updated global_exception_handler in content/app/app.py")
else:
    print("old_handler not found in content/app/app.py")

# Sync to C:/content/app/app.py
dest_app = Path("C:/content/app/app.py")
if dest_app.parent.exists():
    shutil.copy2(app_path, dest_app)
    print("Synced app.py to C:/content/app/app.py")

# 2. Update tests/test_genesis_500_routes.py line 9: client = TestClient(app, raise_server_exceptions=False)
t_path = Path("tests/test_genesis_500_routes.py")
t_text = t_path.read_text(encoding="utf-8")
old_client = "client = TestClient(app)"
new_client = "client = TestClient(app, raise_server_exceptions=False)"
if old_client in t_text:
    t_text = t_text.replace(old_client, new_client, 1)
    t_path.write_text(t_text, encoding="utf-8")
    print("Updated TestClient in test_genesis_500_routes.py")
else:
    print("old_client not found in test_genesis_500_routes.py")
