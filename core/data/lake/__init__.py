"""Data lake ingestion and storage scaffold for issue #376 (P0 data truth / historical lake).

Submodules:
- partitioning: point-in-time partition path + record schema helpers.
- backoff: exponential backoff with full jitter.
- circuit_breaker: generic CLOSED/OPEN/HALF_OPEN circuit breaker.
- secrets: environment-variable-first, Secret-Manager-fallback credential loader.
- gcs_parquet_writer: buffered partitioned Parquet writer targeting GCS.
- ws_ingest_client: broker WebSocket ingestion client wiring backoff + circuit
  breaker + the writer together. The exact Dhan wire-message schema is NOT
  verified in this scaffold (no WebSocket feed exists elsewhere in this repo
  to cross-check against) - `DhanFeedClient._parse_message` is a clearly
  marked extension point, not a verified protocol implementation.
"""
