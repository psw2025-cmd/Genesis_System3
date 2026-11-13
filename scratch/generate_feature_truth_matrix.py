import os
import sys

# Ensure current working directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from matrix_builder_core import build_feature_truth_matrix


def main():
    wb, render_sheet = build_feature_truth_matrix()

    # ==========================================
    # 1. API_ENDPOINTS
    # ==========================================
    api_endpoints_data = [
        # --- Overlapping Endpoints ---
        {
            "Feature Name": "GET /api/broker/status",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:6638 & dashboard/backend/app.py:824",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard integrates with broker_truth_validator.py to perform multi-field truth checks (zero-order check, token validity, paper/live status, and latency); content returns static hardcoded JSON.",
            "Evidence": "dashboard/backend/app.py lines 824-870 calls build_broker_truth_report(); content/app/app.py line 6638 returns static status dict."
        },
        {
            "Feature Name": "GET /api/health",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:4542 & dashboard/backend/app.py:4276",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard dynamically checks database connectivity, memory guard RSS status, paper engine health, and background worker state; content returns hardcoded uptime and simulated instrument counts.",
            "Evidence": "dashboard/backend/app.py lines 4276-4310 queries get_memory_stats() and state stores; content/app/app.py line 4542 returns hardcoded total_monitored_instruments: 2048."
        },
        {
            "Feature Name": "GET /api/market/top-gainers",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:7370 & dashboard/backend/app.py:11736",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard integrates with gain_rank_spot_enrichment.py to pull live Dhan spot prices and verifies F&O contract eligibility; content serves unverified cached or simulated fallback lists.",
            "Evidence": "dashboard/backend/gain_rank_spot_enrichment.py enriches gainers with live Dhan quotes; content/app/app.py line 7370 falls back to mock scanner list."
        },
        {
            "Feature Name": "GET /api/options/gainers",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:2890 & dashboard/backend/app.py:11755",
            "Destination File": "dashboard/backend/contract_gain_scanner.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard uses contract_gain_scanner.py with dynamic strike discovery, volume thresholds, and multi-validation audit; content uses a hardcoded synthetic strike array from 1000 to 1500.",
            "Evidence": "dashboard/backend/contract_gain_scanner.py vs content/app/app.py lines 188 & 2890 (STRIKES = list(range(1000, 1505, 5)))."
        },
        {
            "Feature Name": "GET /api/orders",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:4846 & dashboard/backend/app.py:9694",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard integrates with CloudPaperEngine and FirestoreStateBackend for persistent, audit-proven paper order history; content returns ephemeral in-memory orders array.",
            "Evidence": "dashboard/backend/routers/trading.py line 116 queries CloudPaperEngine state; content/app/app.py line 4846 returns global in-memory list."
        },
        {
            "Feature Name": "GET /api/pnl",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:4498 & dashboard/backend/routers/trading.py:116",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard computes mark-to-market P&L rigorously validated by live_profit_validator.py with slippage and commission calculations; content returns simulated random walk numbers.",
            "Evidence": "dashboard/backend/live_profit_validator.py multi-validates broker vs market P&L; content/app/app.py line 4498 returns synthetic realized/unrealized floats."
        },
        {
            "Feature Name": "GET /api/positions",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:4810 & dashboard/backend/routers/trading.py:143",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard paper positions are tied to position_reconciliation.py and paper_ledger_guard.py for audit compliance; content returns an unvalidated in-memory dictionary.",
            "Evidence": "dashboard/backend/position_reconciliation.py reconciles position book; content/app/app.py line 4810 returns static mock array."
        },
        {
            "Feature Name": "GET /api/risk",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:4722 & dashboard/backend/app.py:8612",
            "Destination File": "dashboard/backend/risk_management.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard computes parametric VaR, portfolio beta, Greek exposure limits, and capital utilization via risk_management.py; content returns static hardcoded JSON risk thresholds.",
            "Evidence": "dashboard/backend/risk_management.py calculates portfolio risk metrics; content/app/app.py line 4722 returns fixed dictionary values."
        },
        {
            "Feature Name": "GET /funds",
            "Classification": "Present in both",
            "Source File": "content/app/dhan_account_router.py:100 & dashboard/backend/routers/broker.py:137",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Content router executes authenticated read-only API calls via core.brokers.dhan.dhan_readonly.get_funds(); dashboard router has placeholder mock structure. Merge required.",
            "Evidence": "content/app/dhan_account_router.py line 100 executes _raw_get_funds(); dashboard/backend/routers/broker.py line 137 returns mock available margin."
        },
        {
            "Feature Name": "GET /holdings",
            "Classification": "Present in both",
            "Source File": "content/app/dhan_account_router.py:114 & dashboard/backend/routers/broker.py:119",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Content router queries live Dhan broker holdings via core.brokers.dhan.dhan_readonly.get_holdings() with credential parsing; dashboard router returns mock data. Merge required.",
            "Evidence": "content/app/dhan_account_router.py line 114 executes _raw_get_holdings(); dashboard/backend/routers/broker.py line 119 returns mock holdings list."
        },
        {
            "Feature Name": "GET /positions (Broker)",
            "Classification": "Present in both",
            "Source File": "content/app/dhan_account_router.py:131 & dashboard/backend/app.py:11125",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Content retrieves live Dhan broker positions via core client, essential for proving 0 real positions; dashboard route returns internal paper positions. Merge required.",
            "Evidence": "content/app/dhan_account_router.py line 131 calls _raw_get_positions(); dashboard/backend/app.py line 11125 queries paper runtime state."
        },
        {
            "Feature Name": "GET /ui",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:1137 & dashboard/backend/app.py:662",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard mounts the full Next.js/React production UI with static caching, responsive navigation, and tabbed analytics; content serves a monolithic 154KB premium.html template.",
            "Evidence": "dashboard/backend/app.py lines 662-720 mounts frontend static build; content/app/app.py line 1137 reads templates/premium.html."
        },
        {
            "Feature Name": "POST /emergency-exit",
            "Classification": "Present in both",
            "Source File": "content/app/app.py:6966 & dashboard/backend/app.py:11258",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard triggers atomic shutdown of trading loops, cancels all active paper orders, clears in-flight state, logs proof hash, and halts daemon; content flips in-memory flag.",
            "Evidence": "dashboard/backend/app.py lines 11258-11295 executes CloudPaperEngine.close_all() and state sync; content/app/app.py line 6966 sets emergency_stop = True."
        },

        # --- Content-Only Endpoints ---
        {
            "Feature Name": "GET /api/verified-market",
            "Classification": "Present in content only",
            "Source File": "content/app/verified_market.py:294",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "content/app",
            "Reason": "Implements live, authenticated Dhan /v2/marketfeed/quote REST requests with IST market session detection and 1-second TTL mutex caching. Must be merged into dashboard.",
            "Evidence": "content/app/verified_market.py lines 294-309 performs POST to MARKET_URL with Dhan client/token headers."
        },
        {
            "Feature Name": "GET /profile",
            "Classification": "Present in content only",
            "Source File": "content/app/dhan_account_router.py:77",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Provides read-only Dhan client profile retrieval with client ID redaction and token validation. Crucial for verifying broker connectivity.",
            "Evidence": "content/app/dhan_account_router.py line 77 calls core.brokers.dhan.dhan_readonly.get_profile()."
        },
        {
            "Feature Name": "GET /summary",
            "Classification": "Present in content only",
            "Source File": "content/app/dhan_account_router.py:145",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Consolidates funds, margin, holdings count, and open positions into a clean read-only broker summary payload.",
            "Evidence": "content/app/dhan_account_router.py lines 145-165 builds unified account summary."
        },
        {
            "Feature Name": "GET /orders (Broker)",
            "Classification": "Present in content only",
            "Source File": "content/app/dhan_account_router.py:138",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Directly queries Dhan broker order book to independently prove 0 real orders were sent. Indispensable for Layer 6 proof.",
            "Evidence": "content/app/dhan_account_router.py line 138 calls core.brokers.dhan.dhan_readonly.get_orders()."
        },
        {
            "Feature Name": "GET /api/data/provenance",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2498",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "Merge required",
            "Reason": "Exposes SHA-256 data provenance chain, feed origins, and audit metadata. Must be merged with dashboard's proof_ledger_service.py.",
            "Evidence": "content/app/app.py lines 2498-2550 returns cryptographic envelope with sha256_hash."
        },
        {
            "Feature Name": "GET /api/hash-chain",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6190",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "Merge required",
            "Reason": "Validates cryptographic block sequence for ledger transitions. Merge required with SQLite/Firestore proof ledger.",
            "Evidence": "content/app/app.py line 6190 returns block sequence and hash chain links."
        },
        {
            "Feature Name": "GET /api/route-health",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2418",
            "Destination File": "dashboard/backend/scanner_telemetry.py",
            "Winner": "content/app",
            "Reason": "Calculates microsecond route latency telemetry and endpoint availability across all registered routes.",
            "Evidence": "content/app/app.py lines 2418-2495 records request start/end delta and rolling p95 latency."
        },
        {
            "Feature Name": "GET /api/evidence",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2614",
            "Destination File": "dashboard/backend/ml_evidence_store.py",
            "Winner": "dashboard/backend",
            "Reason": "Content provides simple in-memory evidence store; dashboard has ml_evidence_store.py with disk/Firestore persistence. Winner: dashboard (Merge endpoint into ml_evidence_store).",
            "Evidence": "dashboard/backend/ml_evidence_store.py persists predictions with timestamps; content/app/app.py line 2614 returns in-memory dict."
        },
        {
            "Feature Name": "GET /api/truth/proof/{id}",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:5906",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "Merge required",
            "Reason": "Retrieves specific cryptographic proof receipt by ID. Fits into proof_ledger_service.py.",
            "Evidence": "content/app/app.py line 5906 looks up proof by UUID."
        },
        {
            "Feature Name": "GET /api/market/breadth",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2037",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Institutional market breadth telemetry (advances, declines, unchanged). Must be wired to real Dhan quote scanner.",
            "Evidence": "content/app/app.py lines 2037-2090 computes breadth metrics from symbol cache."
        },
        {
            "Feature Name": "GET /api/market/sectors",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2101",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Sectoral performance breakdown across 14 market sectors. In content, weights are static; merge with dashboard live pricing.",
            "Evidence": "content/app/app.py lines 2101-2120 returns SECTORS_DATA array."
        },
        {
            "Feature Name": "GET /api/market/inventory",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:1853",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Provides full monitored inventory across 2,000+ instruments and 1,649 F&O contracts. Merge with master JSON storage.",
            "Evidence": "content/app/app.py line 1853 counts active symbols from Dhan instrument master."
        },
        {
            "Feature Name": "GET /api/market/missing-symbols",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2121",
            "Destination File": "dashboard/backend/fo_eligibility_filter.py",
            "Winner": "Merge required",
            "Reason": "Audits symbols missing from instrument master or quote feed; merge into fo_eligibility_filter.py.",
            "Evidence": "content/app/app.py line 2121 identifies unresolved ticker symbols."
        },
        {
            "Feature Name": "GET /api/market",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2165",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Content provides high-level overview dict; dashboard has /api/market/live_board which is far richer and dynamic. Winner: dashboard.",
            "Evidence": "content/app/app.py line 2165 vs dashboard/backend/app.py line 1020."
        },
        {
            "Feature Name": "GET /api/dhan/live-connectivity",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2222",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Actively probes Dhan REST API connectivity, ping latency, and auth token validity. Merge into broker router.",
            "Evidence": "content/app/app.py lines 2222-2280 sends HEAD request to Dhan API endpoint."
        },
        {
            "Feature Name": "GET /api/dhan/discovery/full-market",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4042",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Discovers tradable F&O symbols across segments from Dhan master scrip cache.",
            "Evidence": "content/app/app.py line 4042 returns market segment discovery tree."
        },
        {
            "Feature Name": "GET /api/dhan/discovery/chain-subscriptions",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4114",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Maps active Dhan security IDs required for options chain WebSocket/REST polling.",
            "Evidence": "content/app/app.py line 4114 maps contract strike security tokens."
        },
        {
            "Feature Name": "GET /api/options/intelligence",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2718",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Content aggregates simulated PCR, Max Pain, and ATM straddle prices; dashboard computes live PCR and Greeks in routers/chain.py. Winner: dashboard.",
            "Evidence": "content/app/app.py line 2718 vs dashboard/backend/routers/chain.py line 180."
        },
        {
            "Feature Name": "GET /api/options/greeks",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2764",
            "Destination File": "dashboard/backend/greeks_calculator.py",
            "Winner": "dashboard/backend",
            "Reason": "Content computes Greeks using inline math in app.py; dashboard has modular, vectorized greeks_calculator.py with IV solver. Winner: dashboard.",
            "Evidence": "content/app/app.py line 2764 calls _calc_bs_greeks(); dashboard has dedicated greeks_calculator.py."
        },
        {
            "Feature Name": "GET /api/options/oi-buildup",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3266",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Content simulates Long Buildup, Short Covering, Long Unwinding; dashboard has real contract gain scanner and chain analysis. Winner: dashboard.",
            "Evidence": "content/app/app.py line 3266 vs dashboard/backend/contract_gain_scanner.py."
        },
        {
            "Feature Name": "GET /api/chain/{symbol}",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:7186",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Compatibility endpoint returning simulated chain; dashboard has complete /api/options/chain/{symbol} with full expiry selection and contract metadata. Winner: dashboard.",
            "Evidence": "dashboard/backend/routers/chain.py line 45 vs content/app/app.py line 7186."
        },
        {
            "Feature Name": "GET /api/paper/ledger",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3322",
            "Destination File": "dashboard/backend/cloud_paper_engine.py",
            "Winner": "dashboard/backend",
            "Reason": "Content returns simulated trades list; dashboard has CloudPaperEngine and paper_ledger_guard.py with hash chain and ledger proof. Winner: dashboard.",
            "Evidence": "dashboard/backend/paper_ledger_guard.py vs content/app/app.py line 3322."
        },
        {
            "Feature Name": "GET /api/paper/lifecycle",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3562",
            "Destination File": "dashboard/backend/cloud_paper_engine.py",
            "Winner": "dashboard/backend",
            "Reason": "Traces signal -> risk -> fill -> position -> closure lifecycle. Dashboard implements this in cloud_paper_engine.py with persistent state. Winner: dashboard.",
            "Evidence": "dashboard/backend/cloud_paper_engine.py step() method vs content/app/app.py line 3562."
        },
        {
            "Feature Name": "GET /api/ml/forecast-vs-actual",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3654",
            "Destination File": "dashboard/backend/paper_prediction_outcome_audit.py",
            "Winner": "Merge required",
            "Reason": "Institutional Layer 5 verification comparing timestamped predictions with matured actuals. Merge schema with dashboard outcome audit.",
            "Evidence": "content/app/app.py line 3654 computes directional hit rate and MAE vs dashboard/backend/paper_prediction_outcome_audit.py."
        },
        {
            "Feature Name": "GET /api/ml/prediction-audit",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3802",
            "Destination File": "dashboard/backend/ml_evidence_store.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard persists prediction audits with cryptographic receipts in ml_evidence_store.py; content uses in-memory ring buffer. Winner: dashboard.",
            "Evidence": "dashboard/backend/ml_evidence_store.py vs content/app/app.py line 3802."
        },
        {
            "Feature Name": "GET /api/ml/benchmark",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:3986",
            "Destination File": "dashboard/backend/backtesting.py",
            "Winner": "dashboard/backend",
            "Reason": "Content compares strategy return against synthetic Nifty benchmark; dashboard computes real alpha/beta in backtesting.py. Winner: dashboard.",
            "Evidence": "dashboard/backend/backtesting.py calculate_metrics() vs content/app/app.py line 3986."
        },
        {
            "Feature Name": "GET /api/decision",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4458",
            "Destination File": "dashboard/backend/autonomous_paper_core.py",
            "Winner": "dashboard/backend",
            "Reason": "Content returns simulated BUY/SELL signals; dashboard has autonomous_paper_core.py with multi-indicator gating and risk validation. Winner: dashboard.",
            "Evidence": "dashboard/backend/autonomous_paper_core.py vs content/app/app.py line 4458."
        },
        {
            "Feature Name": "GET /api/depth",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4918",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Provides L2 market depth for underlying and strikes; merge with Dhan depth socket when live feed connected.",
            "Evidence": "content/app/app.py line 4918 returns 5-level bid/ask depth."
        },
        {
            "Feature Name": "GET /api/history",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4882",
            "Destination File": "dashboard/backend/index_history_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard has dedicated index_history_service.py pulling multi-timeframe candles; content uses static mock candles. Winner: dashboard.",
            "Evidence": "dashboard/backend/index_history_service.py vs content/app/app.py line 4882."
        },
        {
            "Feature Name": "GET /api/kill-switch",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:5950",
            "Destination File": "dashboard/backend/profit_governor.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard profit_governor.py monitors max daily drawdown and trips automated kill-switch atomically; content is passive status check. Winner: dashboard.",
            "Evidence": "dashboard/backend/profit_governor.py vs content/app/app.py line 5950."
        },
        {
            "Feature Name": "GET /api/var",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6238",
            "Destination File": "dashboard/backend/risk_management.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard computes 95% and 99% historical & parametric Value at Risk across portfolio in risk_management.py. Winner: dashboard.",
            "Evidence": "dashboard/backend/risk_management.py calculate_var() vs content/app/app.py line 6238."
        },
        {
            "Feature Name": "GET /api/drawdown",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6258",
            "Destination File": "dashboard/backend/risk_management.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard tracks peak-to-trough high watermark and duration continuously. Winner: dashboard.",
            "Evidence": "dashboard/backend/risk_management.py vs content/app/app.py line 6258."
        },
        {
            "Feature Name": "POST /api/v1/placeorder & GET /api/v1/placeorder",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6726 & 6758",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "content/app",
            "Reason": "Emulates OpenAlgo webhook order placement protocol while strictly blocking real broker orders and routing to paper engine. Merge required.",
            "Evidence": "content/app/app.py lines 6726-6758 enforces ANALYZE_MODE=1 and records order in paper book."
        },
        {
            "Feature Name": "Telegram Routes (5 endpoints: status, outbox, test-alert, dispatch, command)",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6386-6550",
            "Destination File": "dashboard/backend/alerts_system.py",
            "Winner": "Merge required",
            "Reason": "Content implements complete JSONL outbox logging, custom message dispatch, and bot command router. Merge into dashboard alerts system.",
            "Evidence": "content/app/app.py lines 6386-6550 & content/app/reports/telegram_outbox.jsonl."
        },
        {
            "Feature Name": "GET /api/settings",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:5970",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard has secure config loading with environment variable overrides and Firestore configuration sync. Winner: dashboard.",
            "Evidence": "dashboard/backend/security_policy.py vs content/app/app.py line 5970."
        },
        {
            "Feature Name": "GET /api/logs",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6106",
            "Destination File": "dashboard/backend/structured_logging.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard uses structured JSON logging with correlation IDs, Google Cloud Logging integration, and log levels. Winner: dashboard.",
            "Evidence": "dashboard/backend/structured_logging.py vs content/app/app.py line 6106."
        },
        {
            "Feature Name": "GET /api/metrics",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6130",
            "Destination File": "dashboard/backend/metrics.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard implements Prometheus-compatible metrics endpoint tracking request rate, error codes, and latencies. Winner: dashboard.",
            "Evidence": "dashboard/backend/metrics.py vs content/app/app.py line 6130."
        },
        {
            "Feature Name": "GET /api/audit",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:6170",
            "Destination File": "dashboard/backend/multi_validation_audit.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard has multi_validation_audit.py providing 12-layer institutional audit checks; content returns 4 hardcoded status fields. Winner: dashboard.",
            "Evidence": "dashboard/backend/multi_validation_audit.py vs content/app/app.py line 6170."
        },
        {
            "Feature Name": "GET /api/routes",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:1189",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "content/app",
            "Reason": "Dynamic route auto-discovery endpoint returning path, name, methods, and status for all registered FastAPI routes. Useful for monitoring.",
            "Evidence": "content/app/app.py lines 1189-1220 inspects app.routes dynamically."
        },

        # --- Key Dashboard-Only Endpoints ---
        {
            "Feature Name": "POST /api/auth/session, GET /api/auth/status, POST /api/auth/logout",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:612-660",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Session token management, secure HTTP-only cookies, and brute-force mitigation completely missing from content.",
            "Evidence": "dashboard/backend/app.py lines 612-660."
        },
        {
            "Feature Name": "GET /api/state & GET /api/state/history",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:750-800",
            "Destination File": "dashboard/backend/runtime_state_store.py",
            "Winner": "dashboard/backend",
            "Reason": "Provides full state transitions history with atomic snapshots and Firestore cloud persistence.",
            "Evidence": "dashboard/backend/runtime_state_store.py & firestore_state_backend.py."
        },
        {
            "Feature Name": "GET /api/market/live_board & GET /api/market/trajectories",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:1020-1120",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Real-time market board aggregating multi-timeframe price action, momentum trajectories, and volatility smiles.",
            "Evidence": "dashboard/backend/app.py lines 1020-1120."
        },
        {
            "Feature Name": "GET /api/options/chains & GET /api/options/straddles",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/routers/chain.py:120-250",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Advanced multi-expiry options chains, combined straddle pricing, and strike liquidity analysis.",
            "Evidence": "dashboard/backend/routers/chain.py lines 120-250."
        },
        {
            "Feature Name": "GET /api/accuracy_trend & GET /api/ml/drift & GET /api/ml/feature_importance",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/routers/ml.py:200-500",
            "Destination File": "dashboard/backend/routers/ml.py",
            "Winner": "dashboard/backend",
            "Reason": "Institutional ML monitoring: directional accuracy trends, Kolmogorov-Smirnov data drift tests, and Shapley feature weights.",
            "Evidence": "dashboard/backend/routers/ml.py & accuracy_trend_service.py."
        },
        {
            "Feature Name": "GET /api/audit/comprehensive & GET /api/auto_gates",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:3200-3350",
            "Destination File": "dashboard/backend/multi_validation_audit.py",
            "Winner": "dashboard/backend",
            "Reason": "Production automated audit evaluating broker truth, paper ledger sequence, option strike visibility, and auto-gates.",
            "Evidence": "dashboard/backend/multi_validation_audit.py & auto_gates_service.py."
        },
        {
            "Feature Name": "GET /api/agent/* & POST /agent-full-control (11 endpoints)",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:2474-2700 & 11672",
            "Destination File": "dashboard/backend/upgrade_agent.py",
            "Winner": "dashboard/backend",
            "Reason": "Autonomous agent governance: self-diagnostic issue tracking, memory recall, upgrade plan execution, and rollback safeguards.",
            "Evidence": "dashboard/backend/upgrade_agent.py."
        },
        {
            "Feature Name": "GET /api/backtest/results & POST /api/backtest/run",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:8800-8950",
            "Destination File": "dashboard/backend/backtesting.py",
            "Winner": "dashboard/backend",
            "Reason": "Full historical strategy backtester with customizable parameter grids, drawdown simulations, and sharpe ratio calculations.",
            "Evidence": "dashboard/backend/backtesting.py."
        },
        {
            "Feature Name": "GET /api/metrics/memory & GET /api/telemetry/scanner",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:11800-11900",
            "Destination File": "dashboard/backend/middleware/memory_guard.py",
            "Winner": "dashboard/backend",
            "Reason": "Live telemetry of process RSS memory, garbage collection passes, and scanner latency to ensure zero Cloud Run crashes.",
            "Evidence": "dashboard/backend/middleware/memory_guard.py & scanner_telemetry.py."
        }
    ]

    # ==========================================
    # 2. BROKER_FEATURES
    # ==========================================
    broker_features_data = [
        {
            "Feature Name": "Broker Connectivity & Heartbeat Check",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/app.py & broker_truth_validator.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard queries multi-point truth indicators, records round-trip ping latency, and validates token expiration; content does shallow reachability.",
            "Evidence": "dashboard/backend/broker_truth_validator.py build_broker_truth_report() vs content/app/app.py get_broker_status()."
        },
        {
            "Feature Name": "Read-Only Broker Account Profile",
            "Classification": "Better implementation in content",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Content directly executes core.brokers.dhan.dhan_readonly.get_profile() with proper secret masking; dashboard has mock stub.",
            "Evidence": "content/app/dhan_account_router.py lines 77-98."
        },
        {
            "Feature Name": "Read-Only Broker Funds & Margins",
            "Classification": "Better implementation in content",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Queries live collateral, available cash, and utilized margins directly from Dhan API; dashboard returns placeholder dictionary.",
            "Evidence": "content/app/dhan_account_router.py lines 100-112 calls _raw_get_funds()."
        },
        {
            "Feature Name": "Read-Only Broker Holdings Function",
            "Classification": "Better implementation in content",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Fetches real demat equity holdings from Dhan read-only API; dashboard has static mock items.",
            "Evidence": "content/app/dhan_account_router.py lines 114-129 calls _raw_get_holdings()."
        },
        {
            "Feature Name": "Read-Only Broker Live Positions",
            "Classification": "Better implementation in content",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Returns true broker positions to confirm zero unauthorized open contracts on Dhan; dashboard conflated paper book with broker positions.",
            "Evidence": "content/app/dhan_account_router.py line 131 calls _raw_get_positions()."
        },
        {
            "Feature Name": "Paper Order Execution Core",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/cloud_paper_engine.py & order_management.py",
            "Destination File": "dashboard/backend/cloud_paper_engine.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard has CloudPaperEngine with realistic simulated fills, slippage models, STT/exchange fee calculations, and atomic state sync.",
            "Evidence": "dashboard/backend/cloud_paper_engine.py CloudPaperEngine class (729 lines)."
        },
        {
            "Feature Name": "OpenAlgo Protocol Order Interception",
            "Classification": "Better implementation in content",
            "Source File": "content/app/app.py:6726",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "content/app",
            "Reason": "Content provides complete OpenAlgo webhook endpoint compatibility (/api/v1/placeorder) while strictly intercepting real order calls.",
            "Evidence": "content/app/app.py lines 6726-6756 intercepts OpenAlgo JSON and prevents live execution."
        },
        {
            "Feature Name": "Position Reconciliation Service",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/position_reconciliation.py",
            "Destination File": "dashboard/backend/position_reconciliation.py",
            "Winner": "dashboard/backend",
            "Reason": "Automatically audits internal paper positions against broker positions and detects phantom trades or drift.",
            "Evidence": "dashboard/backend/position_reconciliation.py reconcile_positions() method."
        },
        {
            "Feature Name": "Broker Truth Validator & Zero-Order Proof",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/broker_truth_validator.py",
            "Destination File": "dashboard/backend/broker_truth_validator.py",
            "Winner": "dashboard/backend",
            "Reason": "Independently interrogates Dhan order book to prove zero order modifications/cancellations were submitted, satisfying AGENTS.md mandate.",
            "Evidence": "dashboard/backend/broker_truth_validator.py build_broker_truth_report()."
        },
        {
            "Feature Name": "Unified Portfolio Truth Valuation",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/portfolio_truth_service.py",
            "Destination File": "dashboard/backend/portfolio_truth_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Computes institutional mark-to-market valuation, cash equivalents, and total margin requirement across multi-asset portfolios.",
            "Evidence": "dashboard/backend/portfolio_truth_service.py calculate_portfolio_truth()."
        },
        {
            "Feature Name": "Broker Alert Flapping Deduplicator",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/broker_alert_deduplicator.py",
            "Destination File": "dashboard/backend/broker_alert_deduplicator.py",
            "Winner": "dashboard/backend",
            "Reason": "Prevents alert fatigue by deduplicating transient margin or connection error notifications with sliding window suppression.",
            "Evidence": "dashboard/backend/broker_alert_deduplicator.py BrokerAlertDeduplicator class."
        },
        {
            "Feature Name": "Emergency Square-Off & Kill Switch",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/app.py & profit_governor.py",
            "Destination File": "dashboard/backend/profit_governor.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard cancels open paper orders, calculates exit slippage, commits proof hashes, and permanently latches kill switch; content does simple flag.",
            "Evidence": "dashboard/backend/app.py line 11258 vs content/app/app.py line 6966."
        },
        {
            "Feature Name": "Trade Logging & Trade Journaling",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/trade_logger.py & trade_journal.py",
            "Destination File": "dashboard/backend/trade_journal.py",
            "Winner": "dashboard/backend",
            "Reason": "Structured SQLite trade logging with entry/exit tags, strategy attribution, R-multiple outcomes, and post-trade analytics.",
            "Evidence": "dashboard/backend/trade_logger.py & trade_journal.py."
        },
        {
            "Feature Name": "Broker Order Status Poller",
            "Classification": "Merge required",
            "Source File": "content/app/dhan_account_router.py & dashboard/backend/routers/broker.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "Merge required",
            "Reason": "Merge content's real core Dhan client orders endpoint with dashboard's broker router order lifecycle management.",
            "Evidence": "content/app/dhan_account_router.py get_dhan_orders() vs dashboard/backend/routers/broker.py."
        }
    ]

    # ==========================================
    # 3. DHAN_FEATURES
    # ==========================================
    dhan_features_data = [
        {
            "Feature Name": "Dhan Credential Prober & JWT Claims Decoder",
            "Classification": "Present in content only",
            "Source File": "content/app/probe_dhan_credentials.py",
            "Destination File": "dashboard/backend/broker/dhan_auth.py",
            "Winner": "content/app",
            "Reason": "Decodes JWT base64 payload to extract token expiry timestamp without printing or leaking secrets to logs.",
            "Evidence": "content/app/probe_dhan_credentials.py lines 22-45 parses token claims."
        },
        {
            "Feature Name": "Dhan Read-Only Client Integration",
            "Classification": "Better implementation in content",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Seamlessly imports and wraps core.brokers.dhan.dhan_readonly functions; dashboard broker router has non-functional stubs.",
            "Evidence": "content/app/dhan_account_router.py imports core.brokers.dhan.dhan_readonly."
        },
        {
            "Feature Name": "Dhan Real-Time Marketfeed Quote API",
            "Classification": "Present in content only",
            "Source File": "content/app/verified_market.py",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "content/app",
            "Reason": "Queries live quotes from https://api.dhan.co/v2/marketfeed/quote with client/token authentication, strictly for reading market data.",
            "Evidence": "content/app/verified_market.py MARKET_URL = 'https://api.dhan.co/v2/marketfeed/quote'."
        },
        {
            "Feature Name": "Dhan Instrument Master Ingestion Pipeline",
            "Classification": "Merge required",
            "Source File": "content/app/fetch_dhan_master.py",
            "Destination File": "core/brokers/dhan/fetch_master.py",
            "Winner": "Merge required",
            "Reason": "Content downloads 35MB detailed CSV from Dhan CDN; dashboard uses JSON master. Needs unified cached ingestion into storage/.",
            "Evidence": "content/app/fetch_dhan_master.py downloads https://images.dhan.co/api-data/api-scrip-master-detailed.csv."
        },
        {
            "Feature Name": "Dhan Instrument Master Audit Tool",
            "Classification": "Present in content only",
            "Source File": "content/app/verified_sources/audit_master_ids.py",
            "Destination File": "tools/audit_dhan_master.py",
            "Winner": "content/app",
            "Reason": "Fast script counting segments (NSE, BSE, MCX) and verifying target index/equity security IDs in Dhan master.",
            "Evidence": "content/app/verified_sources/audit_master_ids.py counts EXCH_ID and SEGMENT rows."
        },
        {
            "Feature Name": "Dhan Full Market Discovery API",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4042",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Enumerates all discoverable tradable contracts across cash, futures, and options; needs to be exposed via dashboard router.",
            "Evidence": "content/app/app.py lines 4042-4110."
        },
        {
            "Feature Name": "Dhan Options Chain Subscription Manager",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:4114",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Maps dynamic option strikes to Dhan security IDs for active quote polling. Essential for live options chain.",
            "Evidence": "content/app/app.py lines 4114-4160."
        },
        {
            "Feature Name": "Dhan Live Connectivity & Latency Probe",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:2222",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "Measures ping time and HTTP response codes to Dhan API gateways, providing clear feedback on connection health.",
            "Evidence": "content/app/app.py lines 2222-2280."
        },
        {
            "Feature Name": "Dhan Authenticated Spot Price Enrichment",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/gain_rank_spot_enrichment.py",
            "Destination File": "dashboard/backend/gain_rank_spot_enrichment.py",
            "Winner": "dashboard/backend",
            "Reason": "Enriches top gainers with authenticated spot prices, calculating real percentage distance from strike.",
            "Evidence": "dashboard/backend/gain_rank_spot_enrichment.py enrich_gain_rank_rows_with_authenticated_spots()."
        },
        {
            "Feature Name": "Dhan IST Market Session Validator",
            "Classification": "Present in content only",
            "Source File": "content/app/verified_market.py:32",
            "Destination File": "dashboard/backend/gain_rank_spot_enrichment.py",
            "Winner": "content/app",
            "Reason": "Strictly validates Asia/Kolkata timezone, weekday trading days, and 09:15 to 15:30 IST session windows to avoid false stale ticks.",
            "Evidence": "content/app/verified_market.py _session() function."
        },
        {
            "Feature Name": "Dhan Quote Rate Limiter & Concurrency Lock",
            "Classification": "Present in content only",
            "Source File": "content/app/verified_market.py:28",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "content/app",
            "Reason": "Uses threading.Lock and 1-second TTL memory cache to guarantee Dhan API rate limits (10 req/sec) are never exceeded.",
            "Evidence": "content/app/verified_market.py _mutex = threading.Lock() and _cache dictionary."
        },
        {
            "Feature Name": "Dhan Auth Stub Module",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/broker/dhan_auth.py",
            "Destination File": "dashboard/backend/broker/dhan_auth.py",
            "Winner": "Merge required",
            "Reason": "Current file is an empty 3-line stub; should be replaced with Dhan JWT validator and auth token management from content.",
            "Evidence": "dashboard/backend/broker/dhan_auth.py contains 3 lines with pass."
        }
    ]

    # ==========================================
    # 4. ML_FEATURES
    # ==========================================
    ml_features_data = [
        {
            "Feature Name": "ML Intelligence Service & Pipeline",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/ml_intelligence_service.py",
            "Destination File": "dashboard/backend/ml_intelligence_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Production ML inference pipeline evaluating intraday momentum, volume breakout, and mean-reversion signals.",
            "Evidence": "dashboard/backend/ml_intelligence_service.py MLIntelligenceService class."
        },
        {
            "Feature Name": "ML Performance Predictor Model",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/performance_predictor.py",
            "Destination File": "dashboard/backend/performance_predictor.py",
            "Winner": "dashboard/backend",
            "Reason": "Generates forward price distributions and expected values using trained tabular model weights.",
            "Evidence": "dashboard/backend/performance_predictor.py PerformancePredictor class."
        },
        {
            "Feature Name": "Directional Accuracy Trend Service",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/accuracy_trend_service.py",
            "Destination File": "dashboard/backend/accuracy_trend_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Tracks rolling directional hit rate over 1h, 4h, 1d, and 7d horizons with binomial confidence intervals.",
            "Evidence": "dashboard/backend/accuracy_trend_service.py AccuracyTrendService class."
        },
        {
            "Feature Name": "Black-Scholes Greeks Calculation Engine",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/greeks_calculator.py",
            "Destination File": "dashboard/backend/greeks_calculator.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard has modular, robust greeks_calculator.py calculating IV, Delta, Gamma, Vega, and Theta; content uses inline math in monolithic app.py.",
            "Evidence": "dashboard/backend/greeks_calculator.py vs content/app/app.py _calc_bs_greeks()."
        },
        {
            "Feature Name": "Implied Volatility Surface & Volatility Smile",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:1080",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "dashboard/backend",
            "Reason": "Calculates volatility smile across strike deltas to identify mispriced out-of-the-money options.",
            "Evidence": "dashboard/backend/app.py get_volatility_smile() endpoint."
        },
        {
            "Feature Name": "Genesis ML Health & Drift Telemetry",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/genesis_ml_health.py",
            "Destination File": "dashboard/backend/genesis_ml_health.py",
            "Winner": "dashboard/backend",
            "Reason": "Monitors feature distribution drift, inference latency spikes, and model degradation in real time.",
            "Evidence": "dashboard/backend/genesis_ml_health.py GenesisMLHealth class."
        },
        {
            "Feature Name": "ML Evidence Store & Proof Logger",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/ml_evidence_store.py",
            "Destination File": "dashboard/backend/ml_evidence_store.py",
            "Winner": "dashboard/backend",
            "Reason": "Persists timestamped predictions prior to outcome realization, enabling tamper-evident forward prediction audits.",
            "Evidence": "dashboard/backend/ml_evidence_store.py MLEvidenceStore class."
        },
        {
            "Feature Name": "Forecast vs Actual Outcome Verification",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:3654 & dashboard/backend/paper_prediction_outcome_audit.py",
            "Destination File": "dashboard/backend/paper_prediction_outcome_audit.py",
            "Winner": "Merge required",
            "Reason": "Content provides clear response schema for Layer 5 verification; dashboard has outcome matching logic. Merge required.",
            "Evidence": "content/app/app.py ml_forecast_vs_actual() vs dashboard/backend/paper_prediction_outcome_audit.py."
        },
        {
            "Feature Name": "ML Prediction Audit API",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/routers/ml.py",
            "Destination File": "dashboard/backend/routers/ml.py",
            "Winner": "dashboard/backend",
            "Reason": "Dashboard queries persisted prediction records from Firestore/SQLite; content serves ephemeral in-memory logs.",
            "Evidence": "dashboard/backend/routers/ml.py lines 600-650."
        },
        {
            "Feature Name": "Benchmark Alpha Comparison",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/backtesting.py",
            "Destination File": "dashboard/backend/backtesting.py",
            "Winner": "dashboard/backend",
            "Reason": "Computes annualized Sharpe ratio, Information Ratio, and Jensen's Alpha against Nifty 50; content uses hardcoded benchmark formula.",
            "Evidence": "dashboard/backend/backtesting.py calculate_metrics() vs content/app/app.py ml_benchmark_comparison()."
        },
        {
            "Feature Name": "Feature Importance & ROC Analysis",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/routers/ml.py",
            "Destination File": "dashboard/backend/routers/ml.py",
            "Winner": "dashboard/backend",
            "Reason": "Exposes model interpretability endpoints (SHAP feature rankings, ROC curves, confusion matrix).",
            "Evidence": "dashboard/backend/routers/ml.py endpoints /api/ml/feature_importance and /api/ml/roc_curve."
        },
        {
            "Feature Name": "Multibagger Pattern Scanner",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/multibagger_service.py",
            "Destination File": "dashboard/backend/multibagger_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Scans option contracts with asymmetric risk-reward, surging open interest, and low IV for exponential moves.",
            "Evidence": "dashboard/backend/multibagger_service.py MultibaggerService class."
        },
        {
            "Feature Name": "Synthetic Random Market Data Generator",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/synthetic_data_generator.py",
            "Destination File": "dashboard/backend/synthetic_data_generator.py",
            "Winner": "Safe removal",
            "Reason": "Generates artificial prices violating real-data compliance. Must be removed from production build.",
            "Evidence": "dashboard/backend/synthetic_data_generator.py generates synthetic random walks."
        }
    ]

    # ==========================================
    # 5. VALIDATION_FEATURES
    # ==========================================
    val_features_data = [
        {
            "Feature Name": "Broker Truth Validator & Zero-Order Proof",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/broker_truth_validator.py",
            "Destination File": "dashboard/backend/broker_truth_validator.py",
            "Winner": "dashboard/backend",
            "Reason": "Production validator proving zero live orders were placed, checking order book state, and verifying account safety.",
            "Evidence": "dashboard/backend/broker_truth_validator.py build_broker_truth_report()."
        },
        {
            "Feature Name": "Live Profit Validator & Slippage Auditor",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/live_profit_validator.py",
            "Destination File": "dashboard/backend/live_profit_validator.py",
            "Winner": "dashboard/backend",
            "Reason": "Multi-validates paper P&L against true market quotes, preventing phantom paper profits and enforcing slippage costs.",
            "Evidence": "dashboard/backend/live_profit_validator.py LiveProfitValidator class."
        },
        {
            "Feature Name": "Multi-Validation Audit Engine",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/multi_validation_audit.py",
            "Destination File": "dashboard/backend/multi_validation_audit.py",
            "Winner": "dashboard/backend",
            "Reason": "12-layer verification engine validating spot prices, contract F&O eligibility, option visibility, and execution rules.",
            "Evidence": "dashboard/backend/multi_validation_audit.py MultiValidationAuditor class."
        },
        {
            "Feature Name": "F&O Eligibility Contract Filter",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/fo_eligibility_filter.py",
            "Destination File": "dashboard/backend/fo_eligibility_filter.py",
            "Winner": "dashboard/backend",
            "Reason": "Maintains authoritative set of approved NSE F&O underlyings, preventing trades on illiquid or ineligible securities.",
            "Evidence": "dashboard/backend/fo_eligibility_filter.py FOEligibilityFilter class."
        },
        {
            "Feature Name": "Option Strike Visibility & Liquidity Auditor",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/option_strike_visibility_audit.py",
            "Destination File": "dashboard/backend/option_strike_visibility_audit.py",
            "Winner": "dashboard/backend",
            "Reason": "Audits entire strike range for gaps, ensuring all active strikes have bids, asks, and valid pricing data.",
            "Evidence": "dashboard/backend/option_strike_visibility_audit.py OptionVisibilityAuditor class."
        },
        {
            "Feature Name": "Paper Ledger Integrity Guard",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/paper_ledger_guard.py",
            "Destination File": "dashboard/backend/paper_ledger_guard.py",
            "Winner": "dashboard/backend",
            "Reason": "Guarantees monotonic sequence numbers and cryptographic integrity of all paper trade ledger records.",
            "Evidence": "dashboard/backend/paper_ledger_guard.py PaperLedgerGuard class."
        },
        {
            "Feature Name": "Paper Feed Admission Gate",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/paper_feed_admission.py",
            "Destination File": "dashboard/backend/paper_feed_admission.py",
            "Winner": "dashboard/backend",
            "Reason": "Rejects stale ticks, inverted bid-ask spreads, and zero-volume quotes before feeding trading models.",
            "Evidence": "dashboard/backend/paper_feed_admission.py PaperFeedAdmissionGate class."
        },
        {
            "Feature Name": "Signal Plan Pre-Trade Risk Audit",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/signal_plan_audit.py",
            "Destination File": "dashboard/backend/signal_plan_audit.py",
            "Winner": "dashboard/backend",
            "Reason": "Pre-flight audit checking position sizing, maximum margin, portfolio concentration, and stop-loss rules.",
            "Evidence": "dashboard/backend/signal_plan_audit.py SignalPlanAudit class."
        },
        {
            "Feature Name": "Continuous Closure & Stop-Loss Governor",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/continuous_closure_service.py",
            "Destination File": "dashboard/backend/continuous_closure_service.py",
            "Winner": "dashboard/backend",
            "Reason": "High-frequency background worker enforcing automated exit rules, profit targets, and stop losses.",
            "Evidence": "dashboard/backend/continuous_closure_service.py ContinuousClosureService class."
        },
        {
            "Feature Name": "Cryptographic Proof Ledger Service",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/proof_ledger_service.py",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Persists SHA-256 state chain transitions in SQLite/Firestore with receipt retrieval; content has ephemeral in-memory chain.",
            "Evidence": "dashboard/backend/proof_ledger_service.py ProofLedgerService class."
        },
        {
            "Feature Name": "Truth Patch V1 String Replacer",
            "Classification": "Safe removal",
            "Source File": "content/app/patch_truth.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "One-off script performing brittle text replacement on app.py; replaced by proper architectural enforcement in code.",
            "Evidence": "content/app/patch_truth.py modifies code strings with replace()."
        },
        {
            "Feature Name": "Verified Gate V2 Code Injector",
            "Classification": "Safe removal",
            "Source File": "content/app/install_verified_gate.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "One-off script injecting code into app.py and HTML templates. Should be removed in favor of clean modular routers.",
            "Evidence": "content/app/install_verified_gate.py string injection script."
        },
        {
            "Feature Name": "Option Chain Coverage Validator",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:1250",
            "Destination File": "dashboard/backend/option_strike_visibility_audit.py",
            "Winner": "Merge required",
            "Reason": "Validates that option chain cache covers required symbols and strikes; merge into strike visibility audit.",
            "Evidence": "content/app/app.py _chain_cache_coverage() function."
        },
        {
            "Feature Name": "Positive LTP Price Sanity Enforcement",
            "Classification": "Present in content only",
            "Source File": "content/app/app.py:1270",
            "Destination File": "dashboard/backend/paper_feed_admission.py",
            "Winner": "Merge required",
            "Reason": "Ensures no negative or zero LTP prices enter calculations; merge into paper feed admission gate.",
            "Evidence": "content/app/app.py _positive_ltp() function."
        }
    ]

    # ==========================================
    # 6. SECURITY_FEATURES
    # ==========================================
    sec_features_data = [
        {
            "Feature Name": "Memory Guard Middleware & Defensive GC",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/middleware/memory_guard.py",
            "Destination File": "dashboard/backend/middleware/memory_guard.py",
            "Winner": "dashboard/backend",
            "Reason": "Actively monitors process RSS memory, triggers defensive garbage collection, and rejects heavy requests if RSS exceeds thresholds.",
            "Evidence": "dashboard/backend/middleware/memory_guard.py memory_guard_middleware()."
        },
        {
            "Feature Name": "Security Policy Engine & Paper Trading Locks",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/security_policy.py",
            "Destination File": "dashboard/backend/security_policy.py",
            "Winner": "dashboard/backend",
            "Reason": "Enforces PAPER_MODE=1, LIVE_ORDER_AUTHORITY=0, and LIVE_TRADING_ENABLED=0 with strict request inspection.",
            "Evidence": "dashboard/backend/security_policy.py evaluate_request() and SecurityDecision."
        },
        {
            "Feature Name": "Secure App Wrapper Pipeline",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/secure_app.py",
            "Destination File": "dashboard/backend/secure_app.py",
            "Winner": "dashboard/backend",
            "Reason": "Wraps FastAPI with rate limiting, host header validation, security headers (CSP, HSTS, X-Frame-Options), and input sanitization.",
            "Evidence": "dashboard/backend/secure_app.py."
        },
        {
            "Feature Name": "Safe Environment Enforcer Script",
            "Classification": "Present in content only",
            "Source File": "content/app/configure_safe_env.py",
            "Destination File": "scripts/configure_safe_env.py",
            "Winner": "content/app",
            "Reason": "Idempotent script checking and enforcing paper/analyze mode flags across .env and secret files without leaking keys.",
            "Evidence": "content/app/configure_safe_env.py lines 1-73."
        },
        {
            "Feature Name": "OpenAlgo Order Placement Interceptor",
            "Classification": "Better implementation in content",
            "Source File": "content/app/app.py:6726",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "content/app",
            "Reason": "Strictly intercepts OpenAlgo order requests, returns success response to caller, but routes order exclusively into paper core.",
            "Evidence": "content/app/app.py lines 6726-6756."
        },
        {
            "Feature Name": "Credential Probing & Token Redaction",
            "Classification": "Present in content only",
            "Source File": "content/app/probe_dhan_credentials.py",
            "Destination File": "dashboard/backend/broker/dhan_auth.py",
            "Winner": "content/app",
            "Reason": "Inspects token expiration while explicitly redacting all private tokens, secrets, and client IDs from output.",
            "Evidence": "content/app/probe_dhan_credentials.py prints 'PRESENT' or 'MISSING' without secret values."
        },
        {
            "Feature Name": "CORS & Allowed Origins Configuration",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/app.py:580",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Configures granular CORS policies with allowed origins, credentials support, and explicit HTTP methods.",
            "Evidence": "dashboard/backend/app.py lines 580-600 CORSMiddleware setup."
        },
        {
            "Feature Name": "Session Authentication & Cookie Protection",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/app.py:612",
            "Destination File": "dashboard/backend/app.py",
            "Winner": "dashboard/backend",
            "Reason": "Signs session cookies with secure HMAC keys, supporting session invalidation and role-based access.",
            "Evidence": "dashboard/backend/app.py lines 612-660."
        },
        {
            "Feature Name": "Audit Middleware & Request Fingerprinting",
            "Classification": "Better implementation in dashboard",
            "Source File": "dashboard/backend/proof_ledger_service.py",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Cryptographically hashes all state transitions and critical API mutations into durable tamper-evident proof ledger.",
            "Evidence": "dashboard/backend/proof_ledger_service.py record_proof()."
        },
        {
            "Feature Name": "Automated Profit Governor & Drawdown Lock",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/profit_governor.py",
            "Destination File": "dashboard/backend/profit_governor.py",
            "Winner": "dashboard/backend",
            "Reason": "Enforces strict loss limits; halts all automated paper trading if drawdown exceeds max risk allowance.",
            "Evidence": "dashboard/backend/profit_governor.py ProfitGovernor class."
        },
        {
            "Feature Name": "Auto Gates Anomaly Detector",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/auto_gates_service.py",
            "Destination File": "dashboard/backend/auto_gates_service.py",
            "Winner": "dashboard/backend",
            "Reason": "Trips circuit breakers if market spread widens excessively, feeds drop, or order execution errors spike.",
            "Evidence": "dashboard/backend/auto_gates_service.py AutoGatesService class."
        },
        {
            "Feature Name": "Risk Management Capital Exposure Limit",
            "Classification": "Present in dashboard only",
            "Source File": "dashboard/backend/risk_management.py",
            "Destination File": "dashboard/backend/risk_management.py",
            "Winner": "dashboard/backend",
            "Reason": "Limits max capital per trade (<= 2%) and total portfolio exposure (<= 20%), preventing catastrophic over-allocation.",
            "Evidence": "dashboard/backend/risk_management.py check_risk_limits()."
        },
        {
            "Feature Name": "Verified Gate V2 Unverified Feed Blocker",
            "Classification": "Better implementation in content",
            "Source File": "content/app/verified_market.py",
            "Destination File": "dashboard/backend/gain_rank_spot_enrichment.py",
            "Winner": "content/app",
            "Reason": "Explicitly marks unverified quotes and rejects simulated feeds from masquerading as live Dhan data.",
            "Evidence": "content/app/verified_market.py sets 'exchange_quotes_verified': True/False."
        }
    ]

    # ==========================================
    # 7. MERGE_REQUIRED
    # ==========================================
    merge_data = [
        {
            "Feature Name": "Dhan Real-Time Marketfeed Quote Integration",
            "Classification": "Merge required",
            "Source File": "content/app/verified_market.py",
            "Destination File": "dashboard/backend/routers/chain.py & gain_rank_spot_enrichment.py",
            "Winner": "content/app",
            "Reason": "content/app/verified_market.py has the only working, authenticated Dhan /v2/marketfeed/quote implementation with rate limiting and IST checks. Must be merged into dashboard to replace mock spots.",
            "Evidence": "content/app/verified_market.py lines 294-309 vs dashboard/backend/gain_rank_spot_enrichment.py."
        },
        {
            "Feature Name": "Dhan Read-Only Account Router Integration",
            "Classification": "Merge required",
            "Source File": "content/app/dhan_account_router.py",
            "Destination File": "dashboard/backend/routers/broker.py",
            "Winner": "content/app",
            "Reason": "content/app/dhan_account_router.py connects to core.brokers.dhan.dhan_readonly for funds, holdings, profile, and orders. Must replace empty stubs in dashboard routers/broker.py.",
            "Evidence": "content/app/dhan_account_router.py lines 77-170 vs dashboard/backend/routers/broker.py lines 110-150."
        },
        {
            "Feature Name": "Dhan Credential Prober & JWT Verification",
            "Classification": "Merge required",
            "Source File": "content/app/probe_dhan_credentials.py",
            "Destination File": "dashboard/backend/broker/dhan_auth.py",
            "Winner": "content/app",
            "Reason": "content/app/probe_dhan_credentials.py decodes JWT expiry without printing secrets. Must be integrated into dashboard's empty dhan_auth.py stub.",
            "Evidence": "content/app/probe_dhan_credentials.py vs dashboard/backend/broker/dhan_auth.py (3 lines)."
        },
        {
            "Feature Name": "Dhan Instrument Master Ingestion Pipeline",
            "Classification": "Merge required",
            "Source File": "content/app/fetch_dhan_master.py & verified_sources/audit_master_ids.py",
            "Destination File": "core/brokers/dhan/fetch_master.py",
            "Winner": "Merge required",
            "Reason": "content downloads the 35MB detailed CSV directly from Dhan CDN, while dashboard expects JSON. Unify into a single scheduled ingestion pipeline in core/.",
            "Evidence": "content/app/fetch_dhan_master.py vs storage/instruments/OpenAPIScripMaster.json."
        },
        {
            "Feature Name": "OpenAlgo Protocol Gateway with Zero-Order Lock",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:6726",
            "Destination File": "dashboard/backend/routers/trading.py",
            "Winner": "content/app",
            "Reason": "content has full OpenAlgo-compatible webhook (/api/v1/placeorder) with paper lock enforcement. Must be added to dashboard/backend/routers/trading.py.",
            "Evidence": "content/app/app.py lines 6726-6756."
        },
        {
            "Feature Name": "Cryptographic Proof Hash Chain & Provenance API",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:2498 & 6190",
            "Destination File": "dashboard/backend/proof_ledger_service.py",
            "Winner": "Merge required",
            "Reason": "content provides instant block validation (/api/hash-chain, /api/data/provenance); dashboard has SQLite proof ledger. Merge to provide verified cloud hash chain endpoints.",
            "Evidence": "content/app/app.py lines 2498, 6190 vs dashboard/backend/proof_ledger_service.py."
        },
        {
            "Feature Name": "Telegram Alert Dispatch & Outbox Management",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:6386-6550",
            "Destination File": "dashboard/backend/alerts_system.py",
            "Winner": "Merge required",
            "Reason": "content implements telegram status, outbox tracking, and test alerts; dashboard has alerts_system.py. Unify telegram dispatching without token leakage.",
            "Evidence": "content/app/app.py lines 6386-6550 & reports/telegram_outbox.jsonl vs dashboard/backend/alerts_system.py."
        },
        {
            "Feature Name": "Route Health & Millisecond Latency Telemetry",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:2418",
            "Destination File": "dashboard/backend/scanner_telemetry.py",
            "Winner": "content/app",
            "Reason": "content measures rolling p95 and per-route latency across all registered FastAPI routes. Must be integrated into dashboard's telemetry module.",
            "Evidence": "content/app/app.py lines 2418-2495."
        },
        {
            "Feature Name": "Market Breadth & Sectoral Coverage Metrics",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:2037 & 2101",
            "Destination File": "dashboard/backend/routers/chain.py",
            "Winner": "Merge required",
            "Reason": "Institutional endpoints for advances/declines and 14 sector performance. Currently mock in content; must be wired to dashboard live Dhan feed.",
            "Evidence": "content/app/app.py lines 2037, 2101."
        },
        {
            "Feature Name": "Forecast vs Actual Prediction Tracking Engine",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:3654",
            "Destination File": "dashboard/backend/paper_prediction_outcome_audit.py & routers/ml.py",
            "Winner": "Merge required",
            "Reason": "content provides the exact response schema for Layer 5 verification (matured predictions vs actuals); dashboard has matching algorithm. Merge into ml router.",
            "Evidence": "content/app/app.py lines 3654-3750 vs dashboard/backend/paper_prediction_outcome_audit.py."
        },
        {
            "Feature Name": "Institutional 6-Pillar Telemetry Schema",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:1-45",
            "Destination File": "dashboard/backend/standardize_responses.py",
            "Winner": "Merge required",
            "Reason": "content defines the standardized 6-pillar envelope (coverage, provenance, options, paper, ML, operational). Standardize dashboard responses with this envelope.",
            "Evidence": "content/app/app.py header schema & make_envelope() function."
        },
        {
            "Feature Name": "Option Chain Coverage & Positive LTP Validator",
            "Classification": "Merge required",
            "Source File": "content/app/app.py:1250-1280",
            "Destination File": "dashboard/backend/option_strike_visibility_audit.py",
            "Winner": "Merge required",
            "Reason": "content contains quick validation helpers (_chain_cache_coverage, _positive_ltp) that should be incorporated into dashboard strike audit.",
            "Evidence": "content/app/app.py lines 1250-1280."
        }
    ]

    # ==========================================
    # 8. SAFE_REMOVE
    # ==========================================
    safe_remove_data = [
        {
            "Feature Name": "HTML Template Backup File",
            "Classification": "Safe removal",
            "Source File": "content/app/templates/premium.html.bak",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Redundant, unmaintained 38KB backup of HTML template. Safe to delete.",
            "Evidence": "File exists at content/app/templates/premium.html.bak (38,156 bytes)."
        },
        {
            "Feature Name": "Legacy Truth Backups Snapshot (Nov 2)",
            "Classification": "Safe removal",
            "Source File": "content/app/truth_backups/20261102T162014Z/app.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Obsolete snapshot from Nov 2 with outdated mock routes and test code. Safe to delete.",
            "Evidence": "File exists at content/app/truth_backups/20261102T162014Z/app.py (47,641 bytes)."
        },
        {
            "Feature Name": "Legacy Truth Backups HTML Snapshot",
            "Classification": "Safe removal",
            "Source File": "content/app/truth_backups/20261102T162014Z/premium.html",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Obsolete snapshot from Nov 2. Safe to delete.",
            "Evidence": "File exists at content/app/truth_backups/20261102T162014Z/premium.html (30,953 bytes)."
        },
        {
            "Feature Name": "Verified Gate Backup Snapshot app.py",
            "Classification": "Safe removal",
            "Source File": "content/app/truth_backups/verified_gate_20261102T165613Z/app.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Temporary backup generated during install_verified_gate run on Nov 2. Safe to delete.",
            "Evidence": "File exists at content/app/truth_backups/verified_gate_20261102T165613Z/app.py (50,847 bytes)."
        },
        {
            "Feature Name": "Verified Gate Backup Snapshot premium.html",
            "Classification": "Safe removal",
            "Source File": "content/app/truth_backups/verified_gate_20261102T165613Z/premium.html",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Temporary backup generated during install_verified_gate run on Nov 2. Safe to delete.",
            "Evidence": "File exists at content/app/truth_backups/verified_gate_20261102T165613Z/premium.html (33,576 bytes)."
        },
        {
            "Feature Name": "Uvicorn Detached Log File",
            "Classification": "Safe removal",
            "Source File": "content/app/uvicorn_detached.log",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Runtime execution log left behind from detached background process. Safe to delete.",
            "Evidence": "File exists at content/app/uvicorn_detached.log (10,161 bytes)."
        },
        {
            "Feature Name": "Legacy Backend app.py Backup",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py.bak",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Legacy 480KB monolithic backup file. Superseded by modular backend.",
            "Evidence": "File exists at dashboard/backend/app.py.bak."
        },
        {
            "Feature Name": "Timestamped Backend app.py Backup (Nov 1)",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py.bak_20261101_065834",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Stale backup from Nov 1. Safe to delete.",
            "Evidence": "File exists at dashboard/backend/app.py.bak_20261101_065834."
        },
        {
            "Feature Name": "Market Top Route Backend Backup",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py.bak_market_top_route",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Stale experimental route backup. Safe to delete.",
            "Evidence": "File exists at dashboard/backend/app.py.bak_market_top_route."
        },
        {
            "Feature Name": "Perma-Del Backend Backup 1",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py.bak_perma_del_20261101_074025",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Old pre-deletion backup from Nov 1. Safe to delete.",
            "Evidence": "File exists at dashboard/backend/app.py.bak_perma_del_20261101_074025."
        },
        {
            "Feature Name": "Perma-Del Backend Backup 2",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py.bak_perma_del_20261101_074148",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Old pre-deletion backup from Nov 1. Safe to delete.",
            "Evidence": "File exists at dashboard/backend/app.py.bak_perma_del_20261101_074148."
        },
        {
            "Feature Name": "Temporary Test Artifact File",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/test_temp.txt",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Empty or scratch test artifact left in backend directory. Safe to delete.",
            "Evidence": "File exists at dashboard/backend/test_temp.txt."
        },
        {
            "Feature Name": "Synthetic Market Data Generator",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/synthetic_data_generator.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Generates artificial market feeds that violate real-data compliance. Must be removed from production runtime.",
            "Evidence": "dashboard/backend/synthetic_data_generator.py (351 lines of synthetic random walk logic)."
        },
        {
            "Feature Name": "Synthetic Paper Lifecycle Generator",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/synthetic_paper_lifecycle.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Generates simulated trade lifecycles instead of using true broker feeds. Safe to remove.",
            "Evidence": "dashboard/backend/synthetic_paper_lifecycle.py (65 lines)."
        },
        {
            "Feature Name": "Empty Dhan Auth Stub",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/broker/dhan_auth.py",
            "Destination File": "dashboard/backend/broker/dhan_auth.py (replace)",
            "Winner": "Safe removal",
            "Reason": "Empty 3-line stub file with no functionality; safe to replace with merged implementation from probe_dhan_credentials.py.",
            "Evidence": "dashboard/backend/broker/dhan_auth.py contains pass."
        },
        {
            "Feature Name": "Deprecated MoneyControl Scraper Stub",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/services/moneycontrol_live.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "Fragile web-scraping stub violating broker direct feed policy. Safe to remove in favor of Dhan REST feed.",
            "Evidence": "dashboard/backend/services/moneycontrol_live.py."
        },
        {
            "Feature Name": "Hardcoded Synthetic Option Strikes & Greeks",
            "Classification": "Safe removal",
            "Source File": "content/app/app.py:188",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "STRIKES = list(range(1000, 1505, 5)) and synthetic random walk Greeks in app.py violate real-data compliance. Remove during consolidation.",
            "Evidence": "content/app/app.py lines 188 & 2764."
        },
        {
            "Feature Name": "Brittle Patch Truth String Replacer",
            "Classification": "Safe removal",
            "Source File": "content/app/patch_truth.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "One-off regex text replacer used to patch mock flags into app.py. Not needed in clean architecture.",
            "Evidence": "content/app/patch_truth.py (66 lines)."
        },
        {
            "Feature Name": "Verified Gate Text Injector",
            "Classification": "Safe removal",
            "Source File": "content/app/install_verified_gate.py",
            "Destination File": "None",
            "Winner": "Safe removal",
            "Reason": "One-off script modifying Python code and HTML via string concatenation. Safe to remove.",
            "Evidence": "content/app/install_verified_gate.py (88 lines)."
        },
        {
            "Feature Name": "Shadowed Duplicate Routes in backend/app.py",
            "Classification": "Safe removal",
            "Source File": "dashboard/backend/app.py",
            "Destination File": "dashboard/backend/routers/",
            "Winner": "Safe removal",
            "Reason": "Routes duplicated between app.py and routers/broker.py, chain.py, and ml.py (e.g. /api/accuracy_trend). Consolidate into routers.",
            "Evidence": "dashboard/backend/app.py line 2350 vs routers/ml.py line 691."
        }
    ]

    # Render all 8 sheets
    print("Rendering API_ENDPOINTS...")
    render_sheet("API_ENDPOINTS", api_endpoints_data)
    
    print("Rendering BROKER_FEATURES...")
    render_sheet("BROKER_FEATURES", broker_features_data)
    
    print("Rendering DHAN_FEATURES...")
    render_sheet("DHAN_FEATURES", dhan_features_data)
    
    print("Rendering ML_FEATURES...")
    render_sheet("ML_FEATURES", ml_features_data)
    
    print("Rendering VALIDATION_FEATURES...")
    render_sheet("VALIDATION_FEATURES", val_features_data)
    
    print("Rendering SECURITY_FEATURES...")
    render_sheet("SECURITY_FEATURES", sec_features_data)
    
    print("Rendering MERGE_REQUIRED...")
    render_sheet("MERGE_REQUIRED", merge_data)
    
    print("Rendering SAFE_REMOVE...")
    render_sheet("SAFE_REMOVE", safe_remove_data)

    out_path = r"C:\Genesis_System3_clean\FEATURE_TRUTH_MATRIX.xlsx"
    wb.save(out_path)
    print(f"Successfully saved FEATURE_TRUTH_MATRIX.xlsx to {out_path}!")
    print(f"File size: {os.path.getsize(out_path)} bytes")

if __name__ == '__main__':
    main()
    sys.exit(0)
