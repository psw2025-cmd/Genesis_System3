import asyncio
import json
from datetime import datetime, timezone

import pytest

from core.data.lake.backoff import BackoffPolicy
from core.data.lake.circuit_breaker import CircuitBreaker, CircuitState
from core.data.lake.gcs_parquet_writer import PartitionedParquetWriter
from core.data.lake.partitioning import MarketDataRecord
from core.data.lake.ws_ingest_client import (
    BrokerFeedClient,
    DhanFeedClient,
    FeedConfig,
    WebSocketConnection,
)


class FakeUploader:
    def __init__(self):
        self.uploads = []

    def upload_bytes(self, bucket, object_path, data):
        self.uploads.append((bucket, object_path, data))
        return f"gs://{bucket}/{object_path}"


class FakeConnection(WebSocketConnection):
    """Records connect/send/close calls and replays a fixed message list."""

    sent: list = []
    closed = False
    connected_url = None

    def __init__(self, ping_interval_s, ping_timeout_s):
        self._messages = list(FakeConnection.preset_messages)
        FakeConnection.sent = []
        FakeConnection.closed = False

    async def connect(self, url):
        FakeConnection.connected_url = url

    async def send(self, data):
        FakeConnection.sent.append(data)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)

    async def close(self):
        FakeConnection.closed = True


class EchoFeedClient(BrokerFeedClient):
    def _subscribe_payload(self, symbols):
        return json.dumps({"sub": list(symbols)})

    def _parse_message(self, raw, receive_ts_utc):
        data = json.loads(raw)
        if data.get("type") == "heartbeat":
            return None
        return MarketDataRecord(
            instrument_type="index",
            symbol=data["symbol"],
            payload=data,
            receive_ts_utc=receive_ts_utc,
            source_ts_utc=datetime.fromtimestamp(data["ts"], tz=timezone.utc),
        )


def test_connect_and_consume_writes_parsed_records_and_skips_none():
    FakeConnection.preset_messages = [
        json.dumps({"type": "tick", "symbol": "NIFTY", "ts": 1798000000}),
        json.dumps({"type": "heartbeat"}),
        json.dumps({"type": "tick", "symbol": "NIFTY", "ts": 1798000005}),
    ]
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    config = FeedConfig(ws_url="wss://example.invalid/feed", subscribe_symbols=("NIFTY",))
    client = EchoFeedClient(config, writer, connection_factory=FakeConnection)

    asyncio.run(client._connect_and_consume())

    assert writer.pending_row_count() == 2  # heartbeat skipped
    assert FakeConnection.connected_url == "wss://example.invalid/feed"
    assert FakeConnection.sent == [json.dumps({"sub": ["NIFTY"]})]
    assert FakeConnection.closed is True


class FlakyThenStopClient(BrokerFeedClient):
    """Test double: fails `fail_count` times then stops itself on success -
    isolates run_forever's retry orchestration from real socket I/O."""

    def __init__(self, config, writer, fail_count):
        super().__init__(config, writer, connection_factory=FakeConnection)
        self._fail_count = fail_count
        self.call_count = 0

    def _subscribe_payload(self, symbols):
        return ""

    def _parse_message(self, raw, receive_ts_utc):
        return None

    async def _connect_and_consume(self):
        self.call_count += 1
        if self.call_count <= self._fail_count:
            raise ConnectionError("simulated feed drop")
        self.stop()


def test_run_forever_retries_with_backoff_then_succeeds():
    FakeConnection.preset_messages = []
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    config = FeedConfig(
        ws_url="wss://example.invalid/feed",
        backoff=BackoffPolicy(base_seconds=0.001, cap_seconds=0.005, max_attempts=10),
        circuit_breaker=CircuitBreaker(failure_threshold=10, reset_timeout_s=0.01),
    )
    client = FlakyThenStopClient(config, writer, fail_count=3)

    asyncio.run(client.run_forever())

    assert client.call_count == 4  # 3 failures + 1 success
    assert client.config.circuit_breaker.state is CircuitState.CLOSED


def test_run_forever_raises_once_backoff_exhausted():
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    config = FeedConfig(
        ws_url="wss://example.invalid/feed",
        backoff=BackoffPolicy(base_seconds=0.001, cap_seconds=0.005, max_attempts=2),
        circuit_breaker=CircuitBreaker(failure_threshold=10, reset_timeout_s=0.01),
    )
    client = FlakyThenStopClient(config, writer, fail_count=999)

    with pytest.raises(ConnectionError):
        asyncio.run(client.run_forever())


def test_dhan_feed_client_subscribe_payload_maps_symbols_to_security_ids():
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    config = FeedConfig(ws_url="wss://example.invalid/feed", subscribe_symbols=("NIFTY", "UNKNOWN"))
    client = DhanFeedClient(
        config, writer, instrument_type="index", security_ids_by_symbol={"NIFTY": "13"}, connection_factory=FakeConnection
    )
    payload = json.loads(client._subscribe_payload(config.subscribe_symbols))
    assert payload["InstrumentCount"] == 1
    assert payload["InstrumentList"] == [{"ExchangeSegment": "NSE_FNO", "SecurityId": "13"}]


def test_dhan_feed_client_parse_message_is_not_a_silent_fabrication():
    """Issue #376 explicitly forbids a silent synthetic/demo fallback - the
    unverified Dhan wire parser must fail loudly, not invent data."""
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    config = FeedConfig(ws_url="wss://example.invalid/feed")
    client = DhanFeedClient(config, writer, instrument_type="index", security_ids_by_symbol={})
    with pytest.raises(NotImplementedError):
        client._parse_message(b"\x00\x01", datetime.now(timezone.utc))
