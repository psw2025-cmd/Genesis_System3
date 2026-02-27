"""
Live Option Chain Runner - Main entry point
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import pytz
import pandas as pd
import json

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from src.angel.expiry_selector import get_expiry_for_all_indices
from src.angel.live_chain_ws import LiveChainWebSocket
from src.angel.live_chain_rest import LiveChainREST
from src.metrics.iv_solver import solve_implied_volatility
from src.metrics.greeks import calculate_greeks_from_market_price
from src.metrics.oi_buildup import compute_deltas
from src.selector.top_symbol_selector import TopSymbolSelector
from src.selector.strategy_engine import StrategyEngine
from src.storage.sqlite_store import OptionChainStore
from src.output.export_csv import CSVExporter
from src.validation.qc_validator import QCValidator
from src.utils.market_hours import is_market_open, get_market_status
from src.output.metrics_logger import log_cycle_metrics
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker
from src.storage.trade_history import TradeHistoryStore
from core.utils.option_chain_calculations import add_calculated_columns
from core.utils.logger import logger


# Available indices
AVAILABLE_INDICES = [
    {"name": "NIFTY", "exchange": "NFO"},
    {"name": "BANKNIFTY", "exchange": "NFO"},
    {"name": "FINNIFTY", "exchange": "NFO"},
    {"name": "MIDCPNIFTY", "exchange": "NFO"},
    {"name": "SENSEX", "exchange": "BFO"},
]


class LiveChainRunner:
    """
    Main runner for live option chain system.
    """

    def __init__(
        self,
        refresh_interval: int = 5,
        use_websocket: bool = True,
        prefer_weekly: bool = True,
        sim_mode: bool = False,
        ignore_market_hours: bool = False,
        replay_engine=None,
    ):
        """
        Initialize runner.

        Args:
            refresh_interval: Refresh interval in seconds (default: 5)
            use_websocket: Use WebSocket if available (default: True)
            prefer_weekly: Prefer weekly expiries (default: True)
            sim_mode: Simulation mode (default: False)
            ignore_market_hours: Ignore market hours check (default: False)
            replay_engine: Replay engine instance for sim mode
        """
        self.refresh_interval = refresh_interval
        self.use_websocket = use_websocket
        self.prefer_weekly = prefer_weekly
        self.sim_mode = sim_mode
        self.ignore_market_hours = ignore_market_hours
        self.replay_engine = replay_engine

        # Initialize components
        if not sim_mode:
            logger.info("Initializing broker...")
            self.broker = AngelOneBroker(allow_data_only=True)
            logger.info("Initializing components...")
            self.ws_manager = LiveChainWebSocket(self.broker) if use_websocket else None
            self.rest_fallback = LiveChainREST(self.broker)
        else:
            logger.info("SIMULATION MODE: Skipping broker initialization")
            self.broker = None
            self.ws_manager = None
            self.rest_fallback = None

        self.selector = TopSymbolSelector()
        self.strategy_engine = StrategyEngine()
        self.storage = OptionChainStore()
        self.exporter = CSVExporter()
        self.qc_validator = QCValidator(sim_mode=self.sim_mode)

        # Paper trading components
        self.paper_executor = PaperExecutor()
        self.pnl_tracker = PnLTracker()
        self.trade_history_store = TradeHistoryStore()

        # Multi-session handler (optional)
        try:
            from scripts.multi_session_handler import MultiSessionHandler

            self.multi_session_handler = MultiSessionHandler()
        except:
            self.multi_session_handler = None

        # State
        self.expiry_map = {}
        self.previous_snapshots = {}  # For delta calculations
        self.cycle_count = 0
        self.start_time = None
        self._current_scenario = None
        self._total_cycles = None

    def initialize_expiries(self) -> bool:
        """Initialize expiry selection for all indices."""
        if self.sim_mode:
            # In sim mode, use simulated expiries
            for idx in AVAILABLE_INDICES:
                self.expiry_map[idx["name"]] = "24FEB2026"  # Simulated expiry
            logger.info("SIM MODE: Using simulated expiries")
            return True

        logger.info("Selecting expiries for all indices...")
        expiry_results = get_expiry_for_all_indices(AVAILABLE_INDICES, self.prefer_weekly)

        for name, result in expiry_results.items():
            if result["expiry_string"]:
                self.expiry_map[name] = result["expiry_string"]
                logger.info(f"{name}: {result['expiry_string']} ({'weekly' if result['is_weekly'] else 'monthly'})")
            else:
                logger.error(f"{name}: Failed to select expiry - {result['reason']}")
                return False

        return True

    def fetch_data_websocket(self) -> Dict[str, pd.DataFrame]:
        """Fetch data via WebSocket (placeholder - needs full implementation)."""
        # WebSocket implementation would go here
        # For now, fallback to REST
        logger.warning("WebSocket not fully implemented, using REST fallback")
        return self.fetch_data_rest()

    def fetch_data_rest(self) -> Dict[str, pd.DataFrame]:
        """Fetch data via REST API or simulation."""
        if self.sim_mode and self.replay_engine:
            # Simulation mode: use replay engine
            all_data = self.replay_engine.generate_snapshot(
                scenario=self._current_scenario or "RANGE",
                cycle=self.cycle_count,
                total_cycles=self._total_cycles or 120,
                inject_errors=(self._current_scenario == "DATA_ERROR"),
            )

            # Compute deltas
            for name, df in all_data.items():
                if name in self.previous_snapshots:
                    df = compute_deltas(df, self.previous_snapshots[name])
                else:
                    df = compute_deltas(df, None)
                all_data[name] = df
                self.previous_snapshots[name] = df.copy()

            return all_data

        # Real mode: fetch from API
        all_data = {}

        for idx in AVAILABLE_INDICES:
            name = idx["name"]
            exchange = idx["exchange"]
            expiry = self.expiry_map.get(name)

            if not expiry:
                logger.warning(f"No expiry for {name}, skipping")
                print(f"[WARNING] No expiry for {name}, skipping")
                continue

            logger.info(f"Fetching {name} ({exchange}) - expiry: {expiry}")
            print(f"[FETCH] {name} ({exchange}) - expiry: {expiry}")

            try:
                # Add timeout to prevent hanging
                import signal
                import threading

                fetch_result = [None]
                fetch_error = [None]

                def fetch_with_timeout():
                    try:
                        result = self.rest_fallback.fetch_option_chain_batch(name, exchange, expiry)
                        fetch_result[0] = result
                    except Exception as e:
                        fetch_error[0] = e
                        fetch_result[0] = None

                # Start fetch in thread with timeout
                fetch_thread = threading.Thread(target=fetch_with_timeout, daemon=True)
                fetch_thread.start()
                fetch_thread.join(timeout=30)  # 30 second timeout per index

                if fetch_thread.is_alive():
                    # Fetch timed out
                    logger.error(f"Fetch timeout for {name} after 30 seconds")
                    print(f"[ERROR] {name}: Fetch timeout (30s), skipping")
                    all_data[name] = pd.DataFrame()
                    continue

                if fetch_error[0]:
                    logger.error(f"Error fetching {name}: {fetch_error[0]}", exc_info=True)
                    print(f"[ERROR] {name}: {fetch_error[0]}")
                    all_data[name] = pd.DataFrame()
                    continue

                option_chain = fetch_result[0]

                if option_chain:
                    df = pd.DataFrame(option_chain)

                    # Add calculated columns
                    ist = pytz.timezone("Asia/Kolkata")
                    now = datetime.now(ist)
                    fetch_timestamp = now.strftime("%Y-%m-%d %H:%M:%S IST")
                    df = add_calculated_columns(df, fetch_timestamp=fetch_timestamp)

                    # Compute deltas if previous snapshot exists
                    if name in self.previous_snapshots:
                        df = compute_deltas(df, self.previous_snapshots[name])
                    else:
                        df = compute_deltas(df, None)

                    # Calculate IV and Greeks if not available (skip if takes too long)
                    try:
                        if "iv" not in df.columns or df["iv"].isna().all():
                            self._calculate_iv_and_greeks(df)
                    except Exception as e:
                        logger.debug(f"Greeks calculation skipped for {name}: {e}")

                    all_data[name] = df
                    self.previous_snapshots[name] = df.copy()

                    logger.info(f"Fetched {len(df)} options for {name}")
                    print(f"[OK] {name}: {len(df)} contracts fetched")
                else:
                    logger.warning(f"No data for {name}")
                    print(f"[WARNING] {name}: No data returned")
                    all_data[name] = pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}", exc_info=True)
                print(f"[ERROR] {name}: {e}")
                all_data[name] = pd.DataFrame()
                # Continue to next index even if this one fails

        return all_data

    def _calculate_iv_and_greeks(self, df: pd.DataFrame):
        """Calculate IV and Greeks for options missing them."""
        from src.metrics.greeks import calculate_greeks_from_market_price

        for idx, row in df.iterrows():
            if pd.notna(row.get("iv")) and pd.notna(row.get("delta")):
                continue  # Already has Greeks

            if not all(pd.notna([row.get("ltp"), row.get("strike"), row.get("spot_price"), row.get("time_to_expiry")])):
                continue

            try:
                greeks = calculate_greeks_from_market_price(
                    spot=float(row["spot_price"]),
                    strike=float(row["strike"]),
                    time_to_expiry=float(row.get("time_to_expiry", 0.065)),
                    risk_free_rate=0.06,
                    market_price=float(row["ltp"]),
                    option_type=str(row["option_type"]),
                )

                if greeks:
                    df.loc[idx, "iv"] = greeks.get("iv")
                    df.loc[idx, "delta"] = greeks.get("delta")
                    df.loc[idx, "gamma"] = greeks.get("gamma")
                    df.loc[idx, "theta"] = greeks.get("theta")
                    df.loc[idx, "vega"] = greeks.get("vega")
                    df.loc[idx, "rho"] = greeks.get("rho")
            except Exception as e:
                logger.debug(f"Failed to calculate Greeks for {row.get('symbol')}: {e}")

    def run_cycle(self) -> Dict:
        """Run one cycle of data fetch and processing."""
        self.cycle_count += 1
        ist = pytz.timezone("Asia/Kolkata")
        cycle_time = datetime.now(ist)

        logger.info(f"=== CYCLE {self.cycle_count} - {cycle_time.strftime('%H:%M:%S IST')} ===")
        print(f"\n{'='*80}")
        print(f"[CYCLE {self.cycle_count}] {cycle_time.strftime('%H:%M:%S IST')} - Fetching live data...")

        # Fetch data
        # Check WebSocket health: if no data for >30s, fallback to REST
        if self.use_websocket and self.ws_manager:
            if self.ws_manager.is_alive(timeout_seconds=30):
                all_data = self.fetch_data_websocket()
            else:
                logger.warning("WebSocket not alive, falling back to REST")
                self.use_websocket = False
                all_data = self.fetch_data_rest()
        else:
            all_data = self.fetch_data_rest()

        # Exclude SENSEX if data coverage < 70%
        for name, df in list(all_data.items()):
            if name == "SENSEX" and not df.empty:
                required_strikes = 50  # Approximate
                if len(df) < required_strikes * 0.7:
                    logger.warning(f"Excluding {name}: only {len(df)} contracts (< 70% of required)")
                    del all_data[name]

        # QC Validation
        qc_results = self.qc_validator.validate_all(all_data)

        if not qc_results["overall_passed"]:
            logger.warning("QC FAILED - Outputting NO TRADE")
            print(f"[QC] ❌ FAILED - {qc_results.get('reason', 'Unknown reason')}")

            # Still export data and reports even if QC fails
            trade_signal = {"action": "NO TRADE", "reason": "QC failed"}

            # Export outputs even on QC failure
            try:
                # Combine all data
                all_dfs = []
                for name, df in all_data.items():
                    if not df.empty:
                        all_dfs.append(df)

                if all_dfs:
                    combined_df = pd.concat(all_dfs, ignore_index=True)
                    try:
                        output_path = self.exporter.export_chain_raw(combined_df)
                        print(f"[DATA] ✅ Exported {len(combined_df)} contracts to {output_path.name}")
                    except Exception as e:
                        print(f"[DATA] ❌ Export failed: {e}")

                # Export empty rankings
                empty_rankings = pd.DataFrame()
                try:
                    rank_path = self.exporter.export_underlying_rank(empty_rankings)
                    print(f"[RANKINGS] ✅ Exported (empty rankings)")
                except Exception as e:
                    print(f"[RANKINGS] ❌ Export failed: {e}")

                # Export trade signal
                try:
                    signal_path = self.exporter.export_trade_signal(trade_signal)
                    print(f"[SIGNAL] NO TRADE - QC Failed")
                except Exception as e:
                    print(f"[SIGNAL] ❌ Export failed: {e}")

                # Export QC report
                try:
                    qc_path = self.exporter.export_qc_report(qc_results)
                    print(f"[QC] ❌ FAILED - Report exported")
                except Exception as e:
                    print(f"[QC] ❌ Export failed: {e}")
            except Exception as e:
                logger.error(f"Failed to export on QC failure: {e}", exc_info=True)
                print(f"[EXPORT] ❌ Critical error: {e}")

            return {
                "cycle": self.cycle_count,
                "timestamp": cycle_time.isoformat(),
                "qc_passed": False,
                "qc_reasons": qc_results,
                "top_underlying": None,
                "trade_signal": trade_signal,
            }

        # Get spot prices and time to expiry
        spots = {}
        time_to_expiry_map = {}
        for name, df in all_data.items():
            if not df.empty and "spot_price" in df.columns:
                spots[name] = df["spot_price"].iloc[0]
                if "time_to_expiry" in df.columns:
                    time_to_expiry_map[name] = df["time_to_expiry"].iloc[0]
                else:
                    time_to_expiry_map[name] = 0.065  # Default ~24 days

        # Top symbol selection
        top_underlying, rankings_df = self.selector.select_top_underlying(all_data, spots, time_to_expiry_map)

        # Strategy recommendation
        trade_signal = {"action": "NO TRADE", "reason": "No suitable underlying"}

        if top_underlying and top_underlying in all_data:
            df_top = all_data[top_underlying]
            spot = spots.get(top_underlying, 0)
            expected_move = rankings_df[rankings_df["underlying"] == top_underlying]["expected_move"].iloc[0]

            # Analyze sentiment
            pcr = rankings_df[rankings_df["underlying"] == top_underlying]["pcr"].iloc[0]
            delta_pcr = rankings_df[rankings_df["underlying"] == top_underlying]["pcr_delta_weighted"].iloc[0]
            sentiment = self.strategy_engine.analyze_sentiment(df_top, spot, pcr, delta_pcr)

            # Get scores
            signal_strength = rankings_df[rankings_df["underlying"] == top_underlying]["signal_strength"].iloc[0]
            execution_quality = rankings_df[rankings_df["underlying"] == top_underlying]["execution_quality"].iloc[0]

            # Recommend strategy
            trade_signal = self.strategy_engine.recommend_strategy(
                df_top, top_underlying, spot, expected_move, sentiment, execution_quality, signal_strength
            )
            trade_signal["underlying"] = top_underlying

        # Store snapshots
        for idx_info in AVAILABLE_INDICES:
            name = idx_info["name"]
            if name in all_data:
                df = all_data[name]
                if not df.empty:
                    self.storage.save_snapshot(df, name, idx_info["exchange"])

        # Export outputs
        try:
            # Combine all data
            all_dfs = []
            for name, df in all_data.items():
                if not df.empty:
                    all_dfs.append(df)

            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                try:
                    output_path = self.exporter.export_chain_raw(combined_df)
                    print(f"[DATA] ✅ Exported {len(combined_df)} contracts to {output_path.name}")
                    logger.info(f"Exported {len(combined_df)} contracts to chain_raw_live.csv")
                except Exception as e:
                    print(f"[DATA] ❌ Export failed: {e}")
                    logger.error(f"Failed to export chain_raw: {e}", exc_info=True)
            else:
                print(f"[DATA] ⚠️  No data to export (all indices empty or failed)")
                logger.warning("No data to export - all indices empty or failed")

            if not rankings_df.empty:
                try:
                    rank_path = self.exporter.export_underlying_rank(rankings_df)
                    print(f"[RANKINGS] ✅ Exported rankings to {rank_path.name}")
                    logger.info(f"Exported rankings to {rank_path.name}")
                except Exception as e:
                    print(f"[RANKINGS] ❌ Export failed: {e}")
                    logger.error(f"Failed to export rankings: {e}", exc_info=True)
            else:
                print(f"[RANKINGS] ⚠️  No rankings to export")

            try:
                signal_path = self.exporter.export_trade_signal(trade_signal)
                print(
                    f"[SIGNAL] {trade_signal.get('action', 'NO TRADE')} - {trade_signal.get('underlying', 'N/A')} - {trade_signal.get('strategy', 'N/A')}"
                )
                logger.info(f"Exported trade signal: {trade_signal.get('action')}")
            except Exception as e:
                print(f"[SIGNAL] ❌ Export failed: {e}")
                logger.error(f"Failed to export trade signal: {e}", exc_info=True)

            try:
                qc_path = self.exporter.export_qc_report(qc_results)
                qc_status = "✅ PASSED" if qc_results.get("overall_passed") else "❌ FAILED"
                print(f"[QC] {qc_status}")
                logger.info(f"Exported QC report: {qc_status}")
            except Exception as e:
                print(f"[QC] ❌ Export failed: {e}")
                logger.error(f"Failed to export QC report: {e}", exc_info=True)
        except Exception as e:
            print(f"[EXPORT] ❌ Critical export error: {e}")
            logger.error(f"Critical export error: {e}", exc_info=True)

        # Paper Trading Execution
        if qc_results["overall_passed"] and trade_signal.get("action") == "TRADE":
            # Execute paper trade
            if top_underlying and top_underlying in all_data:
                position = self.paper_executor.execute_trade(
                    trade_signal, all_data[top_underlying], cycle_time.isoformat()
                )
                if position:
                    logger.info(
                        f"✅ PAPER TRADE EXECUTED: {position['position_id']} | {position.get('underlying')} {position.get('strike')} {position.get('option_type')} @ Rs {position.get('entry_price', 0):.2f}"
                    )
                    print(
                        f"\n[PAPER TRADE] ✅ {position.get('underlying')} {position.get('strike')} {position.get('option_type')} | Entry: Rs {position.get('entry_price', 0):.2f} | Qty: {position.get('qty', 0)}"
                    )
                    # Save OPEN trade to history immediately
                    open_trade = {
                        "position_id": position["position_id"],
                        "action": "OPEN",
                        "timestamp": cycle_time.isoformat(),
                        "time_ist": position.get("entry_time_ist", ""),
                        "underlying": position["underlying"],
                        "strike": position["strike"],
                        "option_type": position["option_type"],
                        "price": float(position["entry_price"]),
                        "qty": position["qty"],
                        "strategy": position["strategy"],
                    }
                    self.trade_history_store.save_trade(open_trade)

        # Update positions with current prices
        closed_positions = self.paper_executor.update_positions(all_data, cycle_time.isoformat())

        # Save closed trades to history
        for pos in closed_positions:
            # Convert position to trade history format
            trade_record = {
                "position_id": pos.get("position_id", ""),
                "action": "CLOSE",
                "timestamp": pos.get("exit_timestamp", cycle_time.isoformat()),
                "time_ist": pos.get("exit_time_ist", ""),
                "underlying": pos.get("underlying", ""),
                "strike": pos.get("strike", 0),
                "option_type": pos.get("option_type", ""),
                "price": float(pos.get("exit_price", pos.get("current_price", 0))),
                "qty": pos.get("qty", 0),
                "exit_reason": pos.get("exit_reason", ""),
                "realized_pnl": float(pos.get("realized_pnl", 0)),
                "realized_pnl_pct": float(pos.get("realized_pnl_pct", 0)),
                "entry_price": float(pos.get("entry_price", 0)),
                "exit_price": float(pos.get("exit_price", 0)),
            }
            self.trade_history_store.save_trade(trade_record)

        # Update PnL tracking
        positions_summary = self.paper_executor.get_positions_summary()
        pnl_summary = self.pnl_tracker.update(positions_summary, cycle_time.isoformat())

        # Display PnL update
        if pnl_summary.get("total_trades", 0) > 0:
            pnl_val = pnl_summary.get("total_pnl", 0)
            pnl_color = "🟢" if pnl_val >= 0 else "🔴"
            print(
                f"[PnL] {pnl_color} Total: Rs {pnl_val:,.2f} | Trades: {pnl_summary.get('total_trades', 0)} | Win Rate: {pnl_summary.get('win_rate', 0):.1f}% | Open Positions: {len(positions_summary.get('open_positions', []))}"
            )
            logger.info(
                f"PnL Update: Total={pnl_val:.2f}, Trades={pnl_summary.get('total_trades', 0)}, WinRate={pnl_summary.get('win_rate', 0):.1f}%"
            )

        # Save positions and PnL
        self.trade_history_store.save_positions(positions_summary.get("open_positions", []), positions_summary)
        self.trade_history_store.save_pnl(pnl_summary)

        # Update multi-session state (if handler available)
        if self.multi_session_handler:
            try:
                self.multi_session_handler.update_multi_session_state()
            except:
                pass  # Non-critical

        # Log metrics (one-line per cycle)
        total_contracts = sum(len(df) for df in all_data.values() if not df.empty)
        log_cycle_metrics(
            cycle=self.cycle_count,
            timestamp=cycle_time.isoformat(),
            qc_passed=qc_results["overall_passed"],
            top_underlying=top_underlying or "NONE",
            trade_action=trade_signal.get("action", "NO_TRADE"),
            underlying_count=len(all_data),
            contract_count=total_contracts,
        )

        return {
            "cycle": self.cycle_count,
            "timestamp": cycle_time.isoformat(),
            "qc_passed": qc_results["overall_passed"],
            "top_underlying": top_underlying,
            "trade_signal": trade_signal,
            "rankings": rankings_df.to_dict("records") if not rankings_df.empty else [],
            "paper_trading": {
                "open_positions": len(positions_summary.get("open_positions", [])),
                "total_pnl": pnl_summary.get("total_pnl", 0.0),
                "win_rate": pnl_summary.get("win_rate", 0.0),
                "total_trades": pnl_summary.get("total_trades", 0),
            },
        }

    def run(self, duration_minutes: Optional[int] = None, max_cycles: Optional[int] = None, scenario: str = None):
        """
        Run live chain system.

        Args:
            duration_minutes: Run for N minutes (None = infinite)
            max_cycles: Maximum cycles to run (None = infinite)
            scenario: Scenario name for sim mode
        """
        self.start_time = datetime.now()
        self._current_scenario = scenario
        self._total_cycles = (
            max_cycles
            if max_cycles
            else (int(duration_minutes * 60 / self.refresh_interval) if duration_minutes else 120)
        )

        mode_str = "SIMULATION" if self.sim_mode else "LIVE"
        logger.info(f"Starting {mode_str} chain system (refresh: {self.refresh_interval}s)")
        print(f"\n{'='*80}")
        print(f"  STARTING {mode_str} PAPER TRADING SYSTEM")
        print(f"  Refresh Interval: {self.refresh_interval} seconds")
        print(f"  Indices: {', '.join([idx['name'] for idx in AVAILABLE_INDICES])}")
        print(f"{'='*80}\n")

        # Check market hours (unless ignored or sim mode)
        if not self.sim_mode and not self.ignore_market_hours:
            is_open, reason = is_market_open()
            if not is_open:
                logger.warning(f"Market closed: {reason}")
                market_status = get_market_status()

                # Write outputs indicating market closed
                qc_result = {
                    "overall_passed": False,
                    "reason": "MARKET_CLOSED",
                    "market_status": market_status,
                    "underlying_results": {},
                }
                trade_signal = {
                    "action": "NO TRADE",
                    "reason": f"Market closed: {reason}",
                    "market_status": market_status,
                }

                self.exporter.export_qc_report(qc_result)
                self.exporter.export_trade_signal(trade_signal)

                logger.info("Outputs written with MARKET_CLOSED status")
                return []

        # Initialize expiries
        print("[INFO] Initializing expiries for all indices...")
        if not self.initialize_expiries():
            print("[ERROR] Failed to initialize expiries")
            logger.error("Failed to initialize expiries")
            return
        print(f"[OK] Expiries initialized: {len(self.expiry_map)} indices")

        # Connect WebSocket if enabled (not in sim mode) - with timeout
        if not self.sim_mode and self.use_websocket and self.ws_manager:
            print("[INFO] Attempting WebSocket connection (5s timeout)...")
            logger.info("Connecting WebSocket with timeout...")
            try:
                import signal
                import threading

                # Use threading to add timeout
                connection_result = [None]
                connection_error = [None]

                def try_connect():
                    try:
                        result = self.ws_manager.connect()
                        connection_result[0] = result
                    except Exception as e:
                        connection_error[0] = e
                        connection_result[0] = False

                # Start connection in thread
                conn_thread = threading.Thread(target=try_connect, daemon=True)
                conn_thread.start()
                conn_thread.join(timeout=5)  # 5 second timeout

                if conn_thread.is_alive():
                    # Connection timed out
                    print("[WARNING] WebSocket connection timeout, using REST only")
                    logger.warning("WebSocket connection timeout, using REST only")
                    self.use_websocket = False
                elif connection_error[0]:
                    print(f"[WARNING] WebSocket error: {connection_error[0]}, using REST only")
                    logger.warning(f"WebSocket error: {connection_error[0]}, using REST only")
                    self.use_websocket = False
                elif not connection_result[0]:
                    print("[WARNING] WebSocket connection failed, using REST only")
                    logger.warning("WebSocket connection failed, using REST only")
                    self.use_websocket = False
                else:
                    print("[OK] WebSocket connected")
            except Exception as e:
                print(f"[WARNING] WebSocket setup error: {e}, using REST only")
                logger.warning(f"WebSocket setup error: {e}, using REST only")
                self.use_websocket = False
        else:
            print("[INFO] Using REST API for data fetching")

        print("\n[INFO] Starting trading cycles...")
        print("[INFO] Watch for [CYCLE X] messages to see activity\n")

        cycle_results = []

        try:
            while True:
                print(f"[INFO] Starting cycle {self.cycle_count + 1}...")
                # Check duration limit
                if duration_minutes:
                    elapsed = (datetime.now() - self.start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Duration limit reached ({duration_minutes} minutes)")
                        break

                # Check cycle limit
                if max_cycles and self.cycle_count >= max_cycles:
                    logger.info(f"Cycle limit reached ({max_cycles} cycles)")
                    break

                # Run cycle
                try:
                    result = self.run_cycle()
                    cycle_results.append(result)

                    # Show cycle summary
                    if result:
                        pnl_info = result.get("paper_trading", {})
                        if pnl_info:
                            pnl_val = pnl_info.get("total_pnl", 0)
                            pnl_icon = "🟢" if pnl_val >= 0 else "🔴"
                            print(
                                f"[CYCLE {self.cycle_count} SUMMARY] {pnl_icon} PnL: Rs {pnl_val:,.2f} | Trades: {pnl_info.get('total_trades', 0)} | Open: {pnl_info.get('open_positions', 0)}"
                            )
                except Exception as e:
                    logger.error(f"Error in cycle {self.cycle_count + 1}: {e}", exc_info=True)
                    print(f"[ERROR] Cycle {self.cycle_count + 1} failed: {e}")
                    import traceback

                    traceback.print_exc()
                    # Continue to next cycle even if this one failed

                # Wait for next cycle
                # Check market hours again if in live mode
                if not self.sim_mode and not self.ignore_market_hours:
                    is_open, reason = is_market_open()
                    if not is_open:
                        logger.warning(f"Market closed during run: {reason}")
                        market_status = get_market_status()
                        qc_result = {
                            "overall_passed": False,
                            "reason": "MARKET_CLOSED",
                            "market_status": market_status,
                            "underlying_results": {},
                        }
                        trade_signal = {
                            "action": "NO TRADE",
                            "reason": f"Market closed: {reason}",
                            "market_status": market_status,
                        }
                        self.exporter.export_qc_report(qc_result)
                        self.exporter.export_trade_signal(trade_signal)
                        logger.info("Sleeping 60 seconds before rechecking...")
                        time.sleep(60)
                        continue

                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            # Cleanup
            if not self.sim_mode and self.ws_manager:
                self.ws_manager.disconnect()

            # Cleanup old data (only in live mode to preserve sim data)
            if not self.sim_mode:
                self.storage.cleanup_old_data()

            logger.info(f"Completed {self.cycle_count} cycles")

        return cycle_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Live Option Chain System")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds (default: 5)")
    parser.add_argument("--duration", type=int, help="Run for N minutes")
    parser.add_argument("--cycles", type=int, help="Maximum cycles")
    parser.add_argument("--no-websocket", action="store_true", help="Disable WebSocket, use REST only")
    parser.add_argument("--monthly", action="store_true", help="Use monthly expiries instead of weekly")
    parser.add_argument("--sim-mode", action="store_true", help="Simulation mode (use replay engine)")
    parser.add_argument("--ignore-market-hours", action="store_true", help="Ignore market hours check")
    parser.add_argument("--scenario", type=str, help="Scenario for sim mode (TREND_UP, TREND_DOWN, etc.)")

    args = parser.parse_args()

    replay_engine = None
    if args.sim_mode:
        from src.sim.replay_engine import ReplayEngine

        replay_engine = ReplayEngine()

    runner = LiveChainRunner(
        refresh_interval=args.refresh,
        use_websocket=not args.no_websocket,
        prefer_weekly=not args.monthly,
        sim_mode=args.sim_mode,
        ignore_market_hours=args.ignore_market_hours,
        replay_engine=replay_engine,
    )

    results = runner.run(duration_minutes=args.duration, max_cycles=args.cycles, scenario=args.scenario)

    return 0


if __name__ == "__main__":
    sys.exit(main())
