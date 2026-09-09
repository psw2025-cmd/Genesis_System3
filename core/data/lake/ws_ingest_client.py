"""Broker WebSocket market-feed ingestion client for the local laptop runtime.

The lifecycle, retry/backoff, circuit breaker and local partitioned writer are
real. Dhan wire-message parsing remains deliberately unimplemented until the
current broker packet schema is verified; no synthetic fallback is allowed.
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
from .local_parquet_writer import PartitionedParquetWriter
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
    def __init__(self, ping_interval_s: float, ping_timeout_s: float):
        self._ping_interval_s = ping_interval_s
        self._ping_timeout_s = ping_timeout_s
        self._ws = None

    async def connect(self, url: str) -> None:
        import websockets
        self._ws = await websockets.connect(url, ping_interval=self._ping_interval_s, ping_timeout=self._ping_timeout_s)

    async def send(self, data: str | bytes) -> None:
        assert self._ws is not None, "send() called before connect()"
        await self._ws.send(data)

    def __aiter__(self) -> "WebsocketsConnection":
        return self

    async def __anext__(self) -> str | bytes:
        assert self._ws is not None, "iteration started before connect()"
        return await self._ws.__anext__()

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()


class BrokerFeedClient(abc.ABC):
    def __init__(self, config: FeedConfig, writer: PartitionedParquetWriter, connection_factory: type[WebSocketConnection] = WebsocketsConnection):
        self.config = config
        self.writer = writer
        self._connection_factory = connection_factory
        self._stop = asyncio.Event()

    @abc.abstractmethod
    def _subscribe_payload(self, symbols: Iterable[str]) -> str | bytes: ...

    @abc.abstractmethod
    def _parse_message(self, raw: str | bytes, receive_ts_utc: datetime) -> MarketDataRecord | None: ...

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
                attempt = 0
                self.config.circuit_breaker.record_success()
            except Exception as exc:
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
    retry_after = getattr(exc, "retry_after", None)
    try:
        return float(retry_after) if retry_after is not None else None
    except (TypeError, ValueError):
        return None


class DhanFeedClient(BrokerFeedClient):
    def __init__(self, config: FeedConfig, writer: PartitionedParquetWriter, instrument_type: str, security_ids_by_symbol: dict[str, str], connection_factory: type[WebSocketConnection] = WebsocketsConnection):
        super().__init__(config, writer, connection_factory)
        self.instrument_type = instrument_type
        self.security_ids_by_symbol = security_ids_by_symbol

    def _subscribe_payload(self, symbols: Iterable[str]) -> str:
        import json
        instruments = [{"ExchangeSegment": "NSE_FNO", "SecurityId": self.security_ids_by_symbol[s]} for s in symbols if s in self.security_ids_by_symbol]
        return json.dumps({"RequestCode": 15, "InstrumentCount": len(instruments), "InstrumentList": instruments})

    def _parse_message(self, raw: str | bytes, receive_ts_utc: datetime) -> MarketDataRecord | None:
        raise NotImplementedError("Dhan wire-message parsing is not verified; implement against the current documented packet schema before use")
