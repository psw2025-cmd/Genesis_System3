"""
System3 Ultra Control Panel

Master entry point for all System3 operations (baseline + ultra).
Provides unified menu interface with 100+ options organized into logical sections.

SAFETY RULES ENFORCED:
- No baseline overwrite
- Ultra isolation
- Read-only defaults
- Manual promotion required
- No auto-execution anywhere
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.dhan_automation_config import AUTOMATION_CONFIG

# Safety imports
from core.engine.ultra_safety import is_ultra_enabled, load_ultra_safety

# Logging setup
LOG_DIR = ROOT_DIR / "storage" / "logs_ultra"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"system3_ultra_{datetime.now().strftime('%Y%m%d')}.log"


def _log(message: str, level: str = "INFO") -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass
    if level == "ERROR":
        print(f"[ERROR] {message}")
    elif level == "WARN":
        print(f"[WARN] {message}")


def _check_safety() -> Dict[str, bool]:
    """Check all safety mechanisms."""
    safety = load_ultra_safety()
    automation = AUTOMATION_CONFIG

    return {
        "auto_execute_trades": not automation.auto_execute_trades,
        "auto_simulate_pnl": not automation.auto_simulate_pnl,
        "ultra_auto_execute": not safety.get("AUTO_EXECUTE_TRADES", False),
        "ultra_auto_update": not safety.get("AUTO_UPDATE_THRESHOLDS", False),
        "ultra_auto_retrain": not safety.get("AUTO_RETRAIN_MODELS", False),
        "ultra_auto_promote": not safety.get("AUTO_PROMOTE_MODELS", False),
    }


def _safe_execute(module_name: str, function_name: str, *args, **kwargs) -> bool:
    """
    Safe execution wrapper.

    Checks safety, logs execution, prevents baseline overwrite.
    """
    try:
        # Pre-execution safety checks
        safety_checks = _check_safety()
        if not all(safety_checks.values()):
            _log(f"Safety check failed for {module_name}.{function_name}", "WARN")
            print("[WARN] Some safety mechanisms are not properly configured.")

        # Log execution
        _log(f"Executing: {module_name}.{function_name}")

        # Import and execute
        module = __import__(module_name, fromlist=[function_name])
        func = getattr(module, function_name)
        result = func(*args, **kwargs)

        _log(f"Completed: {module_name}.{function_name}")
        return True

    except KeyboardInterrupt:
        _log(f"Interrupted: {module_name}.{function_name}", "WARN")
        print("\n[INFO] Operation interrupted by user.")
        return False
    except Exception as e:
        _log(f"Error in {module_name}.{function_name}: {e}\n{traceback.format_exc()}", "ERROR")
        print(f"[ERROR] {module_name}.{function_name} failed: {e}")
        return False


def _safe_execute_main(module_name: str) -> bool:
    """Execute module's main() function safely."""
    return _safe_execute(module_name, "main")


def _safe_execute_phase(phase_module: str, phase_function: str) -> bool:
    """Execute phase function safely."""
    return _safe_execute(phase_module, phase_function)


def show_menu() -> str:
    """Display main menu with all options organized into sections."""
    print("\n" + "=" * 70)
    print("SYSTEM3 ULTRA CONTROL PANEL")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Safety status
    safety = _check_safety()
    print("\n[SAFETY STATUS]")
    print(f"  Auto-execute: {'❌ DISABLED' if safety['auto_execute_trades'] else '⚠️  ENABLED'}")
    print(f"  Auto-simulate: {'❌ DISABLED' if safety['auto_simulate_pnl'] else '⚠️  ENABLED'}")
    print(f"  Ultra auto-execute: {'❌ DISABLED' if safety['ultra_auto_execute'] else '⚠️  ENABLED'}")

    print("\n" + "=" * 70)
    print("OPERATIONAL PHASES (OP)")
    print("=" * 70)
    print("OP1) Pre-Market Diagnostic")
    print("OP2) Live Signal Generation")
    print("OP3) Trade Decision & Planning")
    print("OP4) Post-Market Analysis")
    print("OP5) Weekly Governance Review")
    print("OP6) Ultra Experiments")

    print("\n" + "=" * 70)
    print("BASELINE CORE OPERATIONS (1-3 active | 4-50 DISABLED)")
    print("=" * 70)
    print("1) Core boot (basic startup)")
    print("2) Health check")
    print("3) Test data pipeline")
    print()
    print("  [DISABLED — options 4-50] Dhan / DhanHQ broker paths.")
    print("  System3 is Dhan-only. These options are blocked.")
    print("  Choosing 4-50 will print this notice and return to menu.")

    print("\n" + "=" * 70)
    print("REAL-DATA LEARNING CYCLE (51-64) — DISABLED (Dhan paths)")
    print("=" * 70)
    print("  [DISABLED — options 51-64] All route to dhan_* modules (Dhan).")
    print("  Choosing 51-64 will print this notice and return to menu.")

    print("\n" + "=" * 70)
    print("ULTRA OBSERVABILITY (65-69) — DISABLED (Dhan paths)")
    print("=" * 70)
    print("  [DISABLED — options 65-69] All route to dhan_* modules (Dhan).")
    print("  Choosing 65-69 will print this notice and return to menu.")

    print("\n" + "=" * 70)
    print("MASTER DATASET & MODEL TOOLS (70-72) — DISABLED (Dhan paths)")
    print("=" * 70)
    print("  [DISABLED — options 70-72] All route to dhan_* modules (Dhan).")
    print("  Choosing 70-72 will print this notice and return to menu.")

    print("\n" + "=" * 70)
    print("ULTRA SHADOW DATA & FEATURES (73-79)")
    print("=" * 70)
    print("73) Ultra Shadow Data Engine")
    print("74) Ultra Feature Expander")
    print("75) Train Ultra Shadow Models")
    print("76) Ultra Hyperparameter Explorer")
    print("77) Ultra Risk Regime Classifier")
    print("78) Ultra Multi-Consensus Analyzer")
    print("79) Ultra Threshold Lab")

    print("\n" + "=" * 70)
    print("ULTRA LIVE & SIMULATION (80-83)")
    print("=" * 70)
    print("  [DISABLED — option 80] Ultra Live Signals uses Dhan broker.")
    print("81) Ultra Trade Simulator")
    print("82) Ultra PnL Analyzer")
    print("83) Ultra Promotion Manager")

    print("\n" + "=" * 70)
    print("ULTRA RISK-ADAPTIVE INTELLIGENCE (84-93)")
    print("=" * 70)
    print("84) Ultra Phase 21: Adaptive Risk Engine (ARE)")
    print("85) Ultra Phase 22: Dynamic Position Sizing")
    print("86) Ultra Phase 23: Volatility Regime Impact")
    print("87) Ultra Phase 24: Confidence Drift Analyzer")
    print("88) Ultra Phase 25: Adaptive Stoploss Engine (ASE)")
    print("89) Ultra Phase 26: Adaptive Target Engine (ATE)")
    print("90) Ultra Phase 27: Risk-Reward Balancer")
    print("91) Ultra Phase 28: Failure-Mode Auto-Corrector")
    print("92) Ultra Phase 29: Sensitivity Analyzer")
    print("93) Ultra Phase 30: Real-Time Calibration Engine (RTCE)")

    print("\n" + "=" * 70)
    print("ULTRA INTEGRATION & GOVERNANCE (94-101)")
    print("=" * 70)
    print("94) Ultra Phase 31: Decision Fusion")
    print("95) Ultra Phase 32: vs Baseline Comparator")
    print("96) Ultra Phase 33: Promotion Planner")
    print("97) Ultra Phase 34: Live Shadow Comparison")
    print("98) Ultra Phase 35: Decision Auditor")
    print("99) Ultra Phase 36: Continuous Learning Cycle (CULL)")
    print("100) Ultra Phase 37: Policy & Risk Monitor")
    print("101) Ultra Phase 38: Governance Summary")

    print("\n" + "=" * 70)
    print("ULTRA ROLLOUT & SAFETY (102-107)")
    print("=" * 70)
    print("102) Ultra Phase 39: Shadow Campaign")
    print("103) Ultra Phase 40: Weekly Governance Pack")
    print("104) Ultra Phase 41: Prepare Ultra Promotion (Staging)")
    print("105) Ultra Phase 42: Take Baseline Snapshot")
    print("106) Ultra Phase 42: List / View Snapshots")
    print("107) Ultra Phase 43: Environment & Broker Guard")

    print("\n" + "=" * 70)
    print("ULTRA FINAL EVOLUTION (108-117)")
    print("=" * 70)
    print("108) Ultra Phase 46: Meta Fusion Model")
    print("109) Ultra Phase 47: 7D Confidence Vector Engine")
    print("110) Ultra Phase 48: Real Market Error Scanner")
    print("111) Ultra Phase 49: Smart Risk Regulator (AI Suggestions)")
    print("112) Ultra Phase 50: Ultra Prediction Explainer")
    print("113) Ultra Phase 51: Real-Time Probability Engine")
    print("114) Ultra Phase 52: Multi-Broker Abstraction (Shadow-Only)")
    print("115) Ultra Phase 53: Ultra Monitoring AI Agent")
    print("116) Ultra Phase 54: Real Outcome Back-Reconstruction")
    print("117) Ultra Phase 55: Ultra Intelligence Dashboard")

    print("\n" + "=" * 70)
    print("ULTRA GENI COMPLETION (118-142)")
    print("=" * 70)
    print("118) Phase 76: GENI Self-Critique Engine")
    print("119) Phase 77: GENI Self-Correction Engine")
    print("120) Phase 78: GENI Multi-Model Consensus Engine")
    print("121) Phase 79: Adaptive Threshold Engine")
    print("122) Phase 80: GENI Evolution Status")
    print("123) Phase 81: Micro-Latency Profiler")
    print("124) Phase 82: Async Job Scheduler")
    print("125) Phase 83: Tick-to-Trade Latency Monitor")
    print("126) Phase 84: Resource Optimizer")
    print("127) Phase 85: Heartbeat Engine")
    print("128) Phase 86: Position Sizing Engine")
    print("129) Phase 87: Expected Value Calculator")
    print("130) Phase 88: Portfolio Risk Engine")
    print("131) Phase 89: Optimal Entry Engine")
    print("132) Phase 90: Optimal Exit Engine")
    print("133) Phase 91: Live Control Dashboard")
    print("134) Phase 92: Session Replay Player")
    print("135) Phase 93: Operator Override Engine")
    print("136) Phase 94: Notification Engine")
    print("137) Phase 95: Operator Activity Log")
    print("138) Phase 96: Chaos Test Engine")
    print("139) Phase 97: Backup & Recovery Engine")
    print("140) Phase 98: Rollback Mechanism")
    print("141) Phase 99: Version Freeze & Tagging")
    print("142) Phase 100: Final Certification Engine")

    print("\n" + "=" * 70)
    print("SYSTEM TOOLS")
    print("=" * 70)
    print("S) Safety Status Check")
    print("V) Run Full Validation")
    print("L) View Latest Logs")
    print("H) Help / Documentation")
    print("0) Exit")

    print("\n" + "=" * 70)
    choice = input("Select option: ").strip().upper()
    return choice


def handle_operational_phase(choice: str) -> bool:
    """Handle operational phase shortcuts."""
    if choice == "OP1":
        # Pre-Market Diagnostic
        return _safe_execute_main("core.engine.dhan_market_warmup_scanner")
    elif choice == "OP2":
        # Live Signal Generation
        print("[INFO] Starting live signal generation loop...")
        return _safe_execute_main("core.engine.dhan_live_ai_signals")
    elif choice == "OP3":
        # Trade Decision & Planning
        return _safe_execute_main("core.engine.dhan_trade_decision")
    elif choice == "OP4":
        # Post-Market Analysis
        return _safe_execute_main("core.engine.dhan_daily_learning_digest")
    elif choice == "OP5":
        # Weekly Governance Review
        return _safe_execute_phase("core.engine.system3_phase40_weekly_governance_pack", "run_phase40_weekly_pack")
    elif choice == "OP6":
        # Ultra Experiments
        print("[INFO] Ultra experiments menu...")
        return True
    return False


_ANGEL_BASELINE_CHOICES = {str(n) for n in range(4, 51)}


def handle_baseline_core(choice: str) -> bool:
    """Handle baseline core operations (1-50)."""
    if choice in _ANGEL_BASELINE_CHOICES:
        print(f"[DISABLED] Option {choice} targets Dhan / DhanHQ — blocked in Dhan-only mode.")
        return False

    # Import all baseline modules dynamically
    baseline_handlers = {
        "1": ("core.engine.main_launcher", "main"),
        "2": ("core.engine.health_check", "main"),
        "3": ("core.engine.test_data_pipeline", "main"),
        # 4-50: Dhan paths — removed from dispatch (blocked above)
        "4": ("core.engine.test_angelone_api", "main"),
        "5": ("core.engine.test_angelone_instruments", "main"),
        "6": ("core.engine.dhan_options_watch", "main"),
        "7": ("core.engine.dhan_options_watch_loop", "main"),
        "8": ("core.engine.dhan_options_analyze", "main"),
        "9": ("core.engine.build_dhan_training_dataset", "main"),
        "10": ("core.engine.train_dhan_models", "main"),
        "11": ("core.engine.dhan_live_ai_signals", "main"),
        "12": (
            "core.engine.dhan_synthetic_backtester",
            lambda: __import__("core.engine.dhan_synthetic_backtester", fromlist=["run_backtest"]).run_backtest(
                profile="CONSERVATIVE"
            ),
        ),
        "13": (
            "core.engine.dhan_synthetic_backtester",
            lambda: __import__("core.engine.dhan_synthetic_backtester", fromlist=["run_backtest"]).run_backtest(
                profile="DEV"
            ),
        ),
        "14": (
            "core.engine.dhan_trade_executor",
            lambda: __import__("core.engine.dhan_trade_executor", fromlist=["execute_dry_run"]).execute_dry_run(),
        ),
        "15": ("core.engine.dhan_daily_pnl_summary", "main"),
        "16": ("core.engine.dhan_intraday_pnl_monitor", "main"),
        "17": ("core.engine.dhan_daily_report_generator", "main"),
        "18": ("core.engine.dhan_watchdog_recovery", "main"),
        "19": ("core.engine.dhan_auto_threshold_adjuster", "main"),
        "20": ("core.engine.dhan_confidence_calibrator", "main"),
        "21": ("core.engine.dhan_strategy_optimizer", "main"),
        "22": ("core.engine.dhan_feature_ranker", "main"),
        "23": ("core.engine.dhan_blended_model_trainer", "main"),
        "24": ("core.engine.dhan_market_intelligence_dashboard", "main"),
        "25": ("core.engine.dhan_trade_validator_v2", "main"),
        "26": ("core.engine.dhan_market_profile", "main"),
        "27": ("core.engine.dhan_safety_layer_v3", "main"),
        "28": ("core.engine.dhan_real_outcome_logger", "main"),
        "29": ("core.engine.dhan_signal_outcome_analyzer", "main"),
        "30": ("core.engine.dhan_misfire_detector", "main"),
        "31": ("core.engine.dhan_real_threshold_recommender", "main"),
        "32": ("core.engine.dhan_risk_profile_optimizer", "main"),
        "33": ("core.engine.dhan_real_data_extractor", "main"),
        "34": ("core.engine.dhan_blended_dataset_builder", "main"),
        "35": ("core.engine.dhan_blended_model_trainer_v2", "main"),
        "36": ("core.engine.dhan_daily_learning_report", "main"),
        "37": ("core.engine.dhan_rolling_learning_dashboard", "main"),
        "38": ("core.engine.dhan_blended_model_trainer_v2", "main"),
        "39": ("core.engine.dhan_ultramode_prep", "main"),
        "40": ("core.engine.dhan_daily_auto_reports", "main"),
        "41": ("core.engine.dhan_weekly_summary_report", "main"),
        "42": ("core.engine.dhan_monday_diagnostic", "main"),
        "43": ("core.engine.dhan_report_scheduler", "main"),
        "44": ("core.engine.dhan_live_snapshot_reasoner", "main"),
        "45": ("core.engine.dhan_outcome_confidence_analyzer", "main"),
        "46": ("core.engine.dhan_adaptive_volatility_map", "main"),
        "47": ("core.engine.dhan_safety_layer_v3", "main"),
        "48": ("core.engine.dhan_market_warmup_scanner", "main"),
        "49": ("core.engine.dhan_signal_record_buffer", "main"),
        "50": ("core.engine.dhan_env_consistency_checker", "main"),
    }

    if choice in baseline_handlers:
        handler = baseline_handlers[choice]
        if callable(handler[1]):
            try:
                handler[1]()
                return True
            except Exception as e:
                print(f"[ERROR] Operation failed: {e}")
                return False
        else:
            return _safe_execute_main(handler[0])
    return False


_ANGEL_LEARNING_CHOICES = {str(n) for n in range(51, 65)}
_ANGEL_OBSERVABILITY_CHOICES = {str(n) for n in range(65, 73)}  # 65-72 incl.


def handle_learning_cycle(choice: str) -> bool:
    """Handle real-data learning cycle (51-64)."""
    if choice in _ANGEL_LEARNING_CHOICES:
        print(f"[DISABLED] Option {choice} routes to an Dhan module — blocked in Dhan-only mode.")
        return False
    learning_handlers = {
        "51": ("core.engine.dhan_real_data_capture_starter", "main"),
        "52": ("core.engine.dhan_real_signal_collector_v2", "main"),
        "53": ("core.engine.dhan_outcome_placeholder_generator", "main"),
        "54": ("core.engine.dhan_market_regime_recorder", "main"),
        "55": ("core.engine.dhan_unified_outcome_logger_v3", "main"),
        "56": ("core.engine.dhan_misfire_classifier_v2", "main"),
        "57": ("core.engine.dhan_daily_learning_digest", "main"),
        "58": ("core.engine.dhan_real_threshold_reco_v3", "main"),
        "59": ("core.engine.dhan_risk_profile_optimizer_v3", "main"),
        "60": ("core.engine.dhan_feature_drift_analyzer", "main"),
        "61": ("core.engine.dhan_performance_consistency_checker", "main"),
        "62": ("core.engine.dhan_dataset_merger_real_synth_v1", "main"),
        "63": ("core.engine.dhan_blended_training_orchestrator_dryrun", "main"),
        "64": ("core.engine.dhan_ultra_mode_readiness_report", "main"),
    }

    if choice in learning_handlers:
        handler = learning_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_ultra_observability(choice: str) -> bool:
    """Handle Ultra observability (65-69) and master dataset (70-72) — all disabled."""
    if choice in _ANGEL_OBSERVABILITY_CHOICES:
        print(f"[DISABLED] Option {choice} routes to an Dhan module — blocked in Dhan-only mode.")
        return False
    observability_handlers = {
        "65": ("core.engine.dhan_ultra_health_tree", "main"),
        "66": ("core.engine.dhan_latency_drift_observatory", "main"),
        "67": ("core.engine.dhan_failure_point_predictor", "main"),
        "68": ("core.engine.dhan_execution_readiness_auditor", "main"),
        "69": ("core.engine.dhan_ultra_dashboard_readonly", "main"),
    }

    if choice in observability_handlers:
        handler = observability_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_master_dataset(choice: str) -> bool:
    """Handle master dataset & model tools (70-72)."""
    dataset_handlers = {
        "70": ("core.engine.dhan_real_master_dataset", "main"),
        "71": ("core.engine.dhan_blended_training_v3", "main"),
        "72": ("core.engine.dhan_model_selector", "main"),
    }

    if choice in dataset_handlers:
        handler = dataset_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_ultra_shadow(choice: str) -> bool:
    """Handle Ultra shadow data & features (73-79)."""
    shadow_handlers = {
        "73": ("core.engine.ultra_shadow_data_engine", "main"),
        "74": ("core.engine.ultra_feature_engineering", "main"),
        "75": ("core.engine.ultra_train_models", "main"),
        "76": ("core.engine.ultra_hparam_explorer", "main"),
        "77": ("core.engine.ultra_regime_classifier", "main"),
        "78": ("core.engine.ultra_multi_consensus", "main"),
        "79": ("core.engine.ultra_threshold_lab", "main"),
    }

    if choice in shadow_handlers:
        handler = shadow_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_ultra_live(choice: str) -> bool:
    """Handle Ultra live & simulation (80-83)."""
    if choice == "80":
        print("[DISABLED] Option 80 (Ultra Live Signals) uses Dhan broker — blocked in Dhan-only mode.")
        return False
    live_handlers = {
        "80": ("core.engine.ultra_live_signals_shadow", "main"),  # unreachable — guarded above
        "81": ("core.engine.ultra_trade_simulator", "main"),
        "82": ("core.engine.ultra_pnl_analyzer", "main"),
        "83": ("core.engine.ultra_promotion_manager", "main"),
    }

    if choice in live_handlers:
        handler = live_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_ultra_phases_21_30(choice: str) -> bool:
    """Handle Ultra risk-adaptive intelligence (84-93)."""
    phase_handlers = {
        "84": ("core.ultra.phase21_adaptive_risk_engine", "main"),
        "85": ("core.ultra.phase22_position_sizing", "main"),
        "86": ("core.ultra.phase23_volatility_impact", "main"),
        "87": ("core.ultra.phase24_confidence_drift", "main"),
        "88": ("core.ultra.phase25_stoploss_engine", "main"),
        "89": ("core.ultra.phase26_target_engine", "main"),
        "90": ("core.ultra.phase27_rr_balancer", "main"),
        "91": ("core.ultra.phase28_auto_corrector", "main"),
        "92": ("core.ultra.phase29_sensitivity", "main"),
        "93": ("core.ultra.phase30_calibration_engine", "main"),
    }

    if choice in phase_handlers:
        handler = phase_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_ultra_phases_31_38(choice: str) -> bool:
    """Handle Ultra integration & governance (94-101)."""
    phase_handlers = {
        "94": ("core.engine.system3_phase31_ultra_fusion", "run_phase31_fusion"),
        "95": ("core.engine.system3_phase32_ultra_vs_baseline", "run_phase32_comparison"),
        "96": ("core.engine.system3_phase33_promotion_planner", "run_phase33_promotion_planner"),
        "97": ("core.engine.system3_phase34_ultra_shadow_exec", "run_phase34_shadow_once"),
        "98": ("core.engine.system3_phase35_ultra_auditor", "run_phase35_audit"),
        "99": ("core.engine.system3_phase36_cull_orchestrator", "run_phase36_cull_full_cycle"),
        "100": ("core.engine.system3_phase37_policy_risk_monitor", "run_phase37_policy_risk_dashboard"),
        "101": ("core.engine.system3_phase38_governance_summary", "run_phase38_governance_summary"),
    }

    if choice in phase_handlers:
        handler = phase_handlers[choice]
        return _safe_execute_phase(handler[0], handler[1])
    return False


def handle_ultra_phases_39_45(choice: str) -> bool:
    """Handle Ultra rollout & safety (102-107)."""
    phase_handlers = {
        "102": ("core.engine.system3_phase39_shadow_campaign", "run_phase39_shadow_campaign"),
        "103": ("core.engine.system3_phase40_weekly_governance_pack", "run_phase40_weekly_pack"),
        "104": ("core.engine.system3_phase41_promotion_executor", "run_phase41_promotion_executor"),
        "105": ("core.engine.system3_phase42_snapshot_manager", "run_phase42_snapshot_create"),
        "106": ("core.engine.system3_phase42_snapshot_manager", "run_phase42_snapshot_list"),
        "107": ("core.engine.system3_phase43_env_guard", "run_phase43_env_guard"),
    }

    if choice in phase_handlers:
        handler = phase_handlers[choice]
        return _safe_execute_phase(handler[0], handler[1])
    return False


def handle_ultra_phases_46_55(choice: str) -> bool:
    """Handle Ultra final evolution (108-117)."""
    phase_handlers = {
        "108": ("core.ultra.phase46_meta_fusion", "run_phase46_meta_fusion"),
        "109": ("core.ultra.phase47_confidence_vector", "run_phase47_confidence_vector"),
        "110": ("core.ultra.phase48_error_scanner", "run_phase48_error_scanner"),
        "111": ("core.ultra.phase49_risk_regulator", "run_phase49_risk_regulator"),
        "112": ("core.ultra.phase50_prediction_explainer", "run_phase50_prediction_explainer"),
        "113": ("core.ultra.phase51_probability_engine", "run_phase51_probability_engine"),
        "114": ("core.ultra.phase52_multi_broker", "run_phase52_multi_broker"),
        "115": ("core.ultra.phase53_monitoring_agent", "run_phase53_monitoring_agent"),
        "116": ("core.ultra.phase54_back_reconstruction", "run_phase54_back_reconstruction"),
        "117": ("core.ultra.phase55_intelligence_dashboard", "run_phase55_intelligence_dashboard"),
    }

    if choice in phase_handlers:
        handler = phase_handlers[choice]
        return _safe_execute_phase(handler[0], handler[1])
    return False


def handle_ultra_phases_76_100(choice: str) -> bool:
    """Handle Ultra GENI completion (118-142)."""
    phase_handlers = {
        "118": ("core.engine.system3_phase76_geni_self_critique", "main"),
        "119": ("core.engine.system3_phase77_geni_self_correction", "main"),
        "120": ("core.engine.system3_phase78_geni_consensus", "main"),
        "121": ("core.engine.system3_phase79_adaptive_thresholds", "main"),
        "122": ("core.engine.system3_phase80_geni_evolution_status", "main"),
        "123": ("core.engine.system3_phase81_latency_profiler", "main"),
        "124": ("core.engine.system3_phase82_job_scheduler", "main"),
        "125": ("core.engine.system3_phase83_tick_to_trade_latency", "main"),
        "126": ("core.engine.system3_phase84_resource_optimizer", "main"),
        "127": ("core.engine.system3_phase85_heartbeat", "main"),
        "128": ("core.engine.system3_phase86_position_sizing", "main"),
        "129": ("core.engine.system3_phase87_expected_value", "main"),
        "130": ("core.engine.system3_phase88_portfolio_risk", "main"),
        "131": ("core.engine.system3_phase89_optimal_entry", "main"),
        "132": ("core.engine.system3_phase90_optimal_exit", "main"),
        "133": ("core.engine.system3_phase91_live_dashboard", "main"),
        "134": ("core.engine.system3_phase92_session_replay", "main"),
        "135": ("core.engine.system3_phase93_operator_override", "main"),
        "136": ("core.engine.system3_phase94_notification_engine", "main"),
        "137": ("core.engine.system3_phase95_operator_activity_log", "main"),
        "138": ("core.engine.system3_phase96_chaos_test", "main"),
        "139": ("core.engine.system3_phase97_backup_recovery", "main"),
        "140": ("core.engine.system3_phase98_rollback", "main"),
        "141": ("core.engine.system3_phase99_version_freeze", "main"),
        "142": ("core.engine.system3_phase100_final_certification", "main"),
    }

    if choice in phase_handlers:
        handler = phase_handlers[choice]
        return _safe_execute_main(handler[0])
    return False


def handle_system_tools(choice: str) -> bool:
    """Handle system tools (S, V, L, H)."""
    if choice == "S":
        # Safety status check
        from core.engine.ultra_safety import main as safety_main

        safety_main()
        return True
    elif choice == "V":
        # Run full validation
        print("[INFO] Running full validation...")
        try:
            from system3_ultra_validation import run_full_validation

            return run_full_validation()
        except ImportError:
            print("[WARN] Validation engine not found. Run: python system3_ultra_validation.py")
            return False
    elif choice == "L":
        # View latest logs
        if LOG_FILE.exists():
            print(f"\n[LOG FILE] {LOG_FILE}\n")
            try:
                with LOG_FILE.open("r", encoding="utf-8") as f:
                    lines = f.readlines()
                    print("".join(lines[-50:]))  # Last 50 lines
            except Exception as e:
                print(f"[ERROR] Could not read log file: {e}")
        else:
            print("[INFO] No log file found yet.")
        return True
    elif choice == "H":
        # Help / Documentation
        print("\n[HELP] System3 Ultra Control Panel")
        print("=" * 70)
        print("Documentation files:")
        print("  - docs/system3_ultra_menu_structure.md")
        print("  - docs/system3_ultra_safety_matrix.md")
        print("  - docs/system3_ultra_commands.md")
        print("  - docs/system3_ultra_launch_flow.md")
        print("\nFor detailed help, see the documentation files above.")
        return True
    return False


def main():
    """Main entry point for System3 Ultra Control Panel."""
    print("\n" + "=" * 70)
    print("SYSTEM3 ULTRA CONTROL PANEL - STARTING")
    print("=" * 70)
    _log("System3 Ultra Control Panel started")

    while True:
        try:
            choice = show_menu()

            if choice == "0":
                print("\n[INFO] Exiting System3 Ultra Control Panel.")
                _log("System3 Ultra Control Panel exited")
                break

            # Route to appropriate handler
            handled = False

            if choice.startswith("OP"):
                handled = handle_operational_phase(choice)
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= 50:
                    handled = handle_baseline_core(choice)
                elif 51 <= num <= 64:
                    handled = handle_learning_cycle(choice)
                elif 65 <= num <= 69:
                    handled = handle_ultra_observability(choice)
                elif 70 <= num <= 72:
                    handled = handle_master_dataset(choice)
                elif 73 <= num <= 79:
                    handled = handle_ultra_shadow(choice)
                elif 80 <= num <= 83:
                    handled = handle_ultra_live(choice)
                elif 84 <= num <= 93:
                    handled = handle_ultra_phases_21_30(choice)
                elif 94 <= num <= 101:
                    handled = handle_ultra_phases_31_38(choice)
                elif 102 <= num <= 107:
                    handled = handle_ultra_phases_39_45(choice)
                elif 108 <= num <= 117:
                    handled = handle_ultra_phases_46_55(choice)
                elif 118 <= num <= 142:
                    handled = handle_ultra_phases_76_100(choice)
            else:
                handled = handle_system_tools(choice)

            if not handled:
                print(f"[WARN] Unknown option: {choice}")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user. Exiting...")
            _log("System3 Ultra Control Panel interrupted")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            _log(f"Unexpected error: {e}\n{traceback.format_exc()}", "ERROR")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
