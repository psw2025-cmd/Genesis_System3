"""Local-laptop market-data ingestion and storage helpers.

The package provides point-in-time partitioning, retry/backoff, circuit-breaker
logic, local secret resolution, a partitioned local Parquet writer, and the
broker WebSocket ingestion scaffold. Broker wire parsing remains fail-closed
until verified against the current Dhan protocol.
"""
