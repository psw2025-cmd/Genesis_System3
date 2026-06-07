from pathlib import Path

APP_PATH = Path('dashboard/backend/app.py')

OLD = '''# Root route - helpful message
@app.get("/")
async def root():
    return {
        "message": "System3 Ultra Dashboard API",
        "status": "running",
        "dashboard_url": "http://localhost:3000",
        "api_docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/health",
        "state": "http://localhost:8000/api/state",
    }
'''

NEW = '''# Root route - helpful message
@app.get("/")
async def root():
    base_url = os.environ.get("PUBLIC_BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
    dashboard_url = os.environ.get("PUBLIC_DASHBOARD_URL", base_url).rstrip("/")
    return {
        "message": "System3 Ultra Dashboard API",
        "status": "running",
        "backend_url": base_url,
        "dashboard_url": dashboard_url,
        "api_docs": f"{base_url}/docs",
        "health": f"{base_url}/api/health",
        "state": f"{base_url}/api/state",
        "relative_paths": {
            "api_docs": "/docs",
            "health": "/api/health",
            "state": "/api/state",
            "broker_status": "/api/broker/status",
        },
    }
'''


def main() -> int:
    text = APP_PATH.read_text(encoding='utf-8')
    if NEW in text:
        print('Root endpoint already patched.')
        return 0
    if OLD not in text:
        raise SystemExit('Expected localhost root endpoint block not found; refusing broad edit.')
    APP_PATH.write_text(text.replace(OLD, NEW), encoding='utf-8')
    print('Root endpoint patched to production-safe URLs.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
