"""Broker WebSocket market-feed ingestion client.

Wires together: reconnect-with-backoff, a circuit breaker, and the partitioned
Parquet writer. Runs as a long-lived asyncio task, intended for containerized
execution (Cloud Run job / GKE / any long-running container) - never inline
in a request-handling path.

IMPORTANT - scope of what is verified here:
This scaffold's connection lifecycle, backoff, circuit-breaker, and
writer-wiring are real and unit-tested (see tests/test_data_lake_*). The
*wire message format* of Dhan's live-market-feed WebSocket is NOT verified
against current Dhan API docs in this repo - there is no prior WebSocket
integration here to check against (see docs/API_ARCHITECTURE_AND_IMPROVEMENTS.md,
which documents REST-only polling and a stale Angel/SmartAPI code sample from
before the broker migration to Dhan). `DhanFeedClient._parse_message` is
therefore a clearly marked extension point: wire it to Dhan's documented
packet schema (ticker/quote/full-depth/20-depth packets) before relying on
this for real ingestion, rather than trusting the placeholder parsing here.
"""
from __future__ import annotations

import abc
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from .backoff import BackoffPolicy
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .gcs_parquet_writer import PartitionedParquetWriter
from .partitioning import MarketDataRecord

logger = logging.getLogger("system3.data_lake.ws_ingest_client")


@dataclass
class FeedConfig:
    ws_url: str
    subscribe_symbols: tuple[str, ...] = ()
    backoff: BackoffPolicy = field(default_factory=BackoffPolicy)
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    ping_interval_s: float = 15.0
    ping_timeout_s: float = 10.0


class WebSocketConnection(abc.ABC):
    """Thin seam so tests can inject a fake socket instead of a real
    `websockets` connection - keeps the reconnect/backoff logic testable
    without a live network dependency. Concrete subclasses take
    (ping_interval_s, ping_timeout_s) in __init__ so any subclass is
    interchangeable via the `connection_factory` callable used below."""

    def __init__(self, ping_interval_s: float, ping_timeout_s: float) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def connect(self, url: str) -> None: ...

    @abc.abstractmethod
    async def send(self, data: str | bytes) -> None: ...

    @abc.abstractmethod
    def __aiter__(self) -> "WebSocketConnection": ...

    @abc.abstractmethod
    async def __anext__(self) -> str | bytes: ...

    @abc.abstractmethod
    async def close(self) -> None: ...


class WebsocketsConnection(WebSocketConnection):
    """Real adapter over the `websockets` package (already a project dependency;
    see requirements_runtime.txt)."""

    def __init__(self, ping_interval_s: float, ping_timeout_s: float):
        self._ping_interval_s = ping_interval_s
        self._ping_timeout_s = ping_timeout_s
        self._ws = None

    async def connect(self, url: str) -> None:
        import websockets

        self._ws = await websockets.connect(
            url, ping_interval=self._ping_interval_s, ping_timeout=self._ping_timeout_s
        )

    async def send(self, data: str | bytes) -> None:
        assert self._ws is not None, "send() called before connect()"
        await self._ws.send(data)

    def __aiter__(self) -> "WebsocketsConnection":
        return self

    async def __anext__(self) -> str | bytes:
        assert self._ws is not None, "iteration started before connect()"
        return await self._ws.__anext__()  # type: ignore[attr-defined] - websockets supports `async for` at runtime

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()


class BrokerFeedClient(abc.ABC):
    """Generic reconnect/backoff/circuit-breaker loop. Subclasses supply the
    broker-specific subscribe payload and message parsing."""

    def __init__(
        self,
        config: FeedConfig,
        writer: PartitionedParquetWriter,
        connection_factory: type[WebSocketConnection] = WebsocketsConnection,
    ):
        self.config = config
        self.writer = writer
        self._connection_factory = connection_factory
        self._stop = asyncio.Event()

    @abc.abstractmethod
    def _subscribe_payload(self, symbols: Iterable[str]) -> str | bytes: ...

    @abc.abstractmethod
    def _parse_message(self, raw: str | bytes, receive_ts_utc: datetime) -> MarketDataRecord | None:
        """Return a MarketDataRecord, or None to skip (e.g. heartbeat frame)."""

    def stop(self) -> None:
        self._stop.set()

    async def run_forever(self) -> None:
        attempt = 0
        while not self._stop.is_set():
            try:
                self.config.circuit_breaker.guard()
            except CircuitOpenError as exc:
                logger.warning("circuit open, waiting before retry: %s", exc)
                await asyncio.sleep(self.config.circuit_breaker.reset_timeout_s)
                continue

            try:
                await self._connect_and_consume()
                attempt = 0  # clean disconnect after a working session resets backoff
                self.config.circuit_breaker.record_success()
            except Exception as exc:  # noqa: BLE001 - any failure triggers backoff+breaker
                self.config.circuit_breaker.record_failure()
                if self.config.backoff.exhausted(attempt):
                    logger.error("backoff attempts exhausted, giving up: %s", exc)
                    raise
                delay = self.config.backoff.delay_seconds(attempt, retry_after=_retry_after_hint(exc))
                logger.warning("feed connection failed (attempt %d): %s; retrying in %.2fs", attempt, exc, delay)
                attempt += 1
                await asyncio.sleep(delay)

    async def _connect_and_consume(self) -> None:
        conn = self._connection_factory(self.config.ping_interval_s, self.config.ping_timeout_s)
        await conn.connect(self.config.ws_url)
        try:
            await conn.send(self._subscribe_payload(self.config.subscribe_symbols))
            async for raw in conn:
                if self._stop.is_set():
                    break
                receive_ts_utc = datetime.now(timezone.utc)
                record = self._parse_message(raw, receive_ts_utc)
                if record is not None:
                    self.writer.add(record)
        finally:
            await conn.close()


def _retry_after_hint(exc: Exception) -> float | None:
    """Best-effort extraction of a Retry-After style hint from an exception
    raised by the underlying websocket/HTTP layer (e.g. a 429 upgrade
    rejection). Returns None when no such hint is present."""
    retry_after = getattr(exc, "retry_after", None)
    try:
        return float(retry_after) if retry_after is not None else None
    except (TypeError, ValueError):
        return None


class DhanFeedClient(BrokerFeedClient):
    """Dhan live-market-feed client scaffold.

    `_subscribe_payload` and `_parse_message` encode Dhan's DOCUMENTED request
    shape (instrument list keyed by security id + exchange segment) at a high
    level only; the exact packet/field layout must be verified against Dhan's
    current API docs before this reads real depth/option-chain data. Treat
    `_parse_message` below as a placeholder that raises NotImplementedError
    rather than silently emitting fabricated records - a silent
    synthetic/demo fallback here would violate issue #376's own acceptance
    criteria ("no silent synthetic/demo fallback").
    """

    def __init__(
        self,
        config: FeedConfig,
        writer: PartitionedParquetWriter,
        instrument_type: str,
        security_ids_by_symbol: dict[str, str],
        connection_factory: type[WebSocketConnection] = WebsocketsConnection,
    ):
        super().__init__(config, writer, connection_factory)
        self.instrument_type = instrument_type
        self.security_ids_by_symbol = security_ids_by_symbol

    def _subscribe_payload(self, symbols: Iterable[str]) -> str:
        import json

        instruments = [
            {"ExchangeSegment": "NSE_FNO", "SecurityId": self.security_ids_by_symbol[s]}
            for s in symbols
            if s in self.security_ids_by_symbol
        ]
        return json.dumps({"RequestCode": 15, "InstrumentCount": len(instruments), "InstrumentList": instruments})

    def _parse_message(self, raw: str | bytes, receive_ts_utc: datetime) -> MarketDataRecord | None:
        raise NotImplementedError(
            "Dhan wire-message parsing is not verified in this scaffold - implement against "
            "Dhan's current live-market-feed packet schema before use; see module docstring."
        )
