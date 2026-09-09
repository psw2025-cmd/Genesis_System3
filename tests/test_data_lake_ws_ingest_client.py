import asyncio
import json
from datetime import datetime, timezone

import pytest

from core.data.lake.backoff import BackoffPolicy
from core.data.lake.circuit_breaker import CircuitBreaker, CircuitState
from core.data.lake.local_parquet_writer import PartitionedParquetWriter
from core.data.lake.partitioning import MarketDataRecord
from core.data.lake.ws_ingest_client import BrokerFeedClient, DhanFeedClient, FeedConfig, WebSocketConnection


class FakeUploader:
    def __init__(self): self.uploads = []
    def upload_bytes(self, namespace, object_path, data):
        self.uploads.append((namespace, object_path, data)); return f"local://{namespace}/{object_path}"


class FakeConnection(WebSocketConnection):
    sent = []; closed = False; connected_url = None; preset_messages = []
    def __init__(self, ping_interval_s, ping_timeout_s): self._messages = list(FakeConnection.preset_messages); FakeConnection.sent=[]; FakeConnection.closed=False
    async def connect(self, url): FakeConnection.connected_url=url
    async def send(self, data): FakeConnection.sent.append(data)
    def __aiter__(self): return self
    async def __anext__(self):
        if not self._messages: raise StopAsyncIteration
        return self._messages.pop(0)
    async def close(self): FakeConnection.closed=True


class EchoFeedClient(BrokerFeedClient):
    def _subscribe_payload(self, symbols): return json.dumps({"sub": list(symbols)})
    def _parse_message(self, raw, receive_ts_utc):
        data=json.loads(raw)
        if data.get("type")=="heartbeat": return None
        return MarketDataRecord(instrument_type="index", symbol=data["symbol"], payload=data, receive_ts_utc=receive_ts_utc, source_ts_utc=datetime.fromtimestamp(data["ts"], tz=timezone.utc))


def test_connect_and_consume_writes_records():
    FakeConnection.preset_messages=[json.dumps({"type":"tick","symbol":"NIFTY","ts":1798000000}),json.dumps({"type":"heartbeat"})]
    writer=PartitionedParquetWriter(uploader=FakeUploader(), bucket="test")
    client=EchoFeedClient(FeedConfig(ws_url="wss://example.invalid/feed", subscribe_symbols=("NIFTY",)), writer, connection_factory=FakeConnection)
    asyncio.run(client._connect_and_consume())
    assert writer.pending_row_count()==1
    assert FakeConnection.closed is True


class FlakyThenStopClient(BrokerFeedClient):
    def __init__(self, config, writer, fail_count): super().__init__(config, writer, connection_factory=FakeConnection); self._fail_count=fail_count; self.call_count=0
    def _subscribe_payload(self, symbols): return ""
    def _parse_message(self, raw, receive_ts_utc): return None
    async def _connect_and_consume(self):
        self.call_count += 1
        if self.call_count <= self._fail_count: raise ConnectionError("simulated feed drop")
        self.stop()


def test_run_forever_retries_then_succeeds():
    writer=PartitionedParquetWriter(uploader=FakeUploader(), bucket="test")
    cfg=FeedConfig(ws_url="wss://example.invalid/feed", backoff=BackoffPolicy(base_seconds=.001, cap_seconds=.005, max_attempts=10), circuit_breaker=CircuitBreaker(failure_threshold=10, reset_timeout_s=.01))
    client=FlakyThenStopClient(cfg, writer, 3); asyncio.run(client.run_forever())
    assert client.call_count==4 and client.config.circuit_breaker.state is CircuitState.CLOSED


def test_dhan_parser_fails_closed():
    writer=PartitionedParquetWriter(uploader=FakeUploader(), bucket="test")
    client=DhanFeedClient(FeedConfig(ws_url="wss://example.invalid/feed"), writer, "index", {})
    with pytest.raises(NotImplementedError): client._parse_message(b"x", datetime.now(timezone.utc))
