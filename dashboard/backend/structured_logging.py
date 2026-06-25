"""
Structured logging + request-ID correlation for the dashboard backend.

This is the new standard for anything touched going forward - it does
NOT retrofit the ~48 existing print() calls in app.py (and many more
across the other service modules). That would be a large, invasive,
high-risk diff for a codebase that has never had logging discipline,
for limited incremental value (the prints work fine functionally, they
just lack levels/structure/correlation). Tracked as backlog.

Usage:
    from dashboard.backend.structured_logging import get_logger
    logger = get_logger(__name__)
    logger.info("order created", extra={"order_id": order_id})
"""

import json
import logging
import os
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Optional

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def set_request_id(value: Optional[str]) -> None:
    _request_id_ctx.set(value)


class JsonFormatter(logging.Formatter):
    """One JSON object per line - the standard structured-log shape
    (timestamp, level, logger, message, request_id, plus any `extra=`
    fields the caller passed) so logs are greppable/parseable instead of
    free-text print() output."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id
        # Anything passed via logger.info(..., extra={...}) lands as
        # plain attributes on the record - pull back out anything that
        # isn't one of the standard LogRecord fields.
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
        return json.dumps(payload, default=str)


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
    """ASGI middleware: assigns a request ID (from X-Request-ID if the
    caller supplied one, otherwise a fresh uuid4) to every request,
    makes it available to get_request_id() for the duration of the
    request via a contextvar, and echoes it back in the response
    header so a client can correlate its request with backend logs."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        incoming = headers.get(b"x-request-id")
        request_id = incoming.decode("latin-1") if incoming else str(uuid.uuid4())
        set_request_id(request_id)
        start = time.monotonic()
        status_holder = {"status": 0}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((b"x-request-id", request_id.encode("latin-1")))
                status_holder["status"] = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_s = time.monotonic() - start
            method = scope.get("method")
            path = scope.get("path")
            get_logger("system3.access").info(
                "request",
                extra={
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration_s * 1000, 1),
                    "status": status_holder["status"],
                },
            )
            try:
                from dashboard.backend.metrics import record_request
            except ImportError:
                from metrics import record_request
            record_request(method or "", path or "", status_holder["status"], duration_s)
            set_request_id(None)
