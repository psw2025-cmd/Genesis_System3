import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from audit.database import Base, engine
from audit.router import router as audit_router
from audit.middleware import AuditMiddleware, global_exception_handler

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Genesis Institutional Audit API",
    version="1.0.0",
    description="Dedicated Immutable Audit Trail & Verification Service for Genesis System3"
)

# Exception handling
app.add_exception_handler(Exception, global_exception_handler)

# Automatic POST Auditing and Correlation ID propagation middleware
app.add_middleware(AuditMiddleware)

# Include Audit Router
app.include_router(audit_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "audit-api",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("audit.main:app", host="127.0.0.1", port=8001, reload=False)
