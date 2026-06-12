"""
run_system3.py — LEGACY ANGEL ONE MENU (DISABLED)

System3 is Dhan-only. All menu options in this file target Angel One /
SmartAPI data paths that are disabled. Any menu option that attempts to
use the broker will raise RuntimeError from the disabled shim.

Do not use this script for live operation. Use system3_ultra.py instead,
which routes to the active Dhan/analyzer paths.
"""

import sys
import os

# Ensure project root is in path before any project imports
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# All Angel module imports are guarded — they may fail due to missing optional
# dependencies (sklearn, pyotp, etc.) without affecting the Dhan/main runtime.
try:
    from core.engine.train_angel_models import main as train_angel_models_main
    from core.engine.build_angel_training_dataset import main as build_angel_training_main
    _ANGEL_TRAINING_AVAILABLE = True
except ImportError:
    train_angel_models_main = None
    build_angel_training_main = None
    _ANGEL_TRAINING_AVAILABLE = False

from core.brokers.angel_one.broker import AngelOneBroker  # disabled shim — safe to import

try:
    from core.engine.main_launcher import main as launch_core
    from core.engine.health_check import main as health_main
    from core.engine.test_data_pipeline import main as data_test_main
    from core.engine.test_angelone_api import main as angelone_test_main
    from core.engine.test_angelone_instruments import main as angelone_instr_test_main
    from core.engine.angel_options_watch import main as angel_options_watch_main
    from core.engine.angel_options_watch_loop import (
        main as angel_options_watch_loop_main,
        _build_full_snapshot,
    )
    from core.engine.angel_options_analyze import main as angel_options_analyze_main
    from core.engine import angel_live_ai_signals
    from core.engine.angel_synthetic_backtester import run_backtest as angel_synthetic_backtest_run
    _ANGEL_ENGINE_AVAILABLE = True
except ImportError as _e:
    launch_core = health_main = data_test_main = angelone_test_main = None
    angelone_instr_test_main = angel_options_watch_main = None
    angel_options_watch_loop_main = _build_full_snapshot = None
    angel_options_analyze_main = angel_live_ai_signals = angel_synthetic_backtest_run = None
    _ANGEL_ENGINE_AVAILABLE = False


def show_menu():
    print("\n=== GENESIS SYSTEM 3 ===")
    print("1) Core boot (basic startup)")
    print("2) Health check")
    print("3) Test data pipeline (live + history)")
    print("4) Test Angel One API (login + LTP)")
    print("5) Test Angel One instruments file")
    print("6) Angel One index options watch (single snapshot)")
    print("7) Angel One index options LIVE watch loop (continuous logging)")
    print("8) Analyze Angel One index options log (simple signals)")
    print("9) Build Angel One index options training dataset (features + labels)")
    print("10) Train Angel One index options models")
    print("11) Angel One index options LIVE AI signals (from models)")
    print("12) Angel One index options SYNTHETIC backtest (CONSERVATIVE)")
    print("13) Angel One index options SYNTHETIC backtest (DEV, more trades)")
    print("14) Angel One trade EXECUTOR (DRY RUN, from trade plan)")
    print("15) Angel One DAILY PnL SUMMARY (today)")
    print("16) Angel One INTRADAY PnL MONITOR (active trades)")
    print("17) Angel One DAILY REPORT GENERATOR")
    print("18) Angel One SYSTEM HEALTH CHECK (watchdog)")
    print("19) Angel One AUTO THRESHOLD ADJUSTER (recommendations)")
    print("20) Angel One CONFIDENCE CALIBRATOR")
    print("21) Angel One STRATEGY OPTIMIZER")
    print("22) Angel One ADVANCED FEATURE RANKER")
    print("23) Angel One BLENDED MODEL TRAINER")
    print("24) Angel One MARKET INTELLIGENCE DASHBOARD")
    print("25) Angel One ACTION LAYER VALIDATOR")
    print("26) Angel One MARKET PROFILE ANALYZER")
    print("27) Angel One SAFETY LAYER V2 CHECK")
    print("28) Angel One REAL OUTCOME LOGGER (test)")
    print("29) Angel One SIGNAL VS OUTCOME ANALYZER")
    print("30) Angel One MISFIRE DETECTOR")
    print("31) Angel One REAL THRESHOLD RECOMMENDER")
    print("32) Angel One RISK PROFILE OPTIMIZER")
    print("33) Angel One REAL DATA EXTRACTOR")
    print("34) Angel One BLENDED DATASET BUILDER")
    print("35) Angel One BLENDED MODEL TRAINER (MANUAL)")
    print("36) Angel One DAILY LEARNING REPORT")
    print("37) Angel One ROLLING 7-DAY LEARNING DASHBOARD")
    print("38) Angel One BLENDED MODEL TRAINER V2 (MANUAL - Enhanced)")
    print("39) Angel One ULTRA-MODE PREP LAYER (Status Check)")
    print("40) Angel One DAILY AUTO-REPORTS (Generate All)")
    print("41) Angel One WEEKLY SUMMARY REPORT")
    print("42) Angel One MONDAY MORNING PRE-MARKET DIAGNOSTIC")
    print("43) Angel One REPORT AUTO-SCHEDULER (Status)")
    print("44) Angel One LIVE SNAPSHOT REASONER")
    print("45) Angel One OUTCOME CONFIDENCE CURVE ANALYZER")
    print("46) Angel One ADAPTIVE VOLATILITY MAP")
    print("47) Angel One SAFETY LAYER V3 (Overfit Guard + Noise Suppressor)")
    print("48) Angel One MARKET WARMUP SCANNER (Pre-Market Diagnostic)")
    print("49) Angel One SIGNAL RECORD BUFFER (Monday Signals)")
    print("50) Angel One ENVIRONMENT CONSISTENCY CHECKER")
    print("51) Angel One REAL DATA CAPTURE STARTER")
    print("52) Angel One REAL SIGNAL COLLECTOR V2 (Monday Signals)")
    print("53) Angel One OUTCOME PLACEHOLDER GENERATOR")
    print("54) Angel One MARKET REGIME RECORDER")
    print("55) Angel One UNIFIED OUTCOME LOGGER V3")
    print("56) Angel One MISFIRE CLASSIFIER V2")
    print("57) Angel One DAILY LEARNING DIGEST")
    print("58) Angel One REAL THRESHOLD RECOMMENDER V3 (Suggestions Only)")
    print("59) Angel One RISK PROFILE OPTIMIZER V3 (Suggestions Only)")
    print("60) Angel One FEATURE DRIFT ANALYZER")
    print("61) Angel One PERFORMANCE CONSISTENCY CHECKER")
    print("62) Angel One DATASET MERGER (Real + Synthetic)")
    print("63) Angel One BLENDED TRAINING ORCHESTRATOR (Dry-Run)")
    print("64) Angel One ULTRA-MODE READINESS REPORT")
    print("65) Angel One ULTRA HEALTH TREE")
    print("66) Angel One LATENCY DRIFT OBSERVATORY")
    print("67) Angel One FAILURE POINT PREDICTOR")
    print("68) Angel One EXECUTION READINESS AUDITOR")
    print("69) Angel One ULTRA DASHBOARD (Read-Only)")
    print("70) Angel One BUILD REAL MASTER DATASET")
    print("71) Angel One TRAIN REAL+SYNTHETIC BLENDED MODELS (V3)")
    print("72) Angel One SHOW LIVE PROFILES & MODEL SOURCES")
    print("73) Ultra Shadow Data Engine (build shadow master dataset)")
    print("74) Ultra Feature Expander (build ultra training set)")
    print("75) Train Ultra Shadow Models")
    print("76) Ultra Hyperparameter Explorer (report only)")
    print("77) Ultra Risk Regime Classifier (labels + report)")
    print("78) Ultra Multi-Consensus Analyzer (shadow)")
    print("79) Ultra Threshold Lab (shadow analysis)")
    print("80) Ultra Live Signals (shadow, no trades)")
    print("81) Ultra Trade Simulator (shadow only)")
    print("82) Ultra PnL Analyzer (shadow only)")
    print("83) Ultra Promotion Manager (manual only)")
    print("84) Ultra Phase 21: Adaptive Risk Engine (ARE)")
    print("85) Ultra Phase 22: Dynamic Position Sizing Engine")
    print("86) Ultra Phase 23: Volatility Regime Impact Engine")
    print("87) Ultra Phase 24: Confidence Drift Analyzer")
    print("88) Ultra Phase 25: Adaptive Stoploss Engine (ASE)")
    print("89) Ultra Phase 26: Adaptive Target Engine (ATE)")
    print("90) Ultra Phase 27: Risk-Reward Balancer")
    print("91) Ultra Phase 28: Failure-Mode Auto-Corrector")
    print("92) Ultra Phase 29: Sensitivity Analyzer")
    print("93) Ultra Phase 30: Real-Time Calibration Engine (RTCE)")
    print("94) Ultra Phase 31: Decision Fusion")
    print("95) Ultra Phase 32: vs Baseline Comparator")
    print("96) Ultra Phase 33: Promotion Planner")
    print("97) Ultra Phase 34: Live Shadow Comparison")
    print("98) Ultra Phase 35: Decision Auditor")
    print("99) Ultra Phase 36: Continuous Learning Cycle (CULL)")
    print("100) Ultra Phase 37: Policy & Risk Monitor")
    print("101) Ultra Phase 38: Governance Summary")
    print("102) Ultra Phase 39: Shadow Campaign (today)")
    print("103) Ultra Phase 40: Weekly Governance Pack")
    print("104) Ultra Phase 41: Prepare Ultra Promotion (staging only)")
    print("105) Ultra Phase 42: Take Baseline Snapshot")
    print("106) Ultra Phase 42: List / View Snapshots")
    print("107) Ultra Phase 43: Environment & Broker Guard Check")
    print("")
    print("=== UNIVERSAL PHASE RUNNER ===")
    print("108) Run ANY Phase by Number (Phases 108-400)")
    print("109) Run Phase Range (e.g., 361-380 validation suite)")
    print("110) List All Available Phases (show registry)")
    print("")
    print("0) Exit")
    choice = input("Select option: ").strip()
    return choice





def main():
    while True:
        choice = show_menu()
        if choice == "1":
            launch_core()
        elif choice == "2":
            health_main()
        elif choice == "3":
            data_test_main()
        elif choice == "4":
            angelone_test_main()
        elif choice == "5":
            angelone_instr_test_main()
        elif choice == "6":
            angel_options_watch_main()
        elif choice == "7":
            angel_options_watch_loop_main()
        elif choice == "8":
            angel_options_analyze_main()
        elif choice == "9":
            build_angel_training_main()
        elif choice == "10":
            train_angel_models_main()
        elif choice == "11":
            print("Starting Angel One index options LIVE AI signals loop...")
            print("[INFO] This will automatically:")
            print("  - Generate AI signals from live data")
            print("  - Create trade plans for eligible trades")
            print("  - Auto-execute trades (DRY RUN) if enabled in automation config")
            print()
            try:
                print("Initializing AngelOne broker...")
                broker = AngelOneBroker()
                print("Login OK.\n")
            except Exception as e:
                print(f"[ERROR] Failed to initialize AngelOne broker: {e}")
                continue

            interval_sec = 30
            iteration = 0
            pnl_sim_counter = 0

            try:
                while True:
                    iteration += 1
                    pnl_sim_counter += 1
                    print(f"[AI] Snapshot #{iteration} ...")
                    try:
                        df_snap = _build_full_snapshot(broker)
                    except Exception as e:
                        print(f"[ERROR] Failed to build snapshot for AI signals: {e}")
                        df_snap = None

                    if df_snap is None or df_snap.empty:
                        print("  -> No snapshot data returned (check market / instruments).")
                    else:
                        angel_live_ai_signals.run_once_with_snapshot(df_snap)

                        # Periodic PnL simulation if enabled
                        from core.engine.angel_automation_config import AUTOMATION_CONFIG
                        if AUTOMATION_CONFIG.auto_simulate_pnl:
                            if pnl_sim_counter >= AUTOMATION_CONFIG.pnl_sim_interval:
                                pnl_sim_counter = 0
                                try:
                                    from core.engine.angel_pnl_simulator import run_pnl_simulation
                                    print("[AUTO] Running PnL simulation...")
                                    run_pnl_simulation()
                                except Exception as e:
                                    print(f"[WARN] Auto PnL simulation failed: {e}")

                    print(f"Sleeping for {interval_sec} seconds...\n")
                    import time

                    time.sleep(interval_sec)
            except KeyboardInterrupt:
                print("\nStopping Angel One LIVE AI signals loop (Ctrl+C).")
        elif choice == "12":
            print("Running synthetic backtest [CONSERVATIVE]...")
            try:
                angel_synthetic_backtest_run(profile="CONSERVATIVE")
            except Exception as e:
                print(f"[ERROR] Synthetic backtest (CONSERVATIVE) failed: {e}")
        elif choice == "13":
            print("Running synthetic backtest [DEV]...")
            try:
                angel_synthetic_backtest_run(profile="DEV")
            except Exception as e:
                print(f"[ERROR] Synthetic backtest (DEV) failed: {e}")
        elif choice == "14":
            print("Running Angel One trade executor in DRY RUN mode...")
            try:
                from core.engine.angel_trade_executor import execute_dry_run as angel_trade_execute_dry_run
                angel_trade_execute_dry_run()
            except Exception as e:
                print(f"[ERROR] Trade executor (DRY RUN) failed: {e}")
        elif choice == "15":
            try:
                from core.engine.angel_daily_pnl_summary import main as angel_daily_pnl_main
                angel_daily_pnl_main()
            except Exception as e:
                print(f"[ERROR] Daily PnL summary failed: {e}")
        elif choice == "16":
            try:
                from core.engine.angel_intraday_pnl_monitor import main as angel_intraday_pnl_main
                angel_intraday_pnl_main()
            except Exception as e:
                print(f"[ERROR] Intraday PnL monitor failed: {e}")
        elif choice == "17":
            try:
                from core.engine.angel_daily_report_generator import main as angel_daily_report_main
                angel_daily_report_main()
            except Exception as e:
                print(f"[ERROR] Daily report generator failed: {e}")
        elif choice == "18":
            try:
                from core.engine.angel_watchdog_recovery import main as angel_watchdog_main
                angel_watchdog_main()
            except Exception as e:
                print(f"[ERROR] System health check failed: {e}")
        elif choice == "19":
            try:
                from core.engine.angel_auto_threshold_adjuster import main as angel_auto_threshold_main
                angel_auto_threshold_main()
            except Exception as e:
                print(f"[ERROR] Auto threshold adjuster failed: {e}")
        elif choice == "20":
            try:
                from core.engine.angel_confidence_calibrator import main as angel_confidence_main
                angel_confidence_main()
            except Exception as e:
                print(f"[ERROR] Confidence calibrator failed: {e}")
        elif choice == "21":
            try:
                from core.engine.angel_strategy_optimizer import main as angel_strategy_main
                angel_strategy_main()
            except Exception as e:
                print(f"[ERROR] Strategy optimizer failed: {e}")
        elif choice == "22":
            try:
                from core.engine.angel_feature_ranker import main as angel_feature_ranker_main
                angel_feature_ranker_main()
            except Exception as e:
                print(f"[ERROR] Advanced feature ranker failed: {e}")
        elif choice == "23":
            try:
                from core.engine.angel_blended_model_trainer import main as angel_blended_main
                angel_blended_main()
            except Exception as e:
                print(f"[ERROR] Blended model trainer failed: {e}")
        elif choice == "24":
            try:
                from core.engine.angel_market_intelligence_dashboard import main as market_intel_main
                market_intel_main()
            except Exception as e:
                print(f"[ERROR] Market intelligence dashboard failed: {e}")
        elif choice == "25":
            try:
                from core.engine.angel_trade_validator_v2 import main as validator_v2_main
                validator_v2_main()
            except Exception as e:
                print(f"[ERROR] ACTION layer validator failed: {e}")
        elif choice == "26":
            try:
                from core.engine.angel_market_profile import main as market_profile_main
                market_profile_main()
            except Exception as e:
                print(f"[ERROR] Market profile analyzer failed: {e}")
        elif choice == "27":
            try:
                from core.engine.angel_overtrade_detector import main as overtrade_main
                from core.engine.angel_signal_quality_meter import main as quality_main
                from core.engine.angel_execution_guardrail import main as guardrail_main
                from core.engine.angel_market_regime_classifier import main as regime_main
                print("=== SAFETY LAYER V2 - COMPLETE CHECK ===\n")
                overtrade_main()
                print()
                quality_main()
                print()
                guardrail_main()
                print()
                regime_main()
            except Exception as e:
                print(f"[ERROR] Safety layer V2 check failed: {e}")
        elif choice == "28":
            try:
                from core.engine.angel_real_outcome_logger import main as outcome_logger_main
                outcome_logger_main()
            except Exception as e:
                print(f"[ERROR] Real outcome logger failed: {e}")
        elif choice == "29":
            try:
                from core.engine.angel_signal_outcome_analyzer import main as signal_outcome_main
                signal_outcome_main()
            except Exception as e:
                print(f"[ERROR] Signal vs outcome analyzer failed: {e}")
        elif choice == "30":
            try:
                from core.engine.angel_misfire_detector import main as misfire_main
                misfire_main()
            except Exception as e:
                print(f"[ERROR] Misfire detector failed: {e}")
        elif choice == "31":
            try:
                from core.engine.angel_real_threshold_recommender import main as threshold_rec_main
                threshold_rec_main()
            except Exception as e:
                print(f"[ERROR] Real threshold recommender failed: {e}")
        elif choice == "32":
            try:
                from core.engine.angel_risk_profile_optimizer import main as risk_profile_main
                risk_profile_main()
            except Exception as e:
                print(f"[ERROR] Risk profile optimizer failed: {e}")
        elif choice == "33":
            try:
                from core.engine.angel_real_data_extractor import main as real_data_main
                real_data_main()
            except Exception as e:
                print(f"[ERROR] Real data extractor failed: {e}")
        elif choice == "34":
            try:
                from core.engine.angel_blended_dataset_builder import main as blended_builder_main
                blended_builder_main()
            except Exception as e:
                print(f"[ERROR] Blended dataset builder failed: {e}")
        elif choice == "35":
            try:
                from core.engine.angel_blended_model_trainer_v2 import main as blended_trainer_main
                blended_trainer_main()
            except Exception as e:
                print(f"[ERROR] Blended model trainer failed: {e}")
        elif choice == "36":
            try:
                from core.engine.angel_daily_learning_report import main as daily_learning_main
                daily_learning_main()
            except Exception as e:
                print(f"[ERROR] Daily learning report failed: {e}")
        elif choice == "37":
            try:
                from core.engine.angel_rolling_learning_dashboard import main as rolling_dashboard_main
                rolling_dashboard_main()
            except Exception as e:
                print(f"[ERROR] Rolling learning dashboard failed: {e}")
        elif choice == "38":
            try:
                from core.engine.angel_blended_model_trainer_v2 import main as blended_trainer_v2_main
                blended_trainer_v2_main()
            except Exception as e:
                print(f"[ERROR] Blended model trainer V2 failed: {e}")
        elif choice == "39":
            try:
                from core.engine.angel_ultramode_prep import main as ultramode_main
                ultramode_main()
            except Exception as e:
                print(f"[ERROR] Ultra-Mode prep check failed: {e}")
        elif choice == "40":
            try:
                from core.engine.angel_daily_auto_reports import main as daily_auto_main
                daily_auto_main()
            except Exception as e:
                print(f"[ERROR] Daily auto-reports failed: {e}")
        elif choice == "41":
            try:
                from core.engine.angel_weekly_summary_report import main as weekly_summary_main
                weekly_summary_main()
            except Exception as e:
                print(f"[ERROR] Weekly summary report failed: {e}")
        elif choice == "42":
            try:
                from core.engine.angel_monday_diagnostic import main as monday_diag_main
                monday_diag_main()
            except Exception as e:
                print(f"[ERROR] Monday morning diagnostic failed: {e}")
        elif choice == "43":
            try:
                from core.engine.angel_report_scheduler import main as report_scheduler_main
                report_scheduler_main()
            except Exception as e:
                print(f"[ERROR] Report scheduler failed: {e}")
        elif choice == "44":
            try:
                from core.engine.angel_live_snapshot_reasoner import main as snapshot_reasoner_main
                snapshot_reasoner_main()
            except Exception as e:
                print(f"[ERROR] Live snapshot reasoner failed: {e}")
        elif choice == "45":
            try:
                from core.engine.angel_outcome_confidence_analyzer import main as confidence_analyzer_main
                confidence_analyzer_main()
            except Exception as e:
                print(f"[ERROR] Outcome confidence analyzer failed: {e}")
        elif choice == "46":
            try:
                from core.engine.angel_adaptive_volatility_map import main as volatility_map_main
                volatility_map_main()
            except Exception as e:
                print(f"[ERROR] Adaptive volatility map failed: {e}")
        elif choice == "47":
            try:
                from core.engine.angel_safety_layer_v3 import main as safety_v3_main
                safety_v3_main()
            except Exception as e:
                print(f"[ERROR] Safety layer V3 failed: {e}")
        elif choice == "48":
            try:
                from core.engine.angel_market_warmup_scanner import main as warmup_main
                warmup_main()
            except Exception as e:
                print(f"[ERROR] Market warmup scanner failed: {e}")
        elif choice == "49":
            try:
                from core.engine.angel_signal_record_buffer import main as buffer_main
                buffer_main()
            except Exception as e:
                print(f"[ERROR] Signal record buffer failed: {e}")
        elif choice == "50":
            try:
                from core.engine.angel_env_consistency_checker import main as consistency_main
                consistency_main()
            except Exception as e:
                print(f"[ERROR] Environment consistency checker failed: {e}")
        elif choice == "51":
            try:
                from core.engine.angel_real_data_capture_starter import main as capture_starter_main
                capture_starter_main()
            except Exception as e:
                print(f"[ERROR] Real data capture starter failed: {e}")
        elif choice == "52":
            try:
                from core.engine.angel_real_signal_collector_v2 import main as signal_collector_main
                signal_collector_main()
            except Exception as e:
                print(f"[ERROR] Real signal collector V2 failed: {e}")
        elif choice == "53":
            try:
                from core.engine.angel_outcome_placeholder_generator import main as placeholder_main
                placeholder_main()
            except Exception as e:
                print(f"[ERROR] Outcome placeholder generator failed: {e}")
        elif choice == "54":
            try:
                from core.engine.angel_market_regime_recorder import main as regime_recorder_main
                regime_recorder_main()
            except Exception as e:
                print(f"[ERROR] Market regime recorder failed: {e}")
        elif choice == "55":
            try:
                from core.engine.angel_unified_outcome_logger_v3 import main as outcome_logger_v3_main
                outcome_logger_v3_main()
            except Exception as e:
                print(f"[ERROR] Unified outcome logger V3 failed: {e}")
        elif choice == "56":
            try:
                from core.engine.angel_misfire_classifier_v2 import main as misfire_classifier_v2_main
                misfire_classifier_v2_main()
            except Exception as e:
                print(f"[ERROR] Misfire classifier V2 failed: {e}")
        elif choice == "57":
            try:
                from core.engine.angel_daily_learning_digest import main as daily_digest_main
                daily_digest_main()
            except Exception as e:
                print(f"[ERROR] Daily learning digest failed: {e}")
        elif choice == "58":
            try:
                from core.engine.angel_real_threshold_reco_v3 import main as threshold_reco_v3_main
                threshold_reco_v3_main()
            except Exception as e:
                print(f"[ERROR] Real threshold recommender V3 failed: {e}")
        elif choice == "59":
            try:
                from core.engine.angel_risk_profile_optimizer_v3 import main as risk_profile_v3_main
                risk_profile_v3_main()
            except Exception as e:
                print(f"[ERROR] Risk profile optimizer V3 failed: {e}")
        elif choice == "60":
            try:
                from core.engine.angel_feature_drift_analyzer import main as drift_analyzer_main
                drift_analyzer_main()
            except Exception as e:
                print(f"[ERROR] Feature drift analyzer failed: {e}")
        elif choice == "61":
            try:
                from core.engine.angel_performance_consistency_checker import main as consistency_checker_main
                consistency_checker_main()
            except Exception as e:
                print(f"[ERROR] Performance consistency checker failed: {e}")
        elif choice == "62":
            try:
                from core.engine.angel_dataset_merger_real_synth_v1 import main as dataset_merger_main
                dataset_merger_main()
            except Exception as e:
                print(f"[ERROR] Dataset merger failed: {e}")
        elif choice == "63":
            try:
                from core.engine.angel_blended_training_orchestrator_dryrun import main as training_orchestrator_main
                training_orchestrator_main()
            except Exception as e:
                print(f"[ERROR] Blended training orchestrator failed: {e}")
        elif choice == "64":
            try:
                from core.engine.angel_ultra_mode_readiness_report import main as readiness_report_main
                readiness_report_main()
            except Exception as e:
                print(f"[ERROR] Ultra-Mode readiness report failed: {e}")
        elif choice == "65":
            try:
                from core.engine.angel_ultra_health_tree import main as health_tree_main
                health_tree_main()
            except Exception as e:
                print(f"[ERROR] Ultra health tree failed: {e}")
        elif choice == "66":
            try:
                from core.engine.angel_latency_drift_observatory import main as latency_drift_main
                latency_drift_main()
            except Exception as e:
                print(f"[ERROR] Latency drift observatory failed: {e}")
        elif choice == "67":
            try:
                from core.engine.angel_failure_point_predictor import main as failure_point_main
                failure_point_main()
            except Exception as e:
                print(f"[ERROR] Failure point predictor failed: {e}")
        elif choice == "68":
            try:
                from core.engine.angel_execution_readiness_auditor import main as execution_auditor_main
                execution_auditor_main()
            except Exception as e:
                print(f"[ERROR] Execution readiness auditor failed: {e}")
        elif choice == "69":
            try:
                from core.engine.angel_ultra_dashboard_readonly import main as dashboard_main
                dashboard_main()
            except Exception as e:
                print(f"[ERROR] Ultra dashboard failed: {e}")
        elif choice == "70":
            try:
                from core.engine.angel_real_master_dataset import main as master_dataset_main
                master_dataset_main()
            except Exception as e:
                print(f"[ERROR] Real master dataset builder failed: {e}")
        elif choice == "71":
            try:
                from core.engine.angel_blended_training_v3 import main as blended_training_v3_main
                blended_training_v3_main()
            except Exception as e:
                print(f"[ERROR] Blended training V3 failed: {e}")
        elif choice == "72":
            try:
                from core.engine.angel_model_selector import main as model_selector_main
                model_selector_main()
            except Exception as e:
                print(f"[ERROR] Model selector failed: {e}")
        elif choice == "73":
            try:
                from core.engine.ultra_shadow_data_engine import main as shadow_data_main
                shadow_data_main()
            except Exception as e:
                print(f"[ERROR] Ultra shadow data engine failed: {e}")
        elif choice == "74":
            try:
                from core.engine.ultra_feature_engineering import main as ultra_feature_main
                ultra_feature_main()
            except Exception as e:
                print(f"[ERROR] Ultra feature expander failed: {e}")
        elif choice == "75":
            try:
                from core.engine.ultra_train_models import main as ultra_train_main
                ultra_train_main()
            except Exception as e:
                print(f"[ERROR] Ultra train models failed: {e}")
        elif choice == "76":
            try:
                from core.engine.ultra_hparam_explorer import main as hparam_explorer_main
                hparam_explorer_main()
            except Exception as e:
                print(f"[ERROR] Ultra hyperparameter explorer failed: {e}")
        elif choice == "77":
            try:
                from core.engine.ultra_regime_classifier import main as regime_classifier_main
                regime_classifier_main()
            except Exception as e:
                print(f"[ERROR] Ultra regime classifier failed: {e}")
        elif choice == "78":
            try:
                from core.engine.ultra_multi_consensus import main as multi_consensus_main
                multi_consensus_main()
            except Exception as e:
                print(f"[ERROR] Ultra multi-consensus analyzer failed: {e}")
        elif choice == "79":
            try:
                from core.engine.ultra_threshold_lab import main as threshold_lab_main
                threshold_lab_main()
            except Exception as e:
                print(f"[ERROR] Ultra threshold lab failed: {e}")
        elif choice == "80":
            try:
                from core.engine.ultra_live_signals_shadow import main as ultra_live_shadow_main
                ultra_live_shadow_main()
            except Exception as e:
                print(f"[ERROR] Ultra live signals shadow failed: {e}")
        elif choice == "81":
            try:
                from core.engine.ultra_trade_simulator import main as ultra_trade_sim_main
                ultra_trade_sim_main()
            except Exception as e:
                print(f"[ERROR] Ultra trade simulator failed: {e}")
        elif choice == "82":
            try:
                from core.engine.ultra_pnl_analyzer import main as ultra_pnl_analyzer_main
                ultra_pnl_analyzer_main()
            except Exception as e:
                print(f"[ERROR] Ultra PnL analyzer failed: {e}")
        elif choice == "83":
            try:
                from core.engine.ultra_promotion_manager import main as ultra_promotion_main
                ultra_promotion_main()
            except Exception as e:
                print(f"[ERROR] Ultra promotion manager failed: {e}")
        elif choice == "84":
            try:
                from core.ultra.phase21_adaptive_risk_engine import main as phase21_main
                phase21_main()
            except Exception as e:
                print(f"[ERROR] Phase 21 Adaptive Risk Engine failed: {e}")
        elif choice == "85":
            try:
                from core.ultra.phase22_position_sizing import main as phase22_main
                phase22_main()
            except Exception as e:
                print(f"[ERROR] Phase 22 Position Sizing Engine failed: {e}")
        elif choice == "86":
            try:
                from core.ultra.phase23_volatility_impact import main as phase23_main
                phase23_main()
            except Exception as e:
                print(f"[ERROR] Phase 23 Volatility Impact Engine failed: {e}")
        elif choice == "87":
            try:
                from core.ultra.phase24_confidence_drift import main as phase24_main
                phase24_main()
            except Exception as e:
                print(f"[ERROR] Phase 24 Confidence Drift Analyzer failed: {e}")
        elif choice == "88":
            try:
                from core.ultra.phase25_stoploss_engine import main as phase25_main
                phase25_main()
            except Exception as e:
                print(f"[ERROR] Phase 25 Adaptive Stoploss Engine failed: {e}")
        elif choice == "89":
            try:
                from core.ultra.phase26_target_engine import main as phase26_main
                phase26_main()
            except Exception as e:
                print(f"[ERROR] Phase 26 Adaptive Target Engine failed: {e}")
        elif choice == "90":
            try:
                from core.ultra.phase27_rr_balancer import main as phase27_main
                phase27_main()
            except Exception as e:
                print(f"[ERROR] Phase 27 Risk-Reward Balancer failed: {e}")
        elif choice == "91":
            try:
                from core.ultra.phase28_auto_corrector import main as phase28_main
                phase28_main()
            except Exception as e:
                print(f"[ERROR] Phase 28 Failure-Mode Auto-Corrector failed: {e}")
        elif choice == "92":
            try:
                from core.ultra.phase29_sensitivity import main as phase29_main
                phase29_main()
            except Exception as e:
                print(f"[ERROR] Phase 29 Sensitivity Analyzer failed: {e}")
        elif choice == "93":
            try:
                from core.ultra.phase30_calibration_engine import main as phase30_main
                phase30_main()
            except Exception as e:
                print(f"[ERROR] Phase 30 Real-Time Calibration Engine failed: {e}")
        elif choice == "94":
            try:
                from core.engine.system3_phase31_ultra_fusion import run_phase31_fusion
                run_phase31_fusion()
            except Exception as e:
                print(f"[ERROR] Phase 31 Ultra Decision Fusion failed: {e}")
        elif choice == "95":
            try:
                from core.engine.system3_phase32_ultra_vs_baseline import run_phase32_comparison
                run_phase32_comparison()
            except Exception as e:
                print(f"[ERROR] Phase 32 Ultra vs Baseline Comparator failed: {e}")
        elif choice == "96":
            try:
                from core.engine.system3_phase33_promotion_planner import run_phase33_promotion_planner
                run_phase33_promotion_planner()
            except Exception as e:
                print(f"[ERROR] Phase 33 Ultra Promotion Planner failed: {e}")
        elif choice == "97":
            try:
                from core.engine.system3_phase34_ultra_shadow_exec import run_phase34_shadow_once
                run_phase34_shadow_once()
            except Exception as e:
                print(f"[ERROR] Phase 34 Ultra Live Shadow Comparison failed: {e}")
        elif choice == "98":
            try:
                from core.engine.system3_phase35_ultra_auditor import run_phase35_audit
                run_phase35_audit()
            except Exception as e:
                print(f"[ERROR] Phase 35 Ultra Decision Auditor failed: {e}")
        elif choice == "99":
            try:
                from core.engine.system3_phase36_cull_orchestrator import run_phase36_cull_full_cycle
                run_phase36_cull_full_cycle()
            except Exception as e:
                print(f"[ERROR] Phase 36 Ultra Continuous Learning Cycle failed: {e}")
        elif choice == "100":
            try:
                from core.engine.system3_phase37_policy_risk_monitor import run_phase37_policy_risk_dashboard
                run_phase37_policy_risk_dashboard()
            except Exception as e:
                print(f"[ERROR] Phase 37 Ultra Policy & Risk Monitor failed: {e}")
        elif choice == "101":
            try:
                from core.engine.system3_phase38_governance_summary import run_phase38_governance_summary
                run_phase38_governance_summary()
            except Exception as e:
                print(f"[ERROR] Phase 38 Ultra Governance Summary failed: {e}")
        elif choice == "102":
            try:
                from core.engine.system3_phase39_shadow_campaign import run_phase39_shadow_campaign
                run_phase39_shadow_campaign()
            except Exception as e:
                print(f"[ERROR] Phase 39 Ultra Shadow Campaign failed: {e}")
        elif choice == "103":
            try:
                from core.engine.system3_phase40_weekly_governance_pack import run_phase40_weekly_pack
                run_phase40_weekly_pack()
            except Exception as e:
                print(f"[ERROR] Phase 40 Weekly Governance Pack failed: {e}")
        elif choice == "104":
            try:
                from core.engine.system3_phase41_promotion_executor import run_phase41_promotion_executor
                run_phase41_promotion_executor()
            except Exception as e:
                print(f"[ERROR] Phase 41 Promotion Executor failed: {e}")
        elif choice == "105":
            try:
                from core.engine.system3_phase42_snapshot_manager import run_phase42_snapshot_create
                run_phase42_snapshot_create()
            except Exception as e:
                print(f"[ERROR] Phase 42 Snapshot Create failed: {e}")
        elif choice == "106":
            try:
                from core.engine.system3_phase42_snapshot_manager import run_phase42_snapshot_list
                run_phase42_snapshot_list()
            except Exception as e:
                print(f"[ERROR] Phase 42 Snapshot List failed: {e}")
        elif choice == "107":
            try:
                from core.engine.system3_phase43_env_guard import run_phase43_env_guard
                run_phase43_env_guard()
            except Exception as e:
                print(f"[ERROR] Phase 43 Environment Guard failed: {e}")

        elif choice == "108":
            # Universal Phase Runner - Run ANY phase by number
            try:
                phase_num = input("Enter phase number (108-400): ").strip()
                if not phase_num.isdigit():
                    print("[ERROR] Invalid phase number")
                    continue
                phase_num = int(phase_num)

                # Try registry-based execution first (for phases 361-380)
                try:
                    from core.engine.system3_phases_361_380_registry import get_phase_callable
                    phase_func = get_phase_callable(phase_num)
                    if phase_func:
                        print(f"\n[INFO] Executing Phase {phase_num} via registry...")
                        result = phase_func()
                        print(f"[SUCCESS] Phase {phase_num} completed")
                        if isinstance(result, dict):
                            import json
                            print(json.dumps(result, indent=2, default=str))
                        continue
                except Exception as e:
                    pass  # Fall through to standard import

                # Standard import pattern for phases 108-360, 381+
                try:
                    import os
                    engine_dir = os.path.join(os.path.dirname(__file__), "core", "engine")
                    matching_files = [f for f in os.listdir(engine_dir) if f.startswith(f"system3_phase{phase_num}_") and f.endswith(".py")]

                    if not matching_files:
                        print(f"[ERROR] Phase {phase_num} file not found")
                        continue

                    # Use first matching file
                    module_file = matching_files[0].replace(".py", "")
                    module = __import__(f"core.engine.{module_file}", fromlist=["main", f"run_phase{phase_num}"])

                    # Try different function names
                    phase_func = None
                    for func_name in [f"run_phase{phase_num}", "main", "run"]:
                        if hasattr(module, func_name):
                            phase_func = getattr(module, func_name)
                            break

                    if not phase_func:
                        print(f"[ERROR] Phase {phase_num} has no callable function (tried: run_phase{phase_num}, main, run)")
                        continue

                    print(f"\n[INFO] Executing Phase {phase_num} ({module_file})...")
                    result = phase_func()
                    print(f"[SUCCESS] Phase {phase_num} completed")
                    if isinstance(result, dict):
                        import json
                        print(json.dumps(result, indent=2, default=str))

                except Exception as e:
                    print(f"[ERROR] Phase {phase_num} execution failed: {e}")
                    import traceback
                    traceback.print_exc()

            except Exception as e:
                print(f"[ERROR] Phase runner failed: {e}")

        elif choice == "109":
            # Run Phase Range (batch execution)
            try:
                range_input = input("Enter phase range (e.g., 361-380 or 108,109,110): ").strip()

                phases_to_run = []
                if "-" in range_input:
                    # Range format: 361-380
                    start, end = map(int, range_input.split("-"))
                    phases_to_run = list(range(start, end + 1))
                elif "," in range_input:
                    # Comma-separated: 108,109,110
                    phases_to_run = [int(p.strip()) for p in range_input.split(",")]
                else:
                    print("[ERROR] Invalid format. Use 'start-end' or 'p1,p2,p3'")
                    continue

                print(f"\n[INFO] Running {len(phases_to_run)} phases: {phases_to_run}")

                results = []
                for phase_num in phases_to_run:
                    try:
                        # Try registry first
                        try:
                            from core.engine.system3_phases_361_380_registry import get_phase_callable
                            phase_func = get_phase_callable(phase_num)
                            if phase_func:
                                print(f"\n--- Phase {phase_num} ---")
                                result = phase_func()
                                results.append({"phase": phase_num, "status": "success", "result": result})
                                continue
                        except Exception:
                            pass

                        # Standard import
                        import os
                        engine_dir = os.path.join(os.path.dirname(__file__), "core", "engine")
                        matching_files = [f for f in os.listdir(engine_dir) if f.startswith(f"system3_phase{phase_num}_") and f.endswith(".py")]

                        if not matching_files:
                            results.append({"phase": phase_num, "status": "not_found"})
                            print(f"[WARN] Phase {phase_num} not found")
                            continue

                        module_file = matching_files[0].replace(".py", "")
                        module = __import__(f"core.engine.{module_file}", fromlist=["main", f"run_phase{phase_num}"])

                        phase_func = None
                        for func_name in [f"run_phase{phase_num}", "main", "run"]:
                            if hasattr(module, func_name):
                                phase_func = getattr(module, func_name)
                                break

                        if phase_func:
                            print(f"\n--- Phase {phase_num} ---")
                            result = phase_func()
                            results.append({"phase": phase_num, "status": "success", "result": result})
                        else:
                            results.append({"phase": phase_num, "status": "no_callable"})
                            print(f"[WARN] Phase {phase_num} has no callable function")

                    except Exception as e:
                        results.append({"phase": phase_num, "status": "error", "error": str(e)})
                        print(f"[ERROR] Phase {phase_num} failed: {e}")

                # Summary
                print("\n=== BATCH EXECUTION SUMMARY ===")
                import json
                print(json.dumps(results, indent=2, default=str))

                success_count = sum(1 for r in results if r["status"] == "success")
                print(f"\nCompleted: {success_count}/{len(phases_to_run)} phases")

            except Exception as e:
                print(f"[ERROR] Batch runner failed: {e}")
                import traceback
                traceback.print_exc()

        elif choice == "110":
            # List all available phases
            try:
                import os
                engine_dir = os.path.join(os.path.dirname(__file__), "core", "engine")
                phase_files = [f for f in os.listdir(engine_dir) if f.startswith("system3_phase") and f.endswith(".py")]

                # Extract phase numbers and names
                phases_info = []
                for filename in sorted(phase_files):
                    # Extract phase number
                    import re
                    match = re.match(r'system3_phase(\d+)_(.+)\.py', filename)
                    if match:
                        phase_num = int(match.group(1))
                        phase_name = match.group(2).replace("_", " ").title()
                        phases_info.append((phase_num, phase_name, filename))

                # Sort by phase number
                phases_info.sort(key=lambda x: x[0])

                print("\n=== SYSTEM3 PHASE REGISTRY ===")
                print(f"Total phases found: {len(phases_info)}")
                print(f"Phases in main menu: 1-107")
                print(f"Phases accessible via runner: 108+")
                print("\n--- PHASES BY NUMBER ---")

                current_range = None
                for phase_num, phase_name, filename in phases_info:
                    # Group by hundreds
                    phase_range = (phase_num // 10) * 10
                    if phase_range != current_range:
                        print(f"\n--- Phases {phase_range}-{phase_range+9} ---")
                        current_range = phase_range

                    # Check if in menu
                    in_menu = "✓" if phase_num <= 107 else " "
                    print(f"[{in_menu}] Phase {phase_num:3d}: {phase_name}")

                print("\n--- SPECIAL REGISTRIES ---")
                print("• Phases 361-380: system3_phases_361_380_registry.py (validation suite)")

                print("\n--- USAGE ---")
                print("• Option 108: Run single phase by number")
                print("• Option 109: Run phase range (e.g., 361-380)")
                print("• Direct Python: from core.engine.system3_phaseXXX_name import main; main()")

            except Exception as e:
                print(f"[ERROR] Failed to list phases: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "0":
            print("Exiting System3 menu.")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
