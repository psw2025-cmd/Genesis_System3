# Genesis System3 ? Datasource Truth Classification Matrix
**Audit Status:** 100% COMPLETE | **UNKNOWN Sources:** 0 (PASSED)

| ID | Datasource Name | Protocol | Classification | Authority | Operating Window | Evidence Emitted |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DS-001` | **DhanHQ Live WebSocket Feed** | `WSS / Binary Protobuf` | `REAL_VERIFIED` | DhanHQ Broker API Gateway (Live Colocation Stream) | Mon-Fri 09:15 - 15:30 IST | Packet timestamp, Exchange seq number, raw tick SHA256 |
| `DS-002` | **DhanHQ REST Market Quotes & Option Chains** | `HTTPS / JSON` | `REAL_VERIFIED` | DhanHQ REST Gateway (/v2/marketfeed/quote, /v2/optionchain) | Mon-Fri 09:15 - 15:30 IST | HTTP status 200, JWT token proof version, response body SHA256 |
| `DS-003` | **Dhan Scrip Master Universe** | `HTTPS / CSV Download` | `REAL_VERIFIED` | Official Dhan Scrip Master (https://images.dhan.co/api-data/api-scrip-master.csv) | Static Daily Ingestion (117,776 scrips, 228 underlyings) | Row count validation (assert rows > 100,000), SHA256 integrity hash |
| `DS-004` | **NSE / BSE State Cache Reference** | `In-Memory / JSON File` | `CACHED` | Exchange-reconciled closing prices and ATM strike grids | Session end snapshot (15:30 IST) | State snapshot timestamp, strike boundaries, spot baseline |
| `DS-005` | **DuckDB & Parquet Columnar Lake** | `DuckDB OLAP / PyArrow Parquet` | `CACHED` | System3 Local Columnar Persistence (storage/parquet/) | 24/7 Hot In-Memory + Cold Parquet Snapshot | Parquet snappy compression metadata, row group count, column schema |
| `DS-006` | **Virtual Paper Order Matching Engine** | `In-Memory ASGI Execution Gateway` | `SIMULATED` | Genesis System3 Paper Ledger (/api/dhan/orders/dynamic-bind) | Active during simulation and backtest cycles | Virtual fill receipt, simulated slippage (0.15 pts), paper ledger transaction ID |
| `DS-007` | **Portfolio Risk Monte Carlo VaR Simulator** | `In-Memory Quant Math Engine` | `SYNTHETIC` | System3 Risk Management Engine (/api/risk/portfolio) | Evaluated upon portfolio state change | Confidence interval (95%), simulated covariance matrix, scenario count |
| `DS-008` | **Unit Test Harness Fixtures** | `Local Python Mock Fixtures` | `MOCK` | Isolated Test Fixtures (tests/fixtures/*.json) | CI and Local pytest runs only | Test assertion receipts, mock function invocation counts |
| `DS-009` | **Operator Demo Landing Canvas** | `React Static Components` | `DEMO` | Dashboard Frontend Static Showcase Cards | Fallback when all upstream connectivity is severed | UI demo badge indicator flag in DOM tree |