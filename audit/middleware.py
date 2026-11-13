import logging
import time
import uuid
import json
import hashlib
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from audit.database import SessionLocal
from audit import models

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        start_time = time.perf_counter()

        # Capture request body for POST if possible without consuming stream permanently
        req_payload = {}
        req_hash = ""
        if request.method == "POST":
            try:
                body_bytes = await request.body()
                if body_bytes:
                    req_hash = hashlib.sha256(body_bytes).hexdigest()
                    try:
                        req_payload = json.loads(body_bytes.decode("utf-8"))
                    except Exception:
                        req_payload = {"raw_size": len(body_bytes)}
            except Exception:
                pass

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000)

            response.headers["X-Correlation-ID"] = correlation_id

            logger.info(
                "%s %s %sms",
                request.method,
                request.url.path,
                duration_ms,
            )

            # Automatically audit POST requests into immutable audit database
            if request.method == "POST" and not request.url.path.startswith("/api/audit/post"):
                self._record_post_audit(
                    endpoint=request.url.path,
                    method=request.method,
                    response_code=response.status_code,
                    latency_ms=duration_ms,
                    correlation_id=correlation_id,
                    request_payload=req_payload,
                    request_hash=req_hash,
                    success=(response.status_code < 400),
                )

            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000)
            logger.exception("Request failed %s", request.url.path)

            if request.method == "POST":
                self._record_post_audit(
                    endpoint=request.url.path,
                    method=request.method,
                    response_code=500,
                    latency_ms=duration_ms,
                    correlation_id=correlation_id,
                    request_payload=req_payload,
                    request_hash=req_hash,
                    success=False,
                )
            raise exc

    def _record_post_audit(
        self,
        endpoint: str,
        method: str,
        response_code: int,
        latency_ms: int,
        correlation_id: str,
        request_payload: dict,
        request_hash: str,
        success: bool,
    ):
        db = SessionLocal()
        try:
            row = models.PostAudit(
                endpoint=endpoint,
                method=method,
                initiated_by="middleware",
                initiated_type="http_post",
                request_hash=request_hash,
                request_payload=request_payload,
                response_payload={},
                response_code=response_code,
                latency_ms=latency_ms,
                success=success,
                correlation_id=correlation_id,
            )
            db.add(row)
            db.commit()
        except Exception as db_err:
            db.rollback()
            logger.warning("Audit middleware failed to persist post audit: %s", db_err)
        finally:
            db.close()


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
        },
    )
