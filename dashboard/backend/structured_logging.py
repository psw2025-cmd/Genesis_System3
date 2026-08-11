"""Structured JSON logging and request/trace correlation for System3.

The middleware is intentionally metadata-only: it never logs request/response
bodies, Authorization/Cookie headers, API keys, broker tokens, PINs or TOTP
values. It propagates safe correlation IDs so synthetic browser evidence can be
joined to Cloud Run logs without exposing credentials.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Optional

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_trace_id_ctx: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
_span_id_ctx: ContextVar[Optional[str]] = ContextVar("span_id", default=None)

_TRACEPARENT_RE = re.compile(
    r"^[0-9a-f]{2}-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$",
    re.IGNORECASE,
)
_TRACE_ID_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def get_trace_id() -> Optional[str]:
    return _trace_id_ctx.get()


def get_span_id() -> Optional[str]:
    return _span_id_ctx.get()


def set_request_id(value: Optional[str]) -> None:
    _request_id_ctx.set(value)


def set_trace_id(value: Optional[str]) -> None:
    _trace_id_ctx.set(value)


def set_span_id(value: Optional[str]) -> None:
    _span_id_ctx.set(value)


def _decode_header(headers: dict[bytes, bytes], key: bytes) -> str:
    raw = headers.get(key, b"")
    try:
        return raw.decode("latin-1").strip()
    except Exception:
        return ""


def _safe_request_id(value: str) -> str:
    return value if value and _REQUEST_ID_RE.fullmatch(value) else str(uuid.uuid4())


def _trace_from_headers(headers: dict[bytes, bytes]) -> tuple[str, str, str]:
    """Return trace_id, parent_span_id and response traceparent.

    Priority is a valid W3C traceparent, then a valid x-trace-id, otherwise a
    fresh 128-bit trace ID. A new server span is always generated.
    """
    incoming_parent = _decode_header(headers, b"traceparent").lower()
    match = _TRACEPARENT_RE.fullmatch(incoming_parent)
    if match and match.group(1) != "0" * 32 and match.group(2) != "0" * 16:
        trace_id = match.group(1).lower()
        parent_span_id = match.group(2).lower()
        flags = match.group(3).lower()
    else:
        incoming_trace = _decode_header(headers, b"x-trace-id").replace("-", "").lower()
        trace_id = incoming_trace if _TRACE_ID_RE.fullmatch(incoming_trace) and incoming_trace != "0" * 32 else uuid.uuid4().hex
        parent_span_id = ""
        flags = "01"
    span_id = uuid.uuid4().hex[:16]
    response_traceparent = f"00-{trace_id}-{span_id}-{flags}"
    return trace_id, parent_span_id, response_traceparent


def _runtime_metadata() -> dict[str, str]:
    return {
        "service": os.environ.get("K_SERVICE") or os.environ.get("GCP_CLOUD_RUN_SERVICE") or "genesis-system3-web",
        "env": os.environ.get("SYSTEM3_ENV") or "prod",
        "region": os.environ.get("K_REGION") or os.environ.get("GCP_REGION") or "asia-south1",
        "revision": os.environ.get("K_REVISION") or "unknown",
        "deployment_tag": os.environ.get("DEPLOY_GIT_SHA") or "unknown",
    }


class JsonFormatter(logging.Formatter):
    """Emit one secret-safe JSON object per line for Cloud Logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            **_runtime_metadata(),
        }
        request_id = get_request_id()
        trace_id = get_trace_id()
        span_id = get_span_id()
        if request_id:
            payload["request_id"] = request_id
        if trace_id:
            payload["trace_id"] = trace_id
        if span_id:
            payload["span_id"] = span_id

        standard_keys = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key not in standard_keys and key not in payload:
                try:
                    json.dumps(value)
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = str(value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)


class RequestIDMiddleware:
    """ASGI correlation middleware for request_id + trace_id + W3C traceparent."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        request_id = _safe_request_id(_decode_header(headers, b"x-request-id"))
        trace_id, parent_span_id, response_traceparent = _trace_from_headers(headers)
        span_id = response_traceparent.split("-")[2]
        set_request_id(request_id)
        set_trace_id(trace_id)
        set_span_id(span_id)

        start = time.monotonic()
        status_holder = {"status": 0}
        caught_error: Exception | None = None

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((b"x-request-id", request_id.encode("ascii")))
                message["headers"].append((b"x-trace-id", trace_id.encode("ascii")))
                message["headers"].append((b"traceparent", response_traceparent.encode("ascii")))
                status_holder["status"] = int(message.get("status", 0) or 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            caught_error = exc
            raise
        finally:
            duration_s = time.monotonic() - start
            method = str(scope.get("method") or "")
            path = str(scope.get("path") or "")
            extra = {
                "endpoint": path,
                "method": method,
                "status": status_holder["status"],
                "latency_ms": round(duration_s * 1000, 1),
                "parent_span_id": parent_span_id or None,
                "secret_payloads_logged": False,
            }
            if caught_error is not None:
                extra["error_type"] = type(caught_error).__name__
                extra["error_message"] = str(caught_error)[:240]
            get_logger("system3.access").info("request", extra=extra)
            try:
                from dashboard.backend.metrics import record_request
            except ImportError:
                from metrics import record_request
            record_request(method, path, status_holder["status"], duration_s)
            set_request_id(None)
            set_trace_id(None)
            set_span_id(None)
