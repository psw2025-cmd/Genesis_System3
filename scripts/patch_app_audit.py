import re

path = "content/app/app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add AuditMiddleware after app definition if not already present
if "from audit.middleware import AuditMiddleware" not in content:
    target = 'app = FastAPI(\n    title="Genesis System3 - Institutional Market-Intelligence Command Center",\n    description="High-Throughput Derivatives, Equities & Institutional Verification Suite",\n    version="3.5.0",\n    lifespan=lifespan\n)'
    replacement = target + '\n\nfrom audit.middleware import AuditMiddleware\napp.add_middleware(AuditMiddleware)\n'
    if target in content:
        content = content.replace(target, replacement, 1)
        print("AuditMiddleware added to app initialization.")
    else:
        print("Target for AuditMiddleware not found!")

# 2. Add Audit Router and placeorder route at the end of content/app/app.py
if "from audit.router import router as _audit_router" not in content:
    additions = '''

# S3_AUDIT_ROUTER — Institutional Audit Trail, POST Audits, and Verification
from audit.router import router as _audit_router
app.include_router(_audit_router)

from fastapi import HTTPException

@app.post("/api/v1/placeorder")
async def openalgo_place_order(request: Request):
    """Enforces Institutional Backend Safety Gate: LIVE_TRADING_ENABLED=0 lock."""
    raise HTTPException(
        status_code=403,
        detail="Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)"
    )
'''
    content += additions
    print("Audit router and /api/v1/placeorder added to content/app/app.py.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patching complete.")
