# System3 Code Index
**Generated:** 2025-12-07 13:56:16

## Total Python Files: 882

### analyze_csv_parsing_issue.py
- **Lines:** 161
- **Header:**
```python
"""
CSV Parsing Issue Analysis - Detailed Investigation
Analyzes the "Expected 72 fields in line 32, saw 75" error
"""

```

### analyze_ev_ready_csv.py
- **Lines:** 94
- **Header:**
```python
"""
Analyze EV-Ready CSV for insights before running Phase 222
"""

import sys
```

### analyze_phases_1_200.py
- **Lines:** 307
- **Header:**
```python
#!/usr/bin/env python3
"""
SYSTEM3 PHASES 1–200 DEEP DIAGNOSTIC ANALYZER
Read-only comprehensive verification tool.
"""
```

### analyze_signal_distribution.py
- **Lines:** 122
- **Header:**
```python
"""
Analyze Signal Distribution in Clean EV-Ready CSV

This script analyzes the distribution of final_score to determine feasible thresholds.
"""
```

### analyze_signals.py
- **Lines:** 42
- **Header:**
```python
import pandas as pd

df = pd.read_csv('storage/live/angel_index_ai_signals.csv')

print("="*60)
```

### analyze_today_run.py
- **Lines:** 290
- **Header:**
```python
"""Analyze today's System3 run and generate reports."""
import sys
import json
import pandas as pd
from pathlib import Path
```

### archive_heartbeat.py
- **Lines:** 56
- **Header:**
```python
#!/usr/bin/env python3
"""
Archive the current heartbeat to storage/heartbeat_archive/ with a timestamped filename.
Optional retention: set HEARTBEAT_ARCHIVE_RETENTION_DAYS to delete older files.
"""
```

### build_system3_structure.py
- **Lines:** 49
- **Header:**
```python
﻿import os

ROOT = os.getcwd()

FOLDERS = [
```

### check_heartbeat_freshness.py
- **Lines:** 80
- **Header:**
```python
#!/usr/bin/env python3
"""
Fail-fast heartbeat freshness check for monitoring/cron.
- Exits 0 if heartbeat is present and _last_updated (or system_info.timestamp) is within threshold.
- Exits 1 with message if stale or missing.
```

### check_phase_compatibility.py
- **Lines:** 78
- **Header:**
```python
"""
Check compatibility between current signal files and Phase 339/370 requirements
"""

import pandas as pd
```

### check_sanity.py
- **Lines:** 74
- **Header:**
```python
import pandas as pd
import os
from datetime import datetime

print("=" * 80)
```

### check_sanity_fixed.py
- **Lines:** 83
- **Header:**
```python
import pandas as pd
import os
from datetime import datetime

print("=" * 80)
```

### check_system3_status.py
- **Lines:** 162
- **Header:**
```python
"""
System3 - Overall Status Check Script

Run this to see the complete present state of System3.
"""
```

### comprehensive_system3_verification.py
- **Lines:** 227
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Comprehensive Verification
Tests all imports, paths, and basic functionality without subprocess.
"""
```

### config\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### config\live_trade_config.py
- **Lines:** 65
- **Header:**
```python
"""
System3 Live Trading Configuration (Mode 1 - Angel One Only)

This is the CENTRAL configuration file for all live trading operations.
All phases 101-130 MUST check these flags before any real trading operations.
```

### core\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\broker\__init__.py
- **Lines:** 6
- **Header:**
```python
"""
System3 Broker Integration Modules

This package contains broker-specific wrappers and integration code.
"""
```

### core\broker\angel_live_order_wrapper.py
- **Lines:** 139
- **Header:**
```python
"""
System3 Phase 103 - AngelOne Low-Level Order Wrapper (Skeleton)

Abstract AngelOne SmartAPI order placement into a dedicated module.
Currently a skeleton - no real API calls yet.
```

### core\brokers\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\brokers\angel_one\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\brokers\angel_one\broker.py
- **Lines:** 101
- **Header:**
```python
import os
import sys

# Ensure project root in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
```

### core\brokers\angel_one\instruments.py
- **Lines:** 159
- **Header:**
```python
import os
import sys
import json
import pandas as pd

```

### core\config\live_trade_config_loader.py
- **Lines:** 71
- **Header:**
```python
"""
System3 Phase 234 - Live Trading Config Loader

Load and validate live trading configuration.
"""
```

### core\data\__init__ - Copy - Copy - Copy (3).py
- **Lines:** 0
- **Header:**
```python
```

### core\data\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\data\data_router.py
- **Lines:** 28
- **Header:**
```python
from core.data.live_fetcher import get_live_price
from core.data.history_fetcher import get_history
from core.data.storage_manager import save_json_snapshot
from core.utils.logger import logger

```

### core\data\history_fetcher.py
- **Lines:** 31
- **Header:**
```python
from core.utils.http_client import HttpClient


def get_history(symbol="BTCUSDT", interval="1h", limit=10):
    """
```

### core\data\live_fetcher.py
- **Lines:** 18
- **Header:**
```python
from core.utils.http_client import HttpClient


def get_live_price(symbol="BTCUSDT"):
    """
```

### core\data\selftest_storage.py
- **Lines:** 28
- **Header:**
```python
import sys
import os

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
```

### core\data\storage_manager.py
- **Lines:** 36
- **Header:**
```python
import os
import json
from datetime import datetime
from core.utils.helpers import ensure_folder

```

### core\engine\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\engine\ai_model\__init__.py
- **Lines:** 22
- **Header:**
```python
"""
AI Model - XGBoost/RandomForest for direction prediction
"""

from .ml_predictor import (
```

### core\engine\ai_model\ml_predictor.py
- **Lines:** 522
- **Header:**
```python
"""
ML Predictor - Train XGBoost/RandomForest for direction prediction

System3 AI upgrade - training data pipeline hardening:
- Robust CSV loader with fast+fallback parser
```

### core\engine\angel_adaptive_volatility_map.py
- **Lines:** 122
- **Header:**
```python
"""
Angel One Index Options - Adaptive Volatility Map

Maps and tracks volatility patterns across underlyings.
SAFE MODE ONLY - Read-only analysis.
```

### core\engine\angel_alerting_system.py
- **Lines:** 157
- **Header:**
```python
"""
Angel One Index Options - Alerting System

Monitors system and sends alerts for:
- Critical errors
```

### core\engine\angel_auto_threshold_adjuster.py
- **Lines:** 276
- **Header:**
```python
"""
Angel One Index Options - Auto Threshold Adjuster

Automatically adjusts thresholds based on real market performance.
Currently DISABLED - requires manual review and approval.
```

### core\engine\angel_automation_config.py
- **Lines:** 32
- **Header:**
```python
"""
Angel One Index Options - Automation Configuration

Controls automatic execution of trades and PnL simulation.
"""
```

### core\engine\angel_blended_dataset_builder.py
- **Lines:** 146
- **Header:**
```python
"""
Angel One Index Options - Blended Dataset Builder

Combines synthetic and real training data.
AUTO-UPDATE: DISABLED - Only builds preview, never auto-trains.
```

### core\engine\angel_blended_model_trainer.py
- **Lines:** 115
- **Header:**
```python
"""
Angel One Index Options - Blended Model Trainer

Trains models using both synthetic and real market data.
Blends training datasets for improved model performance.
```

### core\engine\angel_blended_model_trainer_v2.py
- **Lines:** 217
- **Header:**
```python
"""
Angel One Index Options - Blended Model Trainer V2

Trains models on blended synthetic + real data.
MANUAL TRIGGER ONLY - Never runs automatically.
```

### core\engine\angel_blended_training_orchestrator_dryrun.py
- **Lines:** 156
- **Header:**
```python
"""
Angel One Index Options - Blended Training Orchestrator (Dry-Run)

Creates training plan for blended dataset.
Skip training, dry-run only.
```

### core\engine\angel_blended_training_v3.py
- **Lines:** 333
- **Header:**
```python
"""
Angel One Index Options - Blended Training V3

Trains models using synthetic + real data.
Saves to dedicated directory (core/models/angel_one_real_blended/) without overwriting baseline.
```

### core\engine\angel_breakout_predictor.py
- **Lines:** 163
- **Header:**
```python
"""
Angel One Index Options - Breakout Prediction Engine

Predicts price breakouts above resistance or below support.
"""
```

### core\engine\angel_confidence_calibrator.py
- **Lines:** 171
- **Header:**
```python
"""
Angel One Index Options - Confidence & Score Calibrator

Calibrates model confidence and expected_move_score based on real outcomes.
Helps improve signal quality and threshold selection.
```

### core\engine\angel_confidence_score_fusion.py
- **Lines:** 127
- **Header:**
```python
"""
Angel One Index Options - Confidence-Score Fusion Layer

Fuses confidence and score into unified signal strength metric.
"""
```

### core\engine\angel_daily_auto_reports.py
- **Lines:** 152
- **Header:**
```python
"""
Angel One Index Options - Daily Auto-Reports Generator

Generates automated daily reports (read-only).
AUTO-UPDATE: DISABLED - Only reads and reports.
```

### core\engine\angel_daily_learning_digest.py
- **Lines:** 116
- **Header:**
```python
"""
Angel One Index Options - Daily Learning Digest

Daily report in /reports/real_learning_daily/
SAFE MODE ONLY - Read-only report generation.
```

### core\engine\angel_daily_learning_report.py
- **Lines:** 135
- **Header:**
```python
"""
Angel One Index Options - End-of-Day Learning Report

Generates comprehensive daily learning report.
AUTO-UPDATE: DISABLED - Only reads and reports.
```

### core\engine\angel_daily_pnl_summary.py
- **Lines:** 205
- **Header:**
```python
"""
Angel One Index Options - Daily PnL Summary Tool

Reads PnL logs and produces a clean console summary for today's trading.
Works with both synthetic backtest logs and real live trading logs.
```

### core\engine\angel_daily_report_generator.py
- **Lines:** 250
- **Header:**
```python
"""
Angel One Index Options - Daily Auto-Report Generator

Generates comprehensive daily reports including:
- Signal statistics
```

### core\engine\angel_dataset_merger_real_synth_v1.py
- **Lines:** 209
- **Header:**
```python
"""
Angel One Index Options - Dataset Merger Real + Synthetic V1

Merges real + synthetic data for blended training.
Does NOT train - merging only.
```

### core\engine\angel_dynamic_sl_tp.py
- **Lines:** 150
- **Header:**
```python
"""
Angel One Index Options - Dynamic SL/TP Engine

Computes dynamic stop-loss and take-profit based on volatility and ATR.
"""
```

### core\engine\angel_enhanced_signal_scorer.py
- **Lines:** 134
- **Header:**
```python
"""
Angel One Index Options - Enhanced Signal Scoring Engine

Provides advanced signal scoring beyond basic confidence and expected_move_score.
Includes:
```

### core\engine\angel_entry_optimizer.py
- **Lines:** 120
- **Header:**
```python
"""
Angel One Index Options - Entry Optimizer

Optimizes trade entry timing and price.
"""
```

### core\engine\angel_env_consistency_checker.py
- **Lines:** 185
- **Header:**
```python
"""
Angel One Index Options - Environment Consistency Checker

Checks Python packages, directory structure, config flags.
SAFE MODE ONLY - Reporting only, no auto-fix.
```

### core\engine\angel_execution_guardrail.py
- **Lines:** 147
- **Header:**
```python
"""
Angel One Index Options - Execution Guardrail

Validates execution requests before order placement.
"""
```

### core\engine\angel_execution_readiness_auditor.py
- **Lines:** 155
- **Header:**
```python
"""
Angel One Index Options - Execution Readiness Auditor

Validates if system is safe to start (read-only).
SAFE MODE ONLY - Read-only validation.
```

### core\engine\angel_executor_live_prep.py
- **Lines:** 185
- **Header:**
```python
"""
Angel One Index Options - Executor LIVE Mode Preparation

Prepares the executor for LIVE mode (but keeps it disabled for safety).
This module contains all the infrastructure needed for real order execution,
```

### core\engine\angel_exit_optimizer.py
- **Lines:** 147
- **Header:**
```python
"""
Angel One Index Options - Exit Optimizer

Optimizes trade exit timing and strategy.
"""
```

### core\engine\angel_failure_point_predictor.py
- **Lines:** 204
- **Header:**
```python
"""
Angel One Index Options - Failure Point Predictor

Predict weak points in pipeline.
Read-only analysis.
```

### core\engine\angel_feature_drift_analyzer.py
- **Lines:** 205
- **Header:**
```python
"""
Angel One Index Options - Feature Drift Analyzer

Detects feature drift between training and live data.
No model update - detection only.
```

### core\engine\angel_feature_importance.py
- **Lines:** 197
- **Header:**
```python
"""
angel_feature_importance.py

Compute mutual-information based feature importance for Angel One index options
training data, per underlying.
```

### core\engine\angel_feature_ranker.py
- **Lines:** 121
- **Header:**
```python
"""
Angel One Index Options - Advanced Feature Ranking

Ranks features beyond MI using:
- Permutation importance
```

### core\engine\angel_features.py
- **Lines:** 139
- **Header:**
```python
from __future__ import annotations

import numpy as np
import pandas as pd

```

### core\engine\angel_intraday_pnl_monitor.py
- **Lines:** 169
- **Header:**
```python
"""
Angel One Index Options - Intraday PnL Monitor

Monitors PnL of active trades in real-time during market hours.
Provides alerts and updates on trade performance.
```

### core\engine\angel_iv_estimator.py
- **Lines:** 140
- **Header:**
```python
"""
Angel One Index Options - Synthetic IV Estimator Refinement

Estimates implied volatility from option prices.
"""
```

### core\engine\angel_latency_drift_observatory.py
- **Lines:** 219
- **Header:**
```python
"""
Angel One Index Options - Latency Drift Observatory

Latency / drift detection.
Plots or JSON outputs.
```

### core\engine\angel_live_ai_signals.py
- **Lines:** 454
- **Header:**
```python
import os
import json
from pathlib import Path
from typing import Dict, Any

```

### core\engine\angel_live_ai_signals_v2.py
- **Lines:** 102
- **Header:**
```python
"""
Angel Live AI Signals V2 - Enhanced with System3 Signal Engine

This version integrates the new System3 signal engine while maintaining
compatibility with existing code.
```

### core\engine\angel_live_signals.py
- **Lines:** 291
- **Header:**
```python
import os
import sys
import json
from datetime import datetime

```

### core\engine\angel_live_snapshot_reasoner.py
- **Lines:** 145
- **Header:**
```python
"""
Angel One Index Options - Live Snapshot Reasoner

Provides reasoning and explanations for live snapshot signals.
SAFE MODE ONLY - Read-only analysis.
```

### core\engine\angel_market_intelligence_dashboard.py
- **Lines:** 91
- **Header:**
```python
"""
Angel One Index Options - Market Intelligence Dashboard

Combines all market intelligence modules into unified dashboard.
"""
```

### core\engine\angel_market_profile.py
- **Lines:** 148
- **Header:**
```python
"""
Angel One Index Options - Multi-Timeframe Market Profile

Builds market profile maps for different timeframes.
"""
```

### core\engine\angel_market_regime_classifier.py
- **Lines:** 123
- **Header:**
```python
"""
Angel One Index Options - Market Regime Classifier

Classifies current market regime (trending, ranging, volatile, etc.).
"""
```

### core\engine\angel_market_regime_recorder.py
- **Lines:** 179
- **Header:**
```python
"""
Angel One Index Options - Market Regime Recorder

Logs volatility, microtrend, regime classification.
Output: learning/market_regime_log.csv
```

### core\engine\angel_market_warmup_scanner.py
- **Lines:** 169
- **Header:**
```python
"""
Angel One Index Options - Market Warmup Scanner

Pre-market diagnostics and validation.
SAFE MODE ONLY - Read-only checks, no changes, no execution.
```

### core\engine\angel_microtrend_recognizer.py
- **Lines:** 115
- **Header:**
```python
"""
Angel One Index Options - Microtrend Recognition

Detects short-term trends in price movements.
"""
```

### core\engine\angel_misfire_classifier_v2.py
- **Lines:** 214
- **Header:**
```python
"""
Angel One Index Options - Misfire Classifier V2

Classifies misfires: Wrong Direction, Weak Move, Low Confidence.
Generates report only.
```

### core\engine\angel_misfire_detector.py
- **Lines:** 158
- **Header:**
```python
"""
Angel One Index Options - Misfire Detector

Identifies false positives and false negatives.
AUTO-UPDATE: DISABLED - Only detects and tags, never auto-fixes.
```

### core\engine\angel_model_selector.py
- **Lines:** 319
- **Header:**
```python
"""
Angel One Index Options - Model Selector

Selects models based on active profile (BASELINE or LIVE_BETA).
Reads system3_live_beta_profile.json to determine which models to load.
```

### core\engine\angel_monday_diagnostic.py
- **Lines:** 132
- **Header:**
```python
"""
Angel One Index Options - Monday Morning Pre-Market Diagnostic

Runs comprehensive pre-market diagnostics before trading.
SAFE MODE ONLY - Read-only checks, no actions.
```

### core\engine\angel_multi_model_agreement.py
- **Lines:** 131
- **Header:**
```python
"""
Angel One Index Options - Multi-Model Agreement Filter

Filters signals based on agreement across multiple models or timeframes.
"""
```

### core\engine\angel_multi_resolution_labels.py
- **Lines:** 72
- **Header:**
```python
from __future__ import annotations

from typing import List

import numpy as np
```

### core\engine\angel_multi_timeframe_confirmation.py
- **Lines:** 126
- **Header:**
```python
"""
Angel One Index Options - Multi-Timeframe Confirmation Logic

Confirms signals across multiple timeframes.
"""
```

### core\engine\angel_options_analyze.py
- **Lines:** 244
- **Header:**
```python
import os
import sys
from datetime import datetime

import pandas as pd
```

### core\engine\angel_options_watch.py
- **Lines:** 245
- **Header:**
```python
import os
import sys
from datetime import datetime, date

import pandas as pd
```

### core\engine\angel_options_watch_loop.py
- **Lines:** 297
- **Header:**
```python
import os
import sys
import time
from datetime import datetime, date

```

### core\engine\angel_outcome_confidence_analyzer.py
- **Lines:** 163
- **Header:**
```python
"""
Angel One Index Options - Outcome Confidence Curve Analyzer

Analyzes confidence vs actual outcomes to shape confidence curves.
SAFE MODE ONLY - Read-only analysis.
```

### core\engine\angel_outcome_placeholder_generator.py
- **Lines:** 149
- **Header:**
```python
"""
Angel One Index Options - Outcome Placeholder Generator

Writes placeholders for Monday outcomes.
No scoring, no PnL calculation.
```

### core\engine\angel_overtrade_detector.py
- **Lines:** 136
- **Header:**
```python
"""
Angel One Index Options - Over-Trade Detector

Detects excessive trading activity.
"""
```

### core\engine\angel_performance_consistency_checker.py
- **Lines:** 218
- **Header:**
```python
"""
Angel One Index Options - Performance Consistency Checker

Evaluates consistency of signals across time and underlyings.
Heatmap & stats - read-only analysis.
```

### core\engine\angel_pnl_dummy_seed.py
- **Lines:** 96
- **Header:**
```python
from pathlib import Path

import pandas as pd

from core.engine.train_angel_models import ROOT_DIR as _ROOT_DIR
```

### core\engine\angel_pnl_simulator.py
- **Lines:** 225
- **Header:**
```python
import os
import sys
from dataclasses import dataclass
from pathlib import Path

```

### core\engine\angel_premium_spot_classifier.py
- **Lines:** 134
- **Header:**
```python
"""
Angel One Index Options - Premium-to-Spot Behavior Classifier

Classifies relationship between option premium and underlying spot.
"""
```

### core\engine\angel_real_data_capture_starter.py
- **Lines:** 121
- **Header:**
```python
"""
Angel One Index Options - Real Data Capture Starter

Logs Monday start-time and creates minimal recorder.
SAFE MODE ONLY - Read-only logging, no execution.
```

### core\engine\angel_real_data_extractor.py
- **Lines:** 161
- **Header:**
```python
"""
Angel One Index Options - Real Data Extractor for Training

Converts real outcomes into training rows.
AUTO-UPDATE: DISABLED - Only extracts, never auto-trains.
```

### core\engine\angel_real_master_dataset.py
- **Lines:** 484
- **Header:**
```python
"""
Angel One Index Options - Real Master Dataset Builder

Consolidates live signals, trade plans, PnL outcomes, and real outcome logs
into a single, canonical master dataset for training and analysis.
```

### core\engine\angel_real_outcome_logger.py
- **Lines:** 185
- **Header:**
```python
"""
Angel One Index Options - Real Outcome Logger

Logs every trade (even DRY RUN) into persistent learning table.
AUTO-UPDATE: DISABLED - Only logs, never modifies configs.
```

### core\engine\angel_real_signal_collector_v2.py
- **Lines:** 171
- **Header:**
```python
"""
Angel One Index Options - Real Signal Collector V2

Stores all Monday signals to learning directory.
Writes ONLY to new file: learning/real_signals_raw.csv
```

### core\engine\angel_real_threshold_reco_v3.py
- **Lines:** 227
- **Header:**
```python
"""
Angel One Index Options - Real Threshold Recommender V3

Suggest-only threshold recommendations based on real outcomes.
Must NOT apply them - suggestions only.
```

### core\engine\angel_real_threshold_recommender.py
- **Lines:** 198
- **Header:**
```python
"""
Angel One Index Options - Real Threshold Recommender

Recommends thresholds based on real PnL outcomes.
AUTO-UPDATE: DISABLED - Only generates suggestions, never auto-applies.
```

### core\engine\angel_report_scheduler.py
- **Lines:** 72
- **Header:**
```python
"""
Angel One Index Options - Report Auto-Scheduler

Schedules automatic report generation (read-only).
AUTO-UPDATE: DISABLED - Only schedules, never executes automatically.
```

### core\engine\angel_risk_event_scanner.py
- **Lines:** 119
- **Header:**
```python
"""
Angel One Index Options - Risk Event Scanner

Scans for risk events including big index moves.
"""
```

### core\engine\angel_risk_profile_optimizer.py
- **Lines:** 142
- **Header:**
```python
"""
Angel One Index Options - Position Sizing & Risk Optimizer

Suggests risk profile based on real PnL distribution.
AUTO-UPDATE: DISABLED - Only suggestions, never auto-applies.
```

### core\engine\angel_risk_profile_optimizer_v3.py
- **Lines:** 176
- **Header:**
```python
"""
Angel One Index Options - Risk Profile Optimizer V3

Suggests ideal risk ranges based on real outcomes.
Reports only - no position-size changes.
```

### core\engine\angel_rolling_learning_dashboard.py
- **Lines:** 175
- **Header:**
```python
"""
Angel One Index Options - Rolling 7-Day Learning Dashboard

Aggregates last 7 trading days of learning data.
AUTO-UPDATE: DISABLED - Only reads and reports.
```

### core\engine\angel_safety_checks.py
- **Lines:** 166
- **Header:**
```python
"""
Angel One Index Options - Safety Checks

Validates trade plans and execution requests before processing.
Ensures maximum safety for Monday's live trading.
```

### core\engine\angel_safety_layer_v3.py
- **Lines:** 182
- **Header:**
```python
"""
Angel One Index Options - Safety Layer V3

Overfit Guard + Noise Suppressor for model predictions.
SAFE MODE ONLY - Read-only validation.
```

### core\engine\angel_signal_outcome_analyzer.py
- **Lines:** 243
- **Header:**
```python
"""
Angel One Index Options - Signal vs Outcome Analyzer

Analyzes signal quality vs actual outcomes.
AUTO-UPDATE: DISABLED - Only analyzes and reports.
```

### core\engine\angel_signal_quality_meter.py
- **Lines:** 122
- **Header:**
```python
"""
Angel One Index Options - Signal Quality Meter

Measures and classifies signal quality.
"""
```

### core\engine\angel_signal_record_buffer.py
- **Lines:** 132
- **Header:**
```python
"""
Angel One Index Options - Signal Record Buffer

Temporary buffer for storing Monday signals.
Does NOT touch existing signals file.
```

### core\engine\angel_strategy_optimizer.py
- **Lines:** 220
- **Header:**
```python
"""
Angel One Index Options - Strategy Optimizer

Optimizes overall trading strategy parameters:
- Entry/exit timing
```

### core\engine\angel_synthetic_backtester.py
- **Lines:** 624
- **Header:**
```python
"""
Synthetic backtester for Angel One index options.

Uses:
- Trained models from core/models/angel_one/*_model.pkl
```

### core\engine\angel_threshold_tuner.py
- **Lines:** 396
- **Header:**
```python
"""
angel_threshold_tuner.py

Automatically tunes confidence and score thresholds per underlying
based on historical signal performance.
```

### core\engine\angel_trade_config.py
- **Lines:** 24
- **Header:**
```python
from dataclasses import dataclass


@dataclass
class TradeThresholds:
```

### core\engine\angel_trade_decision.py
- **Lines:** 276
- **Header:**
```python
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
```

### core\engine\angel_trade_executor.py
- **Lines:** 158
- **Header:**
```python
"""
Angel One trade executor (DRY RUN).

Reads:
    storage/live/angel_index_ai_trades_plan.csv
```

### core\engine\angel_trade_lifecycle_logger.py
- **Lines:** 109
- **Header:**
```python
"""
Angel One Index Options - Trade Lifecycle Logger

Tracks complete trade lifecycle from signal → plan → execution → PnL.
Provides detailed audit trail for monitoring and debugging.
```

### core\engine\angel_trade_rules.py
- **Lines:** 111
- **Header:**
```python
from __future__ import annotations

from typing import Any, Dict

import numpy as np
```

### core\engine\angel_trade_validator_v2.py
- **Lines:** 131
- **Header:**
```python
"""
Angel One Index Options - Trade Lifecycle Validator V2

Enhanced validation of complete trade lifecycle.
"""
```

### core\engine\angel_ultra_dashboard_readonly.py
- **Lines:** 195
- **Header:**
```python
"""
Angel One Index Options - Ultra Dashboard (Read-Only)

Mini dashboard with summaries.
Read-only dashboard.
```

### core\engine\angel_ultra_health_tree.py
- **Lines:** 248
- **Header:**
```python
"""
Angel One Index Options - Ultra Health Tree

System dependency + health map.
Read-only health visualization.
```

### core\engine\angel_ultra_mode_readiness_report.py
- **Lines:** 201
- **Header:**
```python
"""
Angel One Index Options - Ultra-Mode Readiness Report

Lists requirements for Ultra-Mode activation.
Does NOT enable Ultra-Mode.
```

### core\engine\angel_ultramode_prep.py
- **Lines:** 150
- **Header:**
```python
"""
Angel One Index Options - Ultra-Mode Prep Layer

Prepares system for future LIVE AUTO mode.
SAFE MODE ONLY - All features disabled by default.
```

### core\engine\angel_unified_outcome_logger_v3.py
- **Lines:** 238
- **Header:**
```python
"""
Angel One Index Options - Unified Outcome Logger V3

Logs real outcomes after market close.
Output: learning/real_outcomes.csv
```

### core\engine\angel_volatility_detector.py
- **Lines:** 129
- **Header:**
```python
"""
Angel One Index Options - Real-Time Volatility Detection

Detects volatility regimes and shocks in real-time market data.
"""
```

### core\engine\angel_watchdog_recovery.py
- **Lines:** 160
- **Header:**
```python
"""
Angel One Index Options - Watchdog & Recovery Process

Monitors system health and recovers from failures:
- Checks if live signals loop is running
```

### core\engine\angel_weekly_summary_report.py
- **Lines:** 114
- **Header:**
```python
"""
Angel One Index Options - Weekly Summary Report

Generates weekly summary report (read-only).
AUTO-UPDATE: DISABLED - Only reads and reports.
```

### core\engine\breakout_model\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Breakout Model - H-L breakouts, CPR, ORB signals, support/resistance breaks
"""

from .breakout_detector import detect_breakouts, compute_cpr_levels, compute_orb_signals
```

### core\engine\breakout_model\breakout_detector.py
- **Lines:** 232
- **Header:**
```python
"""
Breakout Detector - Detect H-L breakouts, CPR, ORB, support/resistance breaks
"""

import numpy as np
```

### core\engine\build_angel_training_dataset.py
- **Lines:** 285
- **Header:**
```python
import os
import sys
from datetime import datetime

import pandas as pd
```

### core\engine\entry_exit_engine\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Entry/Exit Engine - Entry rules, dynamic SL/Target, trailing SL
"""

from .entry_exit_rules import compute_entry_signals, compute_exit_signals, compute_dynamic_sl_tp
```

### core\engine\entry_exit_engine\entry_exit_rules.py
- **Lines:** 174
- **Header:**
```python
"""
Entry/Exit Rules - Compute entry signals, dynamic SL/Target, trailing SL
"""

import numpy as np
```

### core\engine\generate_synthetic_angel_training.py
- **Lines:** 263
- **Header:**
```python
# core/engine/generate_synthetic_angel_training.py

import os
from pathlib import Path
from datetime import datetime, timedelta
```

### core\engine\greeks_engine\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Greeks Engine - Compute option Greeks (delta, gamma, theta, vega)
"""

from .greeks_calculator import compute_greeks, compute_greeks_for_df
```

### core\engine\greeks_engine\greeks_calculator.py
- **Lines:** 252
- **Header:**
```python
"""
Greeks Calculator - Compute delta, gamma, theta, vega for options
"""

import numpy as np
```

### core\engine\health_check.py
- **Lines:** 30
- **Header:**
```python
import sys
import os

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
```

### core\engine\main_launcher.py
- **Lines:** 33
- **Header:**
```python
import sys
import os

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
```

### core\engine\momentum_model\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Momentum Model - Rate of change, acceleration factor
"""

from .momentum_analyzer import compute_momentum_features
```

### core\engine\momentum_model\momentum_analyzer.py
- **Lines:** 78
- **Header:**
```python
"""
Momentum Analyzer - Compute rate of change, acceleration factor
"""

import numpy as np
```

### core\engine\offline_angel_ai_test.py
- **Lines:** 176
- **Header:**
```python
# ================================================
# GENESIS SYSTEM 3
# Offline test of Angel One index options models
#
# Uses:
```

### core\engine\scoring_engine\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Scoring Engine - Combine all signals into final score
"""

from .signal_scorer import compute_final_score, generate_signals
```

### core\engine\scoring_engine\signal_scorer.py
- **Lines:** 295
- **Header:**
```python
"""
Signal Scorer - Combine all signals into final score
"""

import numpy as np
```

### core\engine\scoring_engine\threshold_calibrator.py
- **Lines:** 95
- **Header:**
```python
from pathlib import Path
from typing import Dict, Any

import pandas as pd

```

### core\engine\system3_auto_heal_orchestrator.py
- **Lines:** 515
- **Header:**
```python
"""
System3 Auto-Heal Orchestrator - FULLY AUTOMATED

Automatically detects and fixes common issues:
- Stale data (auto-refresh)
```

### core\engine\system3_lstm_utils.py
- **Lines:** 295
- **Header:**
```python
"""
System3 LSTM Evaluation & Promotion Utilities

Provides robust helpers for Phase 250-255 pipeline:
- Read latest Phase 249 Extended evaluation JSON
```

### core\engine\system3_phase100_final_certification.py
- **Lines:** 162
- **Header:**
```python
"""
System3 Phase 100 - Final Certification Engine

Run a final checklist and produce a certification file:
SYSTEM3_CERTIFIED = TRUE (if all checks pass).
```

### core\engine\system3_phase101_live_trade_config_check.py
- **Lines:** 166
- **Header:**
```python
"""
System3 Phase 101 - Live Trading Config + Sanity Check

Central config layer for live trading (Mode 1 Angel Only) + a check script
that can be run before market to verify configuration.
```

### core\engine\system3_phase102_order_ledger_schema.py
- **Lines:** 153
- **Header:**
```python
"""
System3 Phase 102 - Local Order Ledger Schema

Define the canonical local order ledger CSV that all live trades will write to.
"""
```

### core\engine\system3_phase103_order_ledger_support.py
- **Lines:** 314
- **Header:**
```python
"""
System3 Phase 103 - Order Ledger Support & Integrity Validator

Provides ledger initialization, schema validation, and basic integrity checks.
Bridges Phase 102 (schema definition) and Phase 104 (order construction).
```

### core\engine\system3_phase104_tradeplan_to_orders.py
- **Lines:** 275
- **Header:**
```python
"""
System3 Phase 104 - Trade Plan → Local Order Construction

Take rows from existing trade plan CSV and construct local ledger orders.
"""
```

### core\engine\system3_phase105_ledger_integrity_check.py
- **Lines:** 199
- **Header:**
```python
"""
System3 Phase 105 - Ledger Integrity Checker

Check ledger sanity before any live execution.
"""
```

### core\engine\system3_phase106_dryrun_execution_bridge.py
- **Lines:** 196
- **Header:**
```python
"""
System3 Phase 106 - Live Execution DRY-RUN Bridge

Wire ledger to existing DRY RUN executor without real Angel calls.
"""
```

### core\engine\system3_phase107_live_execution_engine.py
- **Lines:** 317
- **Header:**
```python
"""
System3 Phase 107 - AngelOne LIVE Execution (ONE-LOT, GUARDED, OFF BY DEFAULT)

Actual real-order placement, but tightly guarded and controlled by config.
"""
```

### core\engine\system3_phase108_order_status_refresher.py
- **Lines:** 200
- **Header:**
```python
"""
System3 Phase 108 - Order Status Refresher

Pull order statuses from Angel (or simulated now) and update ledger.
"""
```

### core\engine\system3_phase109_intraday_risk_guard.py
- **Lines:** 176
- **Header:**
```python
"""
System3 Phase 109 - Intraday Risk Guard (Hard Caps)

Before sending orders, enforce capital and drawdown limits.
"""
```

### core\engine\system3_phase110_exit_rule_builder.py
- **Lines:** 175
- **Header:**
```python
"""
System3 Phase 110 - Stop-Loss & Exit Rule Builder (Static)

Build conservative SL/TP rules per trade from existing AI signals.
"""
```

### core\engine\system3_phase111_live_session_brain.py
- **Lines:** 153
- **Header:**
```python
"""
System3 Phase 111 - Live Signal Session Orchestrator (Skeleton)

Orchestrates phases: 101, 102, 104, 105, 109.
Returns combined status for a pre-execution check.
```

### core\engine\system3_phase112_session_loop_controller.py
- **Lines:** 191
- **Header:**
```python
"""
System3 Phase 112 - Session Loop Controller (One-Shot)

One-shot loop controller that orchestrates the full execution flow.
"""
```

### core\engine\system3_phase113_kill_switch_monitor.py
- **Lines:** 100
- **Header:**
```python
"""
System3 Phase 113 - Kill Switch Monitor

Monitor kill switch file and return status.
"""
```

### core\engine\system3_phase114_live_session_health.py
- **Lines:** 179
- **Header:**
```python
"""
System3 Phase 114 - Live Session Health Snapshot

Summarize session health: PLANNED/SENT/FILLED trades, risk guard, kill switch.
"""
```

### core\engine\system3_phase115_intraday_alert_summary.py
- **Lines:** 122
- **Header:**
```python
"""
System3 Phase 115 - Intraday Alert Summary (Text Only)

Generate plain text summary for WhatsApp/Email integration later.
No sending; only content creation.
```

### core\engine\system3_phase116_end_session_auto_stop.py
- **Lines:** 129
- **Header:**
```python
"""
System3 Phase 116 - End-of-Session Auto Stop

Automatically set kill switch at market close.
"""
```

### core\engine\system3_phase117_live_to_learning_bridge.py
- **Lines:** 171
- **Header:**
```python
"""
System3 Phase 117 - Live → Learning Bridge

Connect ledger & PnL to Real Outcome files already used by phases 28–37.
"""
```

### core\engine\system3_phase118_daily_live_pnl_snapshot.py
- **Lines:** 155
- **Header:**
```python
"""
System3 Phase 118 - Daily Live PnL Snapshot (Angel Only)

Summarize daily PnL from ledger.
"""
```

### core\engine\system3_phase119_live_safety_audit.py
- **Lines:** 191
- **Header:**
```python
"""
System3 Phase 119 - Safety Audit for Live Trading

Comprehensive safety check: LIVE_TRADING_ENABLED, risk guard, kill switch, trade counts.
"""
```

### core\engine\system3_phase120_eod_live_summary_pack.py
- **Lines:** 183
- **Header:**
```python
"""
System3 Phase 120 - End-of-Day Live Summary Pack

Combine outputs from 114, 118, 119 into one report.
"""
```

### core\engine\system3_phase121_reserved.py
- **Lines:** 47
- **Header:**
```python
"""
System3 Phase 121 - Reserved for Future Enhancements

This phase is reserved for future System3 live automation enhancements.
"""
```

### core\engine\system3_phase122_reserved.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 122 - Reserved for Future Enhancements
"""

import sys
```

### core\engine\system3_phase123_reserved.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 123 - Reserved for Future Enhancements
"""

import sys
```

### core\engine\system3_phase124_reserved.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 124 - Reserved for Future Enhancements
"""

import sys
```

### core\engine\system3_phase125_reserved.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 125 - Reserved for Future Enhancements
"""

import sys
```

### core\engine\system3_phase126_control_panel_stub.py
- **Lines:** 33
- **Header:**
```python
"""
System3 Phase 126 - Control Panel Stub

Stub for future menu integration in system3_ultra.py.
"""
```

### core\engine\system3_phase127_control_panel_stub.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 127 - Control Panel Stub
"""

import sys
```

### core\engine\system3_phase128_control_panel_stub.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 128 - Control Panel Stub
"""

import sys
```

### core\engine\system3_phase129_control_panel_stub.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 129 - Control Panel Stub
"""

import sys
```

### core\engine\system3_phase130_control_panel_stub.py
- **Lines:** 31
- **Header:**
```python
"""
System3 Phase 130 - Control Panel Stub
"""

import sys
```

### core\engine\system3_phase131_master_session_config.py
- **Lines:** 187
- **Header:**
```python
"""
System3 Phase 131 - Master Session Config

Builds master session configuration for AngelOne-only DRY-RUN mode.
"""
```

### core\engine\system3_phase132_master_health_snapshot.py
- **Lines:** 198
- **Header:**
```python
"""
System3 Phase 132 - Master Session Health Snapshot

Gathers minimal health info for master session.
"""
```

### core\engine\system3_phase133_master_safety_guard.py
- **Lines:** 197
- **Header:**
```python
"""
System3 Phase 133 - Master Safety & Kill-Switch

Computes safety flags and kill-switch state.
"""
```

### core\engine\system3_phase134_master_session_plan.py
- **Lines:** 182
- **Header:**
```python
"""
System3 Phase 134 - Master DRY-RUN Session Plan

Builds session-level plan for DRY-RUN operations.
"""
```

### core\engine\system3_phase135_master_session_summary.py
- **Lines:** 197
- **Header:**
```python
"""
System3 Phase 135 - Master Session Human Summary MD

Generates human-readable summary of master session setup.
"""
```

### core\engine\system3_phase136_angel_symbol_universe.py
- **Lines:** 116
- **Header:**
```python
"""
System3 Phase 136 - Angel Symbol Universe

Creates static metadata for supported Angel index symbols.
"""
```

### core\engine\system3_phase137_expiry_calendar_map.py
- **Lines:** 145
- **Header:**
```python
"""
System3 Phase 137 - Expiry & Calendar Map

Creates expiry calendar mapping for supported underlyings.
"""
```

### core\engine\system3_phase138_risk_tier_assignment.py
- **Lines:** 136
- **Header:**
```python
"""
System3 Phase 138 - Angel Risk Tier Assignment

Assigns risk tiers to underlyings deterministically.
"""
```

### core\engine\system3_phase139_lot_margin_estimator.py
- **Lines:** 139
- **Header:**
```python
"""
System3 Phase 139 - Lot Size & Margin Estimation

Estimates lot sizes and margins for each underlying (approximate metadata).
"""
```

### core\engine\system3_phase140_capital_guardrail.py
- **Lines:** 179
- **Header:**
```python
"""
System3 Phase 140 - Capital Guard & One-Lot Guardrail

Computes capital guardrails for 1-lot-only test mode.
"""
```

### core\engine\system3_phase141_spread_liquidity_estimator.py
- **Lines:** 182
- **Header:**
```python
"""
System3 Phase 141 - Spread & Liquidity Estimation

Estimates spread and liquidity from existing snapshot data.
"""
```

### core\engine\system3_phase142_slippage_calculator.py
- **Lines:** 185
- **Header:**
```python
"""
System3 Phase 142 - DRY-RUN Slippage Calculator (Ledger)

Calculates slippage from DRY-RUN ledger fills.
"""
```

### core\engine\system3_phase143_execution_quality.py
- **Lines:** 163
- **Header:**
```python
"""
System3 Phase 143 - Execution Quality & Fill Heatmap

Classifies execution quality based on slippage.
"""
```

### core\engine\system3_phase144_pnl_vs_execution_scenario.py
- **Lines:** 206
- **Header:**
```python
"""
System3 Phase 144 - DRY-RUN PnL vs Execution Scenario

Recomputes PnL under different execution scenarios.
"""
```

### core\engine\system3_phase145_one_lot_health_report.py
- **Lines:** 216
- **Header:**
```python
"""
System3 Phase 145 - One-Lot Test-Mode Health Report

Summarizes 1-lot DRY-RUN testing health.
"""
```

### core\engine\system3_phase146_index_catalog.py
- **Lines:** 147
- **Header:**
```python
"""
System3 Phase 146 - Phase Index Catalog

Lists all phases and their primary role.
"""
```

### core\engine\system3_phase147_config_inventory.py
- **Lines:** 126
- **Header:**
```python
"""
System3 Phase 147 - Config Inventory

Lists all config JSON files and their purpose.
"""
```

### core\engine\system3_phase148_storage_inventory.py
- **Lines:** 136
- **Header:**
```python
"""
System3 Phase 148 - Storage Inventory

Summarizes storage/ultra and storage/config files.
"""
```

### core\engine\system3_phase149_log_inventory.py
- **Lines:** 132
- **Header:**
```python
"""
System3 Phase 149 - Log Inventory

Lists last-modified times of major log files.
"""
```

### core\engine\system3_phase150_dependency_graph.py
- **Lines:** 162
- **Header:**
```python
"""
System3 Phase 150 - Phase Dependency Graph (Static)

Maps each phase to its inputs/outputs (static mapping).
"""
```

### core\engine\system3_phase151_reserved_stub.py
- **Lines:** 62
- **Header:**
```python
"""
System3 Phase 151 - Reserved Stub

RESERVED FOR FUTURE USE – NO ACTIVE LOGIC
"""
```

### core\engine\system3_phase152_reserved_stub.py
- **Lines:** 26
- **Header:**
```python
"""System3 Phase 152 - Reserved Stub"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase153_reserved_stub.py
- **Lines:** 26
- **Header:**
```python
"""System3 Phase 153 - Reserved Stub"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase154_reserved_stub.py
- **Lines:** 26
- **Header:**
```python
"""System3 Phase 154 - Reserved Stub"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase155_reserved_stub.py
- **Lines:** 26
- **Header:**
```python
"""System3 Phase 155 - Reserved Stub"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase156_capital_curve_analysis.py
- **Lines:** 195
- **Header:**
```python
"""
System3 Phase 156 - Capital Curve & Drawdown Analysis

Analyzes capital curve and drawdown from DRY-RUN PnL data.
"""
```

### core\engine\system3_phase157_misfire_breakdown.py
- **Lines:** 151
- **Header:**
```python
"""
System3 Phase 157 - Misfire Breakdown Analysis

Analyzes misfires (failed predictions) from DRY-RUN data.
"""
```

### core\engine\system3_phase158_regime_stability.py
- **Lines:** 41
- **Header:**
```python
"""System3 Phase 158 - Regime Stability Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase159_threshold_drift.py
- **Lines:** 39
- **Header:**
```python
"""System3 Phase 159 - Threshold Drift Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase160_error_attribution.py
- **Lines:** 39
- **Header:**
```python
"""System3 Phase 160 - Error Attribution Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase161_170_analysis_stubs.py
- **Lines:** 124
- **Header:**
```python
"""
System3 Phases 161-170 - Analysis Stubs

Analysis-only phases for capital, risk, stability logic.
Each phase reads from existing data and writes analysis only.
```

### core\engine\system3_phase161_risk_attribution.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 161 - Risk Attribution Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase161_risk_attribution_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 161 - Risk Attribution Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase162_capital_efficiency.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 162 - Capital Efficiency Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase162_capital_efficiency_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 162 - Capital Efficiency Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase163_trade_frequency.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 163 - Trade Frequency Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase163_trade_frequency_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 163 - Trade Frequency Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase164_win_rate.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 164 - Win Rate Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase164_win_rate_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 164 - Win Rate Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase165_risk-reward_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 165 - Risk-Reward Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase165_risk_reward.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 165 - Risk-Reward Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase166_underlying_performance.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 166 - Underlying Performance Comparison"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase166_underlying_performance_comparison.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 166 - Underlying Performance Comparison

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase167_time-of-day_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 167 - Time-of-Day Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase167_time_of_day.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 167 - Time-of-Day Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase168_volatility_impact.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 168 - Volatility Impact Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase168_volatility_impact_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 168 - Volatility Impact Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase169_confidence_calibration.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 169 - Confidence Calibration Analysis"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase169_confidence_calibration_analysis.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 169 - Confidence Calibration Analysis

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase170_stability_metrics.py
- **Lines:** 33
- **Header:**
```python
"""System3 Phase 170 - Stability Metrics Summary"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase170_stability_metrics_summary.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Phase 170 - Stability Metrics Summary

Analysis-only phase - reads from existing data and writes analysis.
"""
```

### core\engine\system3_phase171_file_backup.py
- **Lines:** 44
- **Header:**
```python
"""System3 Phase 171 - File Backup"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase172_schema_guard.py
- **Lines:** 35
- **Header:**
```python
"""System3 Phase 172 - Schema Guard"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
```

### core\engine\system3_phase173_holiday_detection.py
- **Lines:** 37
- **Header:**
```python
"""System3 Phase 173 - Holiday Detection"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase174_retention_policy.py
- **Lines:** 44
- **Header:**
```python
"""System3 Phase 174 - Retention Policy"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
```

### core\engine\system3_phase175_exception_catalog.py
- **Lines:** 34
- **Header:**
```python
"""System3 Phase 175 - Exception Catalog"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
```

### core\engine\system3_phase176_195_infra_stubs.py
- **Lines:** 129
- **Header:**
```python
"""
System3 Phases 176-195 - Infrastructure Stubs

Non-trading meta/infra modules: summaries, catalogs, utilities.
"""
```

### core\engine\system3_phase176_long_run_summary.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 176 - Long-Run Summary

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase177_performance_trends.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 177 - Performance Trends

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase178_system_health_dashboard.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 178 - System Health Dashboard

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase179_resource_usage_summary.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 179 - Resource Usage Summary

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase180_error_rate_analysis.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 180 - Error Rate Analysis

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase181_config_drift_detection.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 181 - Config Drift Detection

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase182_data_quality_report.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 182 - Data Quality Report

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase183_model_performance_tracking.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 183 - Model Performance Tracking

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase184_signal_quality_metrics.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 184 - Signal Quality Metrics

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase185_trade_execution_summary.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 185 - Trade Execution Summary

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase186_risk_metrics_summary.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 186 - Risk Metrics Summary

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase187_capital_utilization_report.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 187 - Capital Utilization Report

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase188_underlying_performance_trends.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 188 - Underlying Performance Trends

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase189_time_series_analysis.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 189 - Time Series Analysis

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase190_correlation_analysis.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 190 - Correlation Analysis

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase191_feature_importance_summary.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 191 - Feature Importance Summary

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase192_model_comparison_report.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 192 - Model Comparison Report

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase193_system_status_dashboard.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 193 - System Status Dashboard

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase194_operational_metrics.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 194 - Operational Metrics

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase195_master_summary_report.py
- **Lines:** 70
- **Header:**
```python
"""
System3 Phase 195 - Master Summary Report

Non-trading meta/infra module.
"""
```

### core\engine\system3_phase196_dry_run_readiness.py
- **Lines:** 146
- **Header:**
```python
"""
System3 Phase 196 - DRY-RUN Readiness Checklist

Verifies DRY-RUN readiness and provides explicit YES/NO.
"""
```

### core\engine\system3_phase197_micro_capital_test_plan.py
- **Lines:** 122
- **Header:**
```python
"""
System3 Phase 197 - Micro Capital Test Plan MD

Builds a concrete 1-lot-only test plan.
"""
```

### core\engine\system3_phase198_human_gate_checklist.py
- **Lines:** 112
- **Header:**
```python
"""
System3 Phase 198 - Human Gate Checklist (Manual Only)

Generates human-readable checklist for manual confirmation.
"""
```

### core\engine\system3_phase199_live_mode_guard_stub.py
- **Lines:** 113
- **Header:**
```python
"""
System3 Phase 199 - Live Mode Guard Stub (NO REAL LIVE)

Formal guard/memo module stating DRY-RUN mode only.
"""
```

### core\engine\system3_phase200_master_status_snapshot.py
- **Lines:** 190
- **Header:**
```python
"""
System3 Phase 200 - MASTER STATUS SNAPSHOT (Angel DRY-RUN)

Consolidates final view and serves as truth source for session start.
"""
```

### core\engine\system3_phase201_filesystem_integrity.py
- **Lines:** 182
- **Header:**
```python
"""
System3 Phase 201 - Filesystem Integrity Verifier

Scans all core System3 directories and verifies mandatory folders exist.
Auto-creates missing non-critical directories.
```

### core\engine\system3_phase202_permissions_self_repair.py
- **Lines:** 230
- **Header:**
```python
"""
System3 Phase 202 - Permission Self-Repair

Attempts read/write tests on key directories and repairs permissions if needed.
"""
```

### core\engine\system3_phase203_config_consistency.py
- **Lines:** 198
- **Header:**
```python
"""
System3 Phase 203 - Config Consistency Check

Enumerates all JSON config files and validates their structure.
"""
```

### core\engine\system3_phase204_python_env_validator.py
- **Lines:** 160
- **Header:**
```python
"""
System3 Phase 204 - Python Environment Validator

Checks Python version and required packages.
"""
```

### core\engine\system3_phase205_broker_selftest.py
- **Lines:** 169
- **Header:**
```python
"""
System3 Phase 205 - Broker Credential Self-Tester

Performs safe read-only API calls to validate broker connectivity.
"""
```

### core\engine\system3_phase206_model_compatibility.py
- **Lines:** 207
- **Header:**
```python
"""
System3 Phase 206 - Model Compatibility Checker

Scans models directory and checks version compatibility.
"""
```

### core\engine\system3_phase207_hotfix_registry.py
- **Lines:** 126
- **Header:**
```python
"""
System3 Phase 207 - Hotfix Registry Manager

Maintains a JSON registry of applied hotfixes.
"""
```

### core\engine\system3_phase208_signal_consistency.py
- **Lines:** 162
- **Header:**
```python
"""
System3 Phase 208 - Signal Consistency Engine

Validates signal consistency and auto-corrects contradictions.
"""
```

### core\engine\system3_phase209_duplicate_purger.py
- **Lines:** 175
- **Header:**
```python
"""
System3 Phase 209 - Training Data Duplicate Purger

Removes duplicate rows from curated training data.
"""
```

### core\engine\system3_phase210_timegap_analyzer.py
- **Lines:** 163
- **Header:**
```python
"""
System3 Phase 210 - Historical Timegap Analyzer

Detects gaps in historical data timestamps.
"""
```

### core\engine\system3_phase211_feature_drift.py
- **Lines:** 166
- **Header:**
```python
"""
System3 Phase 211 - Feature Drift Monitor

Monitors feature distribution shifts over time.
"""
```

### core\engine\system3_phase212_label_quality.py
- **Lines:** 152
- **Header:**
```python
"""
System3 Phase 212 - Label Quality Inspector

Analyzes label distribution and quality.
"""
```

### core\engine\system3_phase213_training_window.py
- **Lines:** 225
- **Header:**
```python
"""
System3 Phase 213 - Training Window Selector

Evaluates candidate training windows and selects preferred window.
"""
```

### core\engine\system3_phase214_hyperparam_snapshot.py
- **Lines:** 161
- **Header:**
```python
"""
System3 Phase 214 - Model Hyperparameter Snapshotter

Records current ML model hyperparameters.
"""
```

### core\engine\system3_phase215_overfit_sentinel.py
- **Lines:** 109
- **Header:**
```python
"""
System3 Phase 215 - Model Overfit Sentinel

Detects overfitting in ML models.
"""
```

### core\engine\system3_phase216_greeks_audit.py
- **Lines:** 157
- **Header:**
```python
"""
System3 Phase 216 - Greeks Calculation Auditor

Verifies numerical stability of Greeks calculations.
"""
```

### core\engine\system3_phase217_vol_regime.py
- **Lines:** 180
- **Header:**
```python
"""
System3 Phase 217 - Volatility Regime Classifier

Classifies volatility regimes for major underlyings.
"""
```

### core\engine\system3_phase218_momentum_scanner.py
- **Lines:** 188
- **Header:**
```python
"""
System3 Phase 218 - Momentum Pattern Scanner

Detects momentum patterns using technical indicators.
"""
```

### core\engine\system3_phase219_breakout_analyzer.py
- **Lines:** 176
- **Header:**
```python
"""
System3 Phase 219 - Breakout Structure Analyzer

Detects support/resistance levels and breakout zones.
"""
```

### core\engine\system3_phase220_correlation_map.py
- **Lines:** 210
- **Header:**
```python
"""
System3 Phase 220 - Cross-Underlying Correlation Map

Computes rolling correlations between major indices.
"""
```

### core\engine\system3_phase221_forward_returns.py
- **Lines:** 239
- **Header:**
```python
"""
System3 Phase 221 - Forward Return Calculator

Computes forward returns for historical signals.
"""
```

### core\engine\system3_phase222_signal_edge.py
- **Lines:** 262
- **Header:**
```python
"""
System3 Phase 222 - Signal Edge Estimator

Estimates expected value of BUY/SELL signals.
"""
```

### core\engine\system3_phase223_threshold_optimizer.py
- **Lines:** 239
- **Header:**
```python
"""
System3 Phase 223 - Threshold Optimizer

Optimizes BUY/SELL thresholds based on historical data.
"""
```

### core\engine\system3_phase224_score_attribution.py
- **Lines:** 188
- **Header:**
```python
"""
System3 Phase 224 - Score Component Attribution

Decomposes final_score into component contributions.
"""
```

### core\engine\system3_phase225_label_reconciliation.py
- **Lines:** 153
- **Header:**
```python
"""
System3 Phase 225 - Label Reconciliation Engine

Rebuilds labels using consistent rules and forward returns.
"""
```

### core\engine\system3_phase226_feature_importance.py
- **Lines:** 177
- **Header:**
```python
"""
System3 Phase 226 - Feature Importance Tracker

Tracks feature importances from ML models.
"""
```

### core\engine\system3_phase227_latency_profiler.py
- **Lines:** 150
- **Header:**
```python
"""
System3 Phase 227 - Data Latency Profiler

Measures delay between market timestamps and processing times.
"""
```

### core\engine\system3_phase228_snapshot_coverage.py
- **Lines:** 165
- **Header:**
```python
"""
System3 Phase 228 - Snapshot Coverage Auditor

Verifies snapshot coverage for expected time buckets.
"""
```

### core\engine\system3_phase229_schema_guard.py
- **Lines:** 146
- **Header:**
```python
"""
System3 Phase 229 - Data Shape and Schema Guard

Verifies CSV/JSON files match expected schemas.
"""
```

### core\engine\system3_phase230_ai_fallback_audit.py
- **Lines:** 158
- **Header:**
```python
"""
System3 Phase 230 - AI Fallback Behavior Auditor

Reviews logs to count delta-based ai_score fallback usage.
"""
```

### core\engine\system3_phase249_lstm_forward_predictor.py
- **Lines:** 419
- **Header:**
```python
"""
System3 Phase 249 - LSTM Forward Returns Predictor

Train LSTM models to predict forward returns as shadow models.
Does not impact live trading decisions - shadow-only for validation.
```

### core\engine\system3_phase249_model_loader.py
- **Lines:** 85
- **Header:**
```python
"""
Phase 249 Extended: Model Loader & Wrapper

Purpose:
  - Load saved model state dicts from Phase 249 and reconstruct full models
```

### core\engine\system3_phase250_online_learning_manager.py
- **Lines:** 474
- **Header:**
```python
"""
Phase 250: Online Learning Manager (LSTM Model Incremental Trainer)

Purpose:
  - Load trained Phase 249 LSTM models from disk (shadow models)
```

### core\engine\system3_phase251_model_drift_tracker.py
- **Lines:** 335
- **Header:**
```python
"""
System3 Phase 251 - Model Drift Tracker

Detect when LSTM model performance degrades and trigger retraining.
Reads Phase 249 Extended evaluation metrics from Phase 250 output.
```

### core\engine\system3_phase252_model_retraining_scheduler.py
- **Lines:** 254
- **Header:**
```python
"""
System3 Phase 252 - Model Retraining Scheduler

Process drift alerts from Phase 251 and schedule full LSTM retraining.
Shadow-only automation - does not impact live trading decisions.
```

### core\engine\system3_phase253_shadow_model_validator.py
- **Lines:** 248
- **Header:**
```python
"""
System3 Phase 253 - Shadow Model Validator

Validate retrained LSTM models before promoting to production.
Shadow-only validation - does not impact live trading decisions.
```

### core\engine\system3_phase254_production_model_switcher.py
- **Lines:** 189
- **Header:**
```python
"""
System3 Phase 254 - Production Model Switcher

Atomically promote validated shadow models to production.
Shadow-only promotion - does not impact live trading (RandomForest/XGBoost still primary).
```

### core\engine\system3_phase255_model_performance_logger.py
- **Lines:** 163
- **Header:**
```python
"""
System3 Phase 255 - Model Performance Logger

Log LSTM model predictions, accuracy, and confidence over time.
Shadow-only logging - does not impact live trading decisions.
```

### core\engine\system3_phase261_portfolio_risk_analyzer.py
- **Lines:** 143
- **Header:**
```python
"""
System3 Phase 261 - Portfolio Risk Analyzer

Analyzes portfolio-level risk metrics from virtual trades.
Computes position concentration, correlation risk, and overall portfolio exposure.
```

### core\engine\system3_phase262_multitimeframe_consistency.py
- **Lines:** 135
- **Header:**
```python
"""
System3 Phase 262 - Multi-Timeframe Signal Consistency Checker

Validates signal consistency across different timeframes.
Checks if signals align across 1min, 5min, 15min aggregations.
```

### core\engine\system3_phase263_advanced_pnl_attribution.py
- **Lines:** 134
- **Header:**
```python
"""
System3 Phase 263 - Advanced PnL Attribution

Performs detailed PnL attribution analysis by component, timeframe, and regime.
"""
```

### core\engine\system3_phase264_signal_quality_metrics.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 264 - Signal Quality Metrics

Computes signal quality metrics: accuracy, precision, recall, F1-score.
"""
```

### core\engine\system3_phase265_execution_quality_analyzer.py
- **Lines:** 105
- **Header:**
```python
"""
System3 Phase 265 - Execution Quality Analyzer

Analyzes execution quality: slippage, fill rates, latency.
"""
```

### core\engine\system3_phase266_capital_efficiency_tracker.py
- **Lines:** 125
- **Header:**
```python
"""
System3 Phase 266 - Capital Efficiency Tracker

Tracks capital efficiency: ROI, capital utilization, returns per unit risk.
"""
```

### core\engine\system3_phase267_drawdown_analyzer.py
- **Lines:** 126
- **Header:**
```python
"""
System3 Phase 267 - Drawdown Analyzer

Analyzes drawdowns: max drawdown, drawdown duration, recovery time.
"""
```

### core\engine\system3_phase268_sharpe_ratio_calculator.py
- **Lines:** 131
- **Header:**
```python
"""
System3 Phase 268 - Sharpe Ratio Calculator

Calculates Sharpe ratio and other risk-adjusted return metrics.
"""
```

### core\engine\system3_phase269_winrate_by_time.py
- **Lines:** 139
- **Header:**
```python
"""
System3 Phase 269 - Win Rate by Time of Day

Analyzes win rate and performance by hour of day.
"""
```

### core\engine\system3_phase270_regime_performance_comparison.py
- **Lines:** 158
- **Header:**
```python
"""
System3 Phase 270 - Regime Performance Comparison

Compares performance across different volatility regimes.
"""
```

### core\engine\system3_phase271_hyperparameter_search.py
- **Lines:** 96
- **Header:**
```python
"""
System3 Phase 271 - Hyperparameter Search

Performs grid search for optimal ML model hyperparameters.
"""
```

### core\engine\system3_phase272_feature_selection_optimizer.py
- **Lines:** 118
- **Header:**
```python
"""
System3 Phase 272 - Feature Selection Optimizer

Identifies optimal feature subsets for ML models.
"""
```

### core\engine\system3_phase273_model_ensemble_builder.py
- **Lines:** 90
- **Header:**
```python
"""
System3 Phase 273 - Model Ensemble Builder

Builds and evaluates ensemble models combining multiple ML models.
"""
```

### core\engine\system3_phase274_threshold_auto_tuner.py
- **Lines:** 120
- **Header:**
```python
"""
System3 Phase 274 - Threshold Auto-Tuner

Automatically tunes BUY/SELL thresholds based on recent performance.
"""
```

### core\engine\system3_phase275_position_sizing_optimizer.py
- **Lines:** 95
- **Header:**
```python
"""
System3 Phase 275 - Position Sizing Optimizer

Optimizes position sizes based on risk and confidence.
"""
```

### core\engine\system3_phase276_risk_reward_optimizer.py
- **Lines:** 121
- **Header:**
```python
"""
System3 Phase 276 - Risk-Reward Optimizer

Optimizes risk-reward ratios for trades.
"""
```

### core\engine\system3_phase277_entry_timing_optimizer.py
- **Lines:** 118
- **Header:**
```python
"""
System3 Phase 277 - Entry Timing Optimizer

Optimizes entry timing based on historical performance patterns.
"""
```

### core\engine\system3_phase278_exit_timing_optimizer.py
- **Lines:** 127
- **Header:**
```python
"""
System3 Phase 278 - Exit Timing Optimizer

Optimizes exit timing based on historical performance.
"""
```

### core\engine\system3_phase279_portfolio_rebalancer.py
- **Lines:** 119
- **Header:**
```python
"""
System3 Phase 279 - Portfolio Rebalancer

Rebalances portfolio positions based on risk and performance.
"""
```

### core\engine\system3_phase280_strategy_backtester.py
- **Lines:** 115
- **Header:**
```python
"""
System3 Phase 280 - Strategy Backtester

Backtests trading strategies on historical data.
"""
```

### core\engine\system3_phase281_realtime_performance_monitor.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 281 - Real-Time Performance Monitor

Monitors real-time performance metrics during trading sessions.
"""
```

### core\engine\system3_phase282_anomaly_detector.py
- **Lines:** 126
- **Header:**
```python
"""
System3 Phase 282 - Anomaly Detector

Detects anomalies in signals, PnL, and system behavior.
"""
```

### core\engine\system3_phase283_drift_monitor.py
- **Lines:** 126
- **Header:**
```python
"""
System3 Phase 283 - Drift Monitor

Monitors feature drift and model performance drift over time.
"""
```

### core\engine\system3_phase284_alert_aggregator.py
- **Lines:** 85
- **Header:**
```python
"""
System3 Phase 284 - Alert Aggregator

Aggregates and summarizes alerts from various system components.
"""
```

### core\engine\system3_phase285_health_dashboard_generator.py
- **Lines:** 95
- **Header:**
```python
"""
System3 Phase 285 - Health Dashboard Generator

Generates comprehensive system health dashboard.
"""
```

### core\engine\system3_phase286_performance_degradation_detector.py
- **Lines:** 128
- **Header:**
```python
"""
System3 Phase 286 - Performance Degradation Detector

Detects performance degradation over time.
"""
```

### core\engine\system3_phase287_resource_usage_monitor.py
- **Lines:** 95
- **Header:**
```python
"""
System3 Phase 287 - Resource Usage Monitor

Monitors system resource usage: CPU, memory, disk, file sizes.
"""
```

### core\engine\system3_phase288_latency_monitor.py
- **Lines:** 105
- **Header:**
```python
"""
System3 Phase 288 - Latency Monitor

Monitors system latency: signal generation time, model inference time.
"""
```

### core\engine\system3_phase289_error_rate_tracker.py
- **Lines:** 96
- **Header:**
```python
"""
System3 Phase 289 - Error Rate Tracker

Tracks error rates across system components.
"""
```

### core\engine\system3_phase290_system_health_score.py
- **Lines:** 117
- **Header:**
```python
"""
System3 Phase 290 - System Health Score

Calculates overall system health score from multiple metrics.
"""
```

### core\engine\system3_phase291_daily_performance_report.py
- **Lines:** 116
- **Header:**
```python
"""
System3 Phase 291 - Daily Performance Report

Generates comprehensive daily performance report.
"""
```

### core\engine\system3_phase292_weekly_summary_report.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 292 - Weekly Summary Report

Generates weekly summary report aggregating daily performance.
"""
```

### core\engine\system3_phase293_monthly_analytics_report.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 293 - Monthly Analytics Report

Generates comprehensive monthly analytics report.
"""
```

### core\engine\system3_phase294_strategy_performance_report.py
- **Lines:** 115
- **Header:**
```python
"""
System3 Phase 294 - Strategy Performance Report

Generates strategy-level performance report.
"""
```

### core\engine\system3_phase295_risk_metrics_report.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 295 - Risk Metrics Report

Generates comprehensive risk metrics report.
"""
```

### core\engine\system3_phase296_model_performance_report.py
- **Lines:** 115
- **Header:**
```python
"""
System3 Phase 296 - Model Performance Report

Generates ML model performance report.
"""
```

### core\engine\system3_phase297_trade_execution_report.py
- **Lines:** 104
- **Header:**
```python
"""
System3 Phase 297 - Trade Execution Report

Generates trade execution quality report.
"""
```

### core\engine\system3_phase298_system_status_report.py
- **Lines:** 93
- **Header:**
```python
"""
System3 Phase 298 - System Status Report

Generates comprehensive system status report.
"""
```

### core\engine\system3_phase299_master_summary_report.py
- **Lines:** 95
- **Header:**
```python
"""
System3 Phase 299 - Master Summary Report

Generates master summary report aggregating all system metrics.
"""
```

### core\engine\system3_phase300_phase_completion_validator.py
- **Lines:** 83
- **Header:**
```python
"""
System3 Phase 300 - Phase Completion Validator

Validates that all phases 1-300 are implemented and working.
"""
```

### core\engine\system3_phase301_daily_live_vs_forward.py
- **Lines:** 344
- **Header:**
```python
"""
System3 Phase 301 - Daily Live-vs-Forward Performance Tracker

Converts recent signals + forward returns into real, money-like metrics per underlying and signal type.
"""
```

### core\engine\system3_phase302_regime_performance.py
- **Lines:** 226
- **Header:**
```python
"""
System3 Phase 302 - Regime-Aware Performance Profiler

Combines volatility regime info with Phase 301 metrics to see where the system performs best.
"""
```

### core\engine\system3_phase303_edge_decay.py
- **Lines:** 194
- **Header:**
```python
"""
System3 Phase 303 - Intraday Edge Decay Analyzer

Understands how fast signal edge decays after it is generated.
"""
```

### core\engine\system3_phase304_threshold_tuner.py
- **Lines:** 196
- **Header:**
```python
"""
System3 Phase 304 - Dynamic Threshold Tuner (Safe Mode)

Proposes updated BUY/SELL thresholds using Phase 222 + Phases 301-303, but DO NOT change live thresholds automatically.
"""
```

### core\engine\system3_phase305_confidence_tier.py
- **Lines:** 222
- **Header:**
```python
"""
System3 Phase 305 - Confidence Tier Tagger (High/Medium/Low)

Tags each past signal with a confidence tier based on score, edge, and context.
"""
```

### core\engine\system3_phase306_staleness_guard.py
- **Lines:** 228
- **Header:**
```python
"""
System3 Phase 306 - Real-Time Staleness & Latency Guard

Detects and marks stale or delayed snapshots.
AUTO-HEAL INTEGRATED: Automatically triggers recovery actions.
```

### core\engine\system3_phase307_live_vs_test_consistency.py
- **Lines:** 163
- **Header:**
```python
"""
System3 Phase 307 - Live vs Backtest Consistency Checker

Ensures that live DRY-RUN behavior matches what backtest/test-mode would do under the same thresholds.
"""
```

### core\engine\system3_phase308_daily_dashboard.py
- **Lines:** 202
- **Header:**
```python
"""
System3 Phase 308 - Daily PnL & Accuracy Dashboard Generator (Research View)

Produces a single daily dashboard summarizing PnL-like metrics, accuracy, and confidence tiers.
"""
```

### core\engine\system3_phase309_schedule_hints.py
- **Lines:** 157
- **Header:**
```python
"""
System3 Phase 309 - Schedule Hints Generator

Analyzes phase execution patterns and suggests optimal scheduling for phases 301-310.
"""
```

### core\engine\system3_phase310_ultra_health.py
- **Lines:** 226
- **Header:**
```python
"""
System3 Phase 310 - Ultra Health Monitor

Overall health check for phases 301-310 and their integration with the system.
"""
```

### core\engine\system3_phase311_baseline_fs_snapshot.py
- **Lines:** 226
- **Header:**
```python
"""
System3 Phase 311 - Baseline Filesystem Snapshot

Creates a daily filesystem baseline of key System3 files before market,
to detect unexpected edits and support rollback.
```

### core\engine\system3_phase312_phase_registry_self_check.py
- **Lines:** 253
- **Header:**
```python
"""
System3 Phase 312 - Phase Registry Self-Check

Validates phase registry vs actual code implementations and logging.
"""
```

### core\engine\system3_phase313_config_consistency_auditor.py
- **Lines:** 290
- **Header:**
```python
"""
System3 Phase 313 - Config Consistency Auditor

Audits all critical configuration files for syntax, consistency, and conflicts.
"""
```

### core\engine\system3_phase314_data_lineage_tracker.py
- **Lines:** 192
- **Header:**
```python
"""
System3 Phase 314 - Data Lineage Tracker

Tracks origin and lineage of key live and training data files.
"""
```

### core\engine\system3_phase315_transactional_write_guard.py
- **Lines:** 222
- **Header:**
```python
"""
System3 Phase 315 - Transactional Write Guard

Protects critical files from partial or corrupted writes by enforcing transactional writes.
"""
```

### core\engine\system3_phase316_input_schema_gateway.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 316 - Input Schema Gateway

Validates external raw inputs
"""
```

### core\engine\system3_phase317_live_feed_sanitizer.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 317 - Live Feed Sanitizer

Sanitizes live feed data
"""
```

### core\engine\system3_phase318_signal_outlier_detector.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 318 - Signal Outlier Detector

Detects abnormal signals
"""
```

### core\engine\system3_phase319_position_state_consistency_checker.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 319 - Position State Consistency Checker

Checks position consistency
"""
```

### core\engine\system3_phase31_ultra_fusion.py
- **Lines:** 392
- **Header:**
```python
"""
System3 Ultra - Phase 31: Ultra Decision Fusion Layer

Combine all Ultra outputs (SL/TP, risk, position size, regime, confidence, score)
into a single fused per-leg decision.
```

### core\engine\system3_phase320_risk_config_corruption_guard.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 320 - Risk Config Corruption Guard

Detects risk config changes
"""
```

### core\engine\system3_phase321_latency_profiler.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 321 - Latency Profiler

Measures operation latency
"""
```

### core\engine\system3_phase322_resource_usage_monitor.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 322 - Resource Usage Monitor

Monitors CPU/memory usage
"""
```

### core\engine\system3_phase323_phase_health_timeline_builder.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 323 - Phase Health Timeline Builder

Builds phase health timeline
"""
```

### core\engine\system3_phase324_warn_error_cluster_analyzer.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 324 - WARN Error Cluster Analyzer

Clusters WARN/ERROR messages
"""
```

### core\engine\system3_phase325_observability_summary_exporter.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 325 - Observability Summary Exporter

Exports daily observability report
"""
```

### core\engine\system3_phase326_root_cause_hint_generator.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 326 - Root Cause Hint Generator

Generates root cause hints
"""
```

### core\engine\system3_phase327_predictive_failure_scout.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 327 - Predictive Failure Scout

Predicts component failures
"""
```

### core\engine\system3_phase328_daily_integrity_scorecard.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 328 - Daily Integrity Scorecard

Computes daily integrity score
"""
```

### core\engine\system3_phase329_changeset_and_version_recorder.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 329 - Changeset and Version Recorder

Records code/config changes
"""
```

### core\engine\system3_phase32_ultra_vs_baseline.py
- **Lines:** 298
- **Header:**
```python
"""
System3 Ultra - Phase 32: Ultra vs Baseline Comparator

Compare ULTRA fused decisions vs baseline trade plans and PnL.

```

### core\engine\system3_phase330_integrity_gate_before_live_toggle.py
- **Lines:** 103
- **Header:**
```python
"""
System3 Phase 330 - Integrity Gate Before Live Toggle

Final integrity gate verdict
"""
```

### core\engine\system3_phase331_signal_integrity.py
- **Lines:** 225
- **Header:**
```python
"""
System3 Phase 331 - Signal Input Integrity Scanner

Detects structural issues in live signal CSVs before they are used by trade planning phases.
Checks: missing columns, NaNs in key fields, zero rows, mixed dtypes.
```

### core\engine\system3_phase332_signal_volume_coverage.py
- **Lines:** 159
- **Header:**
```python
"""
System3 Phase 332 - Signal Volume & Coverage Monitor

Monitors signal volume and coverage across indices/options to ensure meaningful operation.
"""
```

### core\engine\system3_phase333_signal_consistency.py
- **Lines:** 166
- **Header:**
```python
"""
System3 Phase 333 - Signal Consistency & Duplicate Detector

Detects suspicious duplicates or inconsistent entries in the curated signal file.
"""
```

### core\engine\system3_phase334_model_drift_snapshot.py
- **Lines:** 185
- **Header:**
```python
"""
System3 Phase 334 - Model Drift Snapshot Builder

Creates daily snapshot of key model performance stats for drift detection.
No retraining here, just logging performance metrics.
```

### core\engine\system3_phase335_model_drift_analyzer.py
- **Lines:** 203
- **Header:**
```python
"""
System3 Phase 335 - Model Drift Analyzer (Light)

Reads model_drift_daily.csv and detects early signs of drift.
Compares recent performance against moving averages.
```

### core\engine\system3_phase336_safe_mode_suggestor.py
- **Lines:** 138
- **Header:**
```python
"""
System3 Phase 336 - Safe-Mode Suggestor (Based on Drift)

Suggests safer mode for next trading day if drift is severe (smaller positions, no new positions).
Does NOT enforce automatically - only provides recommendations.
```

### core\engine\system3_phase337_forward_return_quality_tracker.py
- **Lines:** 168
- **Header:**
```python
"""
System3 Phase 337 - Live Forward-Return Quality Tracker

Tracks the quality of forward return data being captured in live signals.
Monitors: data freshness, completeness, anomalies.
```

### core\engine\system3_phase338_signal_outcome_correlation.py
- **Lines:** 157
- **Header:**
```python
"""
System3 Phase 338 - Signal-to-Outcome Correlation Monitor

Monitors correlation between signal scores and actual forward returns.
Helps identify if scoring model is still predictive.
```

### core\engine\system3_phase339_daily_signal_pipeline_summary.py
- **Lines:** 196
- **Header:**
```python
"""
System3 Phase 339 - Daily Signal Pipeline Summary Report

Generates comprehensive daily summary of signal pipeline health.
Aggregates findings from Phases 331-338.
```

### core\engine\system3_phase33_promotion_planner.py
- **Lines:** 231
- **Header:**
```python
"""
System3 Ultra - Phase 33: Ultra Promotion Planner (SAFE, NOT AUTO)

Design a planner that suggests promotions, but does not auto-apply anything.

```

### core\engine\system3_phase340_signal_pipeline_regression_guard.py
- **Lines:** 251
- **Header:**
```python
"""
System3 Phase 340 - Signal Pipeline Regression Guard

Final gate before signal usage - checks for regressions in signal quality.
Compares current metrics against historical baselines.
```

### core\engine\system3_phase341_model_drift_detector_v2.py
- **Lines:** 191
- **Header:**
```python
"""
System3 Phase 341 - Model Drift Detector v2 (Rolling Window)

Quantifies drift between training distribution and recent live data in detail.
Computes per-feature drift scores, overall drift index, and triggers WARN/ALERT flags.
```

### core\engine\system3_phase342_live_performance_estimator.py
- **Lines:** 129
- **Header:**
```python
"""
System3 Phase 342 - Live Prediction Performance Estimator (Paper)

During DRY-RUN, estimates real-time model performance using forward returns and virtual PnL.
Computes hit-rate, average returns, max drawdown, and realized vs predicted metrics.
```

### core\engine\system3_phase343_signals_freshness_enforcer.py
- **Lines:** 139
- **Header:**
```python
"""
System3 Phase 343 - Signals Existence & Freshness Enforcer

Guarantees that angel_index_ai_signals.csv and angel_index_ai_signals_with_forward.csv
always exist and are fresh enough, or forces OP3 into NO-TRADE with clear logs.
```

### core\engine\system3_phase344_pipeline_schema_guard.py
- **Lines:** 120
- **Header:**
```python
"""
System3 Phase 344 - Pipeline Schema Guard (Live CSVs)

Validates that all live CSVs used by the signal/trade pipeline match expected schema.
Detects column mismatches, type issues, and missing required fields.
```

### core\engine\system3_phase345_warn_root_cause_tracker.py
- **Lines:** 102
- **Header:**
```python
"""
System3 Phase 345 - WARN Phase Root-Cause Tracker

Converts generic "Phase XXX: WARN" into structured root-cause reports.
Parses autorun logs and tracks WARN sources with categorized root causes.
```

### core\engine\system3_phase34_ultra_shadow_exec.py
- **Lines:** 175
- **Header:**
```python
"""
System3 Ultra - Phase 34: Ultra Live Shadow Comparison

Run Ultra decisions in shadow, side-by-side with baseline.
Baseline still controls DRY RUN trades.
```

### core\engine\system3_phase35_ultra_auditor.py
- **Lines:** 244
- **Header:**
```python
"""
System3 Ultra - Phase 35: Ultra Decision Auditor

Audit Ultra fused decisions for:
- Over-aggression
```

### core\engine\system3_phase361_signal_pipeline_snapshot.py
- **Lines:** 261
- **Header:**
```python
"""
System3 Phase 361 - Signal Pipeline Snapshot & Quality Summary

Creates a consolidated snapshot of the current signal pipeline state
and writes human-readable report and machine-readable JSON.
```

### core\engine\system3_phase362_forward_calibrator.py
- **Lines:** 250
- **Header:**
```python
"""
System3 Phase 362 - Live Forward-Return Calibrator

Measures real-world predictive strength of signals using forward returns
and produces calibration metrics for thresholds.
```

### core\engine\system3_phase363_model_drift_checker.py
- **Lines:** 336
- **Header:**
```python
"""
System3 Phase 363 - Model Drift Checker

Detects if model behavior has drifted vs recent history by comparing
current signal quality metrics against historical baselines.
```

### core\engine\system3_phase364_health_dashboard_feed.py
- **Lines:** 408
- **Header:**
```python
"""
System3 Phase 364 - Health Dashboard Feed Generator

Aggregates key health metrics from phases 361-363 and system logs
into a single dashboard-ready JSON feed for monitoring tools.
```

### core\engine\system3_phase365_accuracy_tracker.py
- **Lines:** 404
- **Header:**
```python
"""
System3 Phase 365 - Live Accuracy Tracker

Tracks rolling accuracy metrics over time using forward returns and virtual orders.
Provides hit-rate, average gain/loss, per-symbol performance, and time-window stats.
```

### core\engine\system3_phase366_strategy_ensemble_evaluator.py
- **Lines:** 400
- **Header:**
```python
"""
System3 Phase 366 - Strategy Ensemble Evaluator

Evaluates performance of multiple internal strategies (ML, DL, Momentum, Mean-Reversion).
Computes weighted scoring across short-term and long-term windows.
```

### core\engine\system3_phase367_safety_guardrail_recommender.py
- **Lines:** 447
- **Header:**
```python
"""
System3 Phase 367 - Safety Guardrail Recommender

Analyzes volatility regime, signal conflict load, data freshness, and health score.
Recommends additional safety levels (disable trading, reduce trades, cap lot sizes).
```

### core\engine\system3_phase368_broker_latency_monitor.py
- **Lines:** 348
- **Header:**
```python
"""
System3 Phase 368 - Broker Latency Monitor

Measures latency of AngelOne API endpoints WITHOUT placing orders.
Benchmarks: instrument fetch time, feed token refresh, quotes retrieval.
```

### core\engine\system3_phase369_pipeline_profiler.py
- **Lines:** 400
- **Header:**
```python
"""
System3 Phase 369 - Pipeline Profiler

Measures runtime, memory usage, IO cost across entire signal pipeline.
Identifies bottlenecks in curated and forward return processing.
```

### core\engine\system3_phase36_cull_orchestrator.py
- **Lines:** 176
- **Header:**
```python
"""
System3 Ultra - Phase 36: Ultra Continuous Learning Cycle (CULL)

Orchestrator that runs:
- Real data extraction
```

### core\engine\system3_phase370_signal_schema_normalizer.py
- **Lines:** 342
- **Header:**
```python
"""
System3 Phase 370 - Signal Schema Auto-Normalizer

Non-destructively repairs signal CSV files with schema mismatches.
Archives originals with timestamps before any modifications.
```

### core\engine\system3_phase371_signal_duplicate_scanner.py
- **Lines:** 122
- **Header:**
```python
"""
System3 Phase 371 - Signal Duplicate Scanner

Scans cleaned signal files for duplicate and conflicting signals.
Identifies exact duplicates and same-symbol conflicting signals.
```

### core\engine\system3_phase372_signal_conflict_resolver.py
- **Lines:** 120
- **Header:**
```python
"""
System3 Phase 372 - Signal Conflict Resolver

Resolves conflicting signals by keeping most confident/recent signal per symbol.
Creates deduplicated signal files.
```

### core\engine\system3_phase373_signal_clean_curated_builder.py
- **Lines:** 96
- **Header:**
```python
"""
System3 Phase 373 - Clean Signal Curated Builder

Creates final curated signal files from deduplicated data.
Consolidates all data quality improvements into production-ready files.
```

### core\engine\system3_phase374_signal_history_freshness_checker.py
- **Lines:** 109
- **Header:**
```python
"""
System3 Phase 374 - Signal History Freshness Checker

Monitors data freshness and triggers warnings for stale files.
"""
```

### core\engine\system3_phase375_signal_data_quality_summary.py
- **Lines:** 133
- **Header:**
```python
"""
System3 Phase 375 - Signal Data Quality Summary

Comprehensive summary of all data quality phases (370-374).
Reports before/after metrics and quality improvements.
```

### core\engine\system3_phase376_self_test_suite.py
- **Lines:** 414
- **Header:**
```python
"""
System3 Phase 376 - Self-Test Suite

Comprehensive automated testing framework that validates all 375 predecessor phases
and the integrity of the entire System3 pipeline. Executes unit tests, integration
```

### core\engine\system3_phase377_validation_report_generator.py
- **Lines:** 421
- **Header:**
```python
"""
System3 Phase 377 - Validation Report Generator

Comprehensive system-wide validation that analyzes all 15 predecessor phases,
aggregates metrics, validates data integrity, and generates a detailed validation report.
```

### core\engine\system3_phase378_performance_optimizer.py
- **Lines:** 435
- **Header:**
```python
"""
System3 Phase 378 - Performance Optimizer

Analyzes pipeline performance metrics, identifies bottlenecks and optimization
opportunities, and provides actionable recommendations to improve throughput,
```

### core\engine\system3_phase379_edge_case_handler.py
- **Lines:** 420
- **Header:**
```python
"""
System3 Phase 379 - Edge Case Handler

Identifies and handles unusual signal patterns, market conditions, and data
anomalies that might cause unexpected behavior. Provides recommendations for
```

### core\engine\system3_phase37_policy_risk_monitor.py
- **Lines:** 180
- **Header:**
```python
"""
System3 Ultra - Phase 37: Ultra Policy & Risk Monitor

Create a single dashboard-style report summarizing:
- Thresholds
```

### core\engine\system3_phase380_final_sign_off.py
- **Lines:** 510
- **Header:**
```python
"""
System3 Phase 380 - Final Sign-Off

Comprehensive production readiness certification. Validates that all 379 predecessor
phases have executed successfully, consolidates all findings, and provides final
```

### core\engine\system3_phase38_governance_summary.py
- **Lines:** 237
- **Header:**
```python
"""
System3 Ultra - Phase 38: Ultra Governance Summary

Build a "board-level" one-pager summarizing:
- Ultra vs Baseline performance
```

### core\engine\system3_phase39_shadow_campaign.py
- **Lines:** 216
- **Header:**
```python
"""
System3 Ultra - Phase 39: Ultra Shadow Live Campaign Manager

Turn Ultra shadow trading into a structured campaign: run fused decisions + shadow trades
over a configurable window (e.g., whole trading day) and produce a daily summary.
```

### core\engine\system3_phase40_weekly_governance_pack.py
- **Lines:** 281
- **Header:**
```python
"""
System3 Ultra - Phase 40: Weekly Ultra vs Baseline Governance Pack

Aggregate a full week of outputs into one weekly pack for manual review (no automation changes).

```

### core\engine\system3_phase41_promotion_executor.py
- **Lines:** 237
- **Header:**
```python
"""
System3 Ultra - Phase 41: Ultra Promotion Execution Framework (Staging Only)

Provide a safe, two-step mechanism that can prepare promotion of Ultra to baseline,
but does not execute it automatically. This remains a staging step only.
```

### core\engine\system3_phase42_snapshot_manager.py
- **Lines:** 212
- **Header:**
```python
"""
System3 Ultra - Phase 42: Model Snapshot & Rollback Manager

Guarantee we can always roll back: snapshot baseline models + configs before any future
promotion and provide rollback helpers.
```

### core\engine\system3_phase43_env_guard.py
- **Lines:** 244
- **Header:**
```python
"""
System3 Ultra - Phase 43: Environment & Broker Guard

Ensure System3 (Angel indices) never accidentally touches non-Angel brokers and
prepare guardrails for future Binance System3.
```

### core\engine\system3_phase76_geni_self_critique.py
- **Lines:** 309
- **Header:**
```python
"""
System3 Phase 76 - GENI Self-Critique Engine

GENI reviews past signals vs outcomes and creates a self-critique report:
where it was right, wrong, late, or too conservative.
```

### core\engine\system3_phase77_geni_self_correction.py
- **Lines:** 185
- **Header:**
```python
"""
System3 Phase 77 - GENI Self-Correction Engine

Use Phase 76 self-critique to propose concrete corrections (not apply them automatically)
to thresholds and rules.
```

### core\engine\system3_phase78_geni_consensus.py
- **Lines:** 234
- **Header:**
```python
"""
System3 Phase 78 - GENI Multi-Model Consensus Engine

Combine Baseline model, Ultra model, and any heuristic signals into a single
consensus signal per option leg.
```

### core\engine\system3_phase79_adaptive_thresholds.py
- **Lines:** 244
- **Header:**
```python
"""
System3 Phase 79 - Adaptive Threshold Engine

Use volatility/regime features to generate adaptive thresholds per regime
instead of single fixed values.
```

### core\engine\system3_phase80_geni_evolution_status.py
- **Lines:** 211
- **Header:**
```python
"""
System3 Phase 80 - GENI Evolution Status

Create a high-level evolution status overview describing how GENI should evolve
(more aggressive, more conservative, feature focus, etc.).
```

### core\engine\system3_phase81_latency_profiler.py
- **Lines:** 157
- **Header:**
```python
"""
System3 Phase 81 - Micro-Latency Profiler

Measure per-step latency inside live loops: data fetch, feature build,
model inference, trade logic, logging.
```

### core\engine\system3_phase82_job_scheduler.py
- **Lines:** 239
- **Header:**
```python
"""
System3 Phase 82 - Async Job Scheduler

Provide a job scheduler abstraction to run tasks (fetch, train, eval, reports)
in a controlled way.
```

### core\engine\system3_phase83_tick_to_trade_latency.py
- **Lines:** 210
- **Header:**
```python
"""
System3 Phase 83 - Tick-to-Trade Latency Monitor

Measure total real-time latency from market snapshot time to trade decision timestamp.
"""
```

### core\engine\system3_phase84_resource_optimizer.py
- **Lines:** 151
- **Header:**
```python
"""
System3 Phase 84 - Resource Optimizer

Analyze CPU/memory usage logs (if available) and suggest performance optimizations.
"""
```

### core\engine\system3_phase85_heartbeat.py
- **Lines:** 108
- **Header:**
```python
"""
System3 Phase 85 - Heartbeat Engine

Maintain a heartbeat log: System3 alive + status, for monitoring.
"""
```

### core\engine\system3_phase86_position_sizing.py
- **Lines:** 143
- **Header:**
```python
"""
System3 Phase 86 - Position Sizing Engine

Define per-trade position size based on risk rules (max capital % per trade,
volatility, underlying risk).
```

### core\engine\system3_phase87_expected_value.py
- **Lines:** 172
- **Header:**
```python
"""
System3 Phase 87 - Expected Value Calculator

Compute Expected Value (EV) per signal/trade based on historical performance.
"""
```

### core\engine\system3_phase88_portfolio_risk.py
- **Lines:** 213
- **Header:**
```python
"""
System3 Phase 88 - Portfolio Risk Engine

Analyze exposures across underlyings and strikes to detect portfolio-level risk.
"""
```

### core\engine\system3_phase89_optimal_entry.py
- **Lines:** 147
- **Header:**
```python
"""
System3 Phase 89 - Optimal Entry Engine

Assess quality of entry timing for trades.
"""
```

### core\engine\system3_phase90_optimal_exit.py
- **Lines:** 155
- **Header:**
```python
"""
System3 Phase 90 - Optimal Exit Engine

Assess quality of exit logic for trades.
"""
```

### core\engine\system3_phase91_live_dashboard.py
- **Lines:** 222
- **Header:**
```python
"""
System3 Phase 91 - Live Control Dashboard (MD)

Provide a text/MD live dashboard snapshot of System3.
"""
```

### core\engine\system3_phase92_session_replay.py
- **Lines:** 168
- **Header:**
```python
"""
System3 Phase 92 - Session Replay Player

Reconstruct a day's events as a chronological replay log.
"""
```

### core\engine\system3_phase93_operator_override.py
- **Lines:** 200
- **Header:**
```python
"""
System3 Phase 93 - Operator Override Engine

Allow operator to define override rules and log what they would block.
"""
```

### core\engine\system3_phase94_notification_engine.py
- **Lines:** 121
- **Header:**
```python
"""
System3 Phase 94 - Notification Engine

Central notification router, writing events to a log only (no external sends yet).
"""
```

### core\engine\system3_phase95_operator_activity_log.py
- **Lines:** 117
- **Header:**
```python
"""
System3 Phase 95 - Operator Activity Log

Track operator actions in a structured log.
"""
```

### core\engine\system3_phase96_chaos_test.py
- **Lines:** 162
- **Header:**
```python
"""
System3 Phase 96 - Chaos Test Engine

Simulate failures to ensure System3 fails safe (no trades, no corruption).
"""
```

### core\engine\system3_phase97_backup_recovery.py
- **Lines:** 104
- **Header:**
```python
"""
System3 Phase 97 - Backup & Recovery Engine

Create snapshots of key state files for backup.
"""
```

### core\engine\system3_phase98_rollback.py
- **Lines:** 112
- **Header:**
```python
"""
System3 Phase 98 - Rollback Mechanism

Read backup manifest and print rollback plan (dry-run only).
"""
```

### core\engine\system3_phase99_version_freeze.py
- **Lines:** 116
- **Header:**
```python
"""
System3 Phase 99 - Version Freeze & Tagging

Create a version manifest marking current System3 code & config as a named release.
"""
```

### core\engine\system3_phases_331_360_registry.py
- **Lines:** 102
- **Header:**
```python
"""
System3 Phases 331-360 Registry & Integration Module

Registers all new phases for the autorun master.
Provides callable functions and phase metadata.
```

### core\engine\system3_phases_346_350_hardening_pack.py
- **Lines:** 239
- **Header:**
```python
"""
System3 Phases 346-350 - Hardening & Safety Pack

Phase 346: Live Data Integrity Checker
Phase 347: Historical Cache Sanity Check
```

### core\engine\system3_phases_351_360_safety_automation.py
- **Lines:** 389
- **Header:**
```python
"""
System3 Phases 351-360 - Safety & Audit Visibility + Automation

Phase 351: Trading Mode Audit Logger
Phase 352: Risk Limits Snapshot & Enforcement
```

### core\engine\system3_phases_361_380_registry.py
- **Lines:** 123
- **Header:**
```python
"""
System3 Phases 361-380 Registry & Integration Module

Registers all 20 phases in the final implementation block.
Provides callable functions and phase metadata for autorun orchestration.
```

### core\engine\system3_signal_engine.py
- **Lines:** 821
- **Header:**
```python
"""
System3 Signal Engine - Complete signal generation pipeline

Integrates all engines:
- Greeks Engine
```

### core\engine\system3_signal_engine_self_test.py
- **Lines:** 197
- **Header:**
```python
"""
System3 Signal Engine Self-Test

Provides a self-test endpoint for the signal engine that validates:
- Threshold loading
```

### core\engine\system3_threshold_proposer.py
- **Lines:** 309
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Threshold Proposer
Automatically proposes BUY/SELL thresholds based on EV tables from Phase 222.
"""
```

### core\engine\test_angelone_api.py
- **Lines:** 51
- **Header:**
```python
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
```

### core\engine\test_angelone_instruments.py
- **Lines:** 50
- **Header:**
```python
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
```

### core\engine\test_data_pipeline.py
- **Lines:** 30
- **Header:**
```python
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
```

### core\engine\threshold_loader.py
- **Lines:** 403
- **Header:**
```python
"""
System3 Phase 231 - Threshold Loader & Registry

This phase provides a single, robust place to load BUY/SELL thresholds for each underlying.
It reads from storage/meta/system3_threshold_candidates.json (if available) or falls back
```

### core\engine\train_angel_models.py
- **Lines:** 309
- **Header:**
```python
import os
import sys
import json
from datetime import datetime

```

### core\engine\trend_model\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Trend Model - Multi-timeframe trend detection
"""

from .trend_analyzer import compute_trend_features, compute_multi_timeframe_trend
```

### core\engine\trend_model\trend_analyzer.py
- **Lines:** 230
- **Header:**
```python
"""
Trend Analyzer - Compute RSI, MACD, VWAP, SuperTrend, multi-timeframe trends
"""

import numpy as np
```

### core\engine\ultra_feature_engineering.py
- **Lines:** 281
- **Header:**
```python
"""
System3 Ultra - Feature Expander

Extends features from ~25 to ~100 for Ultra models only (shadow).
Does not modify baseline features.
```

### core\engine\ultra_hparam_explorer.py
- **Lines:** 204
- **Header:**
```python
"""
System3 Ultra - Hyperparameter Space Explorer

Offline hyperparameter exploration for Ultra models.
Reports only - no model overwrites.
```

### core\engine\ultra_live_signals_shadow.py
- **Lines:** 232
- **Header:**
```python
"""
System3 Ultra - Ultra Prediction Engine (Shadow Live)

Runs Ultra models in parallel (shadow) with baseline signals for comparison.
Shadow mode only - no trade plans generated.
```

### core\engine\ultra_multi_consensus.py
- **Lines:** 222
- **Header:**
```python
"""
System3 Ultra - Multi-Consensus Engine (Shadow)

Combines predictions from multiple Ultra models & baseline model for analysis.
Shadow mode only - no trade plans generated.
```

### core\engine\ultra_pnl_analyzer.py
- **Lines:** 193
- **Header:**
```python
"""
System3 Ultra - Ultra PnL Analyzer

Advanced analysis of Ultra simulator PnL.
Shadow mode only.
```

### core\engine\ultra_promotion_manager.py
- **Lines:** 230
- **Header:**
```python
"""
System3 Ultra - Ultra Promotion System (Compare & Promote)

Side-by-side comparison of Baseline vs Ultra models, and manual promotion only.
Respects safety switches - no auto-promotion.
```

### core\engine\ultra_regime_classifier.py
- **Lines:** 178
- **Header:**
```python
"""
System3 Ultra - Risk Regime Classifier

Classifies market regimes (low/medium/high volatility, trending vs ranging).
Adds regime labels to Ultra training data.
```

### core\engine\ultra_safety.py
- **Lines:** 74
- **Header:**
```python
"""
System3 Ultra Safety Switches

Central safety control for Ultra-Mode features.
All auto-features disabled by default.
```

### core\engine\ultra_shadow_data_engine.py
- **Lines:** 427
- **Header:**
```python
"""
System3 Ultra - Shadow Real-Data Engine V1

Builds shadow learning datasets for Ultra profile using real signals, trade plans, PnL logs, outcomes.
All operations are shadow/experimental only - no changes to baseline.
```

### core\engine\ultra_threshold_lab.py
- **Lines:** 171
- **Header:**
```python
"""
System3 Ultra - Threshold Lab V2 (Shadow Only)

Experiments thresholds on shadow PnL without changing real configs.
Grid search analysis only.
```

### core\engine\ultra_trade_simulator.py
- **Lines:** 240
- **Header:**
```python
"""
System3 Ultra - Trade Simulator (Shadow, Offline)

Simulates Ultra-only trades on historical snapshots, offline.
Shadow mode only - no real trades.
```

### core\engine\ultra_train_models.py
- **Lines:** 269
- **Header:**
```python
"""
System3 Ultra - Shadow Model Trainer V3

Trains Ultra shadow models separate from baseline.
Uses Ultra training dataset with extended features.
```

### core\engine\volatility_model\__init__.py
- **Lines:** 8
- **Header:**
```python
"""
Volatility Model - IV, IV percentile, IV rank, volatility regime detection
"""

from .volatility_analyzer import compute_volatility_features, detect_volatility_regime
```

### core\engine\volatility_model\volatility_analyzer.py
- **Lines:** 204
- **Header:**
```python
"""
Volatility Analyzer - Compute IV, IVP, IVR, volatility regimes
"""

import numpy as np
```

### core\execution\__init__.py
- **Lines:** 4
- **Header:**
```python
"""
System3 Execution Module - Virtual Order Execution
"""

```

### core\execution\live_execution_engine.py
- **Lines:** 253
- **Header:**
```python
"""
System3 Phase 236 - Virtual Execution Engine

Convert signals + thresholds into virtual orders and log them.
"""
```

### core\execution\order_models.py
- **Lines:** 35
- **Header:**
```python
"""
System3 Phase 233 - Virtual Order Models

Define structured Python models for planned orders and risk decisions.
"""
```

### core\execution\risk_guard.py
- **Lines:** 225
- **Header:**
```python
"""
System3 Phase 235 - Risk Guard Core

Central risk checks for virtual orders (no real API).
"""
```

### core\geni\__init__.py
- **Lines:** 20
- **Header:**
```python
"""
System3 GENI Ultra Master Agent

GENI (Genesis Intelligence) - High-level orchestration and validation layer
for System3 Ultra operations.
```

### core\geni\geni_config.py
- **Lines:** 86
- **Header:**
```python
"""
System3 GENI - Configuration Module

Provides path helpers and safety flags.
All paths are relative to project root.
```

### core\geni\geni_orchestrator.py
- **Lines:** 269
- **Header:**
```python
"""
System3 GENI - Orchestrator

High-level coordinator for GENI operations.
"""
```

### core\geni\geni_state.py
- **Lines:** 96
- **Header:**
```python
"""
System3 GENI - State Management

Manages high-level GENI system state persistence.
"""
```

### core\geni\geni_tasks.py
- **Lines:** 100
- **Header:**
```python
"""
System3 GENI - Task Registry

Defines high-level tasks that GENI can orchestrate.
Tasks reference existing scripts and validators.
```

### core\geni\geni_validator.py
- **Lines:** 289
- **Header:**
```python
"""
System3 GENI - Validation Helpers

Runs validation routines and parses results.
"""
```

### core\models\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\monitoring\__init__.py
- **Lines:** 4
- **Header:**
```python
"""
System3 Monitoring Module - Alerts and Monitoring
"""

```

### core\monitoring\alert_hooks.py
- **Lines:** 37
- **Header:**
```python
"""
System3 Phase 242 - Alert Hooks (Log-Only)

Prepare a minimal alert hook (log-only, no external calls).
"""
```

### core\tools\__init__.py
- **Lines:** 4
- **Header:**
```python
"""
System3 Tools Module
"""

```

### core\tools\clean_angel_signals_csv.py
- **Lines:** 420
- **Header:**
```python
"""
System3 CSV Cleaning Module

Automated cleaning pipeline for angel_index_ai_signals_with_forward.csv
Produces clean and EV-ready versions of the CSV file.
```

### core\tools\schema_audit.py
- **Lines:** 286
- **Header:**
```python
"""
System3 CSV Schema Audit Module

Performs schema audit and generates documentation for angel_index_ai_signals_with_forward.csv
"""
```

### core\tools\system3_auto_test_generator.py
- **Lines:** 658
- **Header:**
```python
"""
System3 Auto-Test Generator

Automatically generates test files for phases based on registry and specifications.
"""
```

### core\tools\system3_history_cleaner.py
- **Lines:** 202
- **Header:**
```python
"""
System3 history cleaner - remove malformed CSV rows with wrong column counts.

This module is intentionally lightweight and uses only the Python standard
library (csv, os, glob, datetime, pathlib) so it can be reused from
```

### core\tools\validate_clean_csv.py
- **Lines:** 382
- **Header:**
```python
"""
System3 Clean CSV Validation Module

Validates the cleaned CSV file and generates validation report.
"""
```

### core\ultra\__init__.py
- **Lines:** 20
- **Header:**
```python
"""
System3 Ultra - Phases 21-30: Risk-Adaptive Intelligence

All modules are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.
```

### core\ultra\phase21_adaptive_risk_engine.py
- **Lines:** 263
- **Header:**
```python
"""
System3 Ultra - Phase 21: Adaptive Risk Engine (ARE)

System3 learns to select risk level dynamically based on:
- Volatility
```

### core\ultra\phase22_position_sizing.py
- **Lines:** 160
- **Header:**
```python
"""
System3 Ultra - Phase 22: Dynamic Position Sizing Engine

Decide quantity dynamically based on:
- Risk level
```

### core\ultra\phase23_volatility_impact.py
- **Lines:** 219
- **Header:**
```python
"""
System3 Ultra - Phase 23: Volatility Regime Impact Engine

Understand how volatility affects decisions.
Classifies volatility regimes and computes impact factors.
```

### core\ultra\phase24_confidence_drift.py
- **Lines:** 223
- **Header:**
```python
"""
System3 Ultra - Phase 24: Confidence Drift Analyzer

Track how model confidence changes over time.
Detects upward, downward, or stable drift patterns.
```

### core\ultra\phase25_stoploss_engine.py
- **Lines:** 161
- **Header:**
```python
"""
System3 Ultra - Phase 25: Adaptive Stoploss Engine (ASE)

Dynamic stoploss based on:
- Volatility
```

### core\ultra\phase26_target_engine.py
- **Lines:** 136
- **Header:**
```python
"""
System3 Ultra - Phase 26: Adaptive Target Engine (ATE)

Compute dynamic target percentage based on:
- Risk level
```

### core\ultra\phase27_rr_balancer.py
- **Lines:** 164
- **Header:**
```python
"""
System3 Ultra - Phase 27: Risk-Reward Balancer

Balance SL/TP dynamically for optimized risk-reward ratio.
Combines results from Adaptive Stoploss Engine (ASE) and Adaptive Target Engine (ATE).
```

### core\ultra\phase28_auto_corrector.py
- **Lines:** 229
- **Header:**
```python
"""
System3 Ultra - Phase 28: Failure-Mode Auto-Corrector

Detect repeated misfires & recommend corrections.
Analyzes last 300 outcomes, clusters misfires, detects patterns.
```

### core\ultra\phase29_sensitivity.py
- **Lines:** 231
- **Header:**
```python
"""
System3 Ultra - Phase 29: Sensitivity Analyzer

Check how sensitive predictions are to inputs.
Perturbs features ±1–5% and measures confidence changes.
```

### core\ultra\phase30_calibration_engine.py
- **Lines:** 231
- **Header:**
```python
"""
System3 Ultra - Phase 30: Real-Time Calibration Engine (RTCE)

Live recalibration of:
- Risk level
```

### core\ultra\phase46_meta_fusion.py
- **Lines:** 222
- **Header:**
```python
"""
System3 Ultra - Phase 46: Ultra Meta Fusion Model

Combine predictions from multiple Ultra models into a single meta-prediction
using weighted fusion based on historical accuracy.
```

### core\ultra\phase47_confidence_vector.py
- **Lines:** 225
- **Header:**
```python
"""
System3 Ultra - Phase 47: 7D Confidence Vector Engine

Track confidence trends over 7-day rolling window.
Detect confidence patterns and generate trajectory predictions.
```

### core\ultra\phase48_error_scanner.py
- **Lines:** 232
- **Header:**
```python
"""
System3 Ultra - Phase 48: Real Market Error Scanner

Scan for discrepancies between predictions and actual market behavior.
Identify systematic errors and classify error types.
```

### core\ultra\phase49_risk_regulator.py
- **Lines:** 233
- **Header:**
```python
"""
System3 Ultra - Phase 49: Smart Risk Regulator (AI Suggestions Only)

AI-powered risk adjustment suggestions.
Read-only, no auto-apply. All suggestions must be manually reviewed.
```

### core\ultra\phase50_prediction_explainer.py
- **Lines:** 218
- **Header:**
```python
"""
System3 Ultra - Phase 50: Ultra Prediction Explainer

Explain why Ultra made specific predictions (interpretability).
Compute feature importance and generate explanation text.
```

### core\ultra\phase51_probability_engine.py
- **Lines:** 246
- **Header:**
```python
"""
System3 Ultra - Phase 51: Real-Time Probability Engine

Compute real-time probability distributions for outcomes.
Generate probability forecasts and track changes over time.
```

### core\ultra\phase52_multi_broker.py
- **Lines:** 167
- **Header:**
```python
"""
System3 Ultra - Phase 52: Multi-Broker Abstraction (Shadow-Only)

Abstract broker interface for future multi-broker support.
Shadow-only, no real connections or API calls.
```

### core\ultra\phase53_monitoring_agent.py
- **Lines:** 218
- **Header:**
```python
"""
System3 Ultra - Phase 53: Ultra Monitoring AI Agent

AI agent that monitors system health and suggests actions.
Read-only, no auto-actions. All suggestions require manual review.
```

### core\ultra\phase54_back_reconstruction.py
- **Lines:** 201
- **Header:**
```python
"""
System3 Ultra - Phase 54: Real Outcome Back-Reconstruction

Reconstruct what should have happened based on actual outcomes.
Compare actual vs optimal decisions and generate "what-if" analysis.
```

### core\ultra\phase55_intelligence_dashboard.py
- **Lines:** 269
- **Header:**
```python
"""
System3 Ultra - Phase 55: Ultra Intelligence Dashboard

Comprehensive dashboard combining all Ultra intelligence.
Aggregates metrics from all phases and generates unified view.
```

### core\utils\__init__.py
- **Lines:** 0
- **Header:**
```python
```

### core\utils\config_loader.py
- **Lines:** 29
- **Header:**
```python
import json
import os

CONFIG_FILE = "config/system3_config.json"

```

### core\utils\env_loader.py
- **Lines:** 22
- **Header:**
```python
import os
from dotenv import load_dotenv

# Project root: .../Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
```

### core\utils\env_manager.py
- **Lines:** 23
- **Header:**
```python
from core.utils.config_loader import ensure_config
from core.utils.logger import logger

class EnvManager:

```

### core\utils\helpers.py
- **Lines:** 9
- **Header:**
```python
import os
from datetime import datetime

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

### core\utils\http_client.py
- **Lines:** 16
- **Header:**
```python
import requests
from core.utils.logger import logger


class HttpClient:
```

### core\utils\logger.py
- **Lines:** 24
- **Header:**
```python
import logging
import os
from datetime import datetime

LOG_DIR = "logs"
```

### core\validation\__init__.py
- **Lines:** 6
- **Header:**
```python
"""
System3 Validation Module

Provides reliability and safety checks for thresholds and signal pipeline.
"""
```

### core\validation\live_safety_guard.py
- **Lines:** 248
- **Header:**
```python
"""
System3 Live Runtime Safety Guard

Provides hard safety limits and logging for live signal generation.
Tracks signal rates, position limits, and logs safety trips.
```

### core\validation\post_close_signal_audit.py
- **Lines:** 471
- **Header:**
```python
"""
System3 Post-Close Signal Consistency Audit

Verifies that logged signals are consistent with thresholds and scores.
Performs daily diagnostics and anomaly detection.
```

### core\validation\pre_market_signal_dryrun.py
- **Lines:** 488
- **Header:**
```python
"""
System3 Pre-Market Signal Dry-Run

Performs a dry-run signal generation using today's latest prepared live-features file.
Applies live thresholds and performs safety checks before market opens.
```

### core\validation\validate_live_thresholds.py
- **Lines:** 397
- **Header:**
```python
"""
System3 Static Threshold Sanity Check

Validates live thresholds JSON structure and verifies signal counts match expectations.
This is a pre-market check to ensure thresholds are safe before market opens.
```

### create_yaml_configs.py
- **Lines:** 175
- **Header:**
```python
#!/usr/bin/env python3
"""
Create YAML Configuration Files for Phase 313

Creates the YAML config files that Phase 313 expects:
```

### deep_analyze_verification_results.py
- **Lines:** 522
- **Header:**
```python
"""
Deep Analysis of Multi-Verification Results
Identifies all issues, warnings, and potential problems
"""

```

### enforce_pnl_log_schema.py
- **Lines:** 65
- **Header:**
```python
#!/usr/bin/env python3
"""
Production-grade schema enforcement for angel_index_ai_pnl_log.csv.
- Ensures file exists with required columns
- Adds any missing required columns with safe default values
```

### evaluate_phase249_models.py
- **Lines:** 340
- **Header:**
```python
"""
Phase 249 Extended: Model Evaluation & Accuracy Validation Script

Purpose:
  - Reload all trained Phase 249 LSTM models from disk (.pth files)
```

### final_sanity_check.py
- **Lines:** 219
- **Header:**
```python
#!/usr/bin/env python3
"""
Final Sanity Check for System3 Repository
Checks:
1. All CSV readers use safe loading
```

### final_system_validation_test.py
- **Lines:** 302
- **Header:**
```python
#!/usr/bin/env python3
"""
Final comprehensive System3 validation and test suite
Tests all critical components and generates detailed results
"""
```

### find_missing_phases.py
- **Lines:** 129
- **Header:**
```python
"""
Find Missing Phases - Micro Investigation

Identifies exactly which 26 phases are missing from the registry.
"""
```

### fix_phase315_csv_schema.py
- **Lines:** 93
- **Header:**
```python
#!/usr/bin/env python3
"""
Fix Phase 315 CSV Schema Issues

Adds missing 'symbol' column to angel_index_ai_pnl_log.csv
```

### fix_phase367_emojis.py
- **Lines:** 20
- **Header:**
```python
#!/usr/bin/env python
"""Fix remaining emojis and issues in phases"""

import sys

```

### fix_phase368_emojis.py
- **Lines:** 28
- **Header:**
```python
#!/usr/bin/env python
"""Fix emojis in phase 368"""

with open('c:\\Genesis_System3\\core\\engine\\system3_phase368_broker_latency_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()
```

### generate_phase_1_200_reports.py
- **Lines:** 770
- **Header:**
```python
#!/usr/bin/env python3
"""
SYSTEM3 PHASES 1-200 COMPREHENSIVE REPORT GENERATOR
Generates 5 required audit reports from diagnostic data.
"""
```

### generate_phases_316_330.py
- **Lines:** 156
- **Header:**
```python
"""
Batch Phase Generator for Phases 316-330
Creates all remaining phase implementations efficiently
"""

```

### generate_phases_366_369_status.py
- **Lines:** 113
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Phases 366-369 Implementation Status Report
"""

```

### multi_verify_all.py
- **Lines:** 490
- **Header:**
```python
"""
MULTI-LEVEL VERIFICATION - Complete System3 CSV Fixes & Warnings Check
"""

import sys
```

### rebuild_complete_signals.py
- **Lines:** 505
- **Header:**
```python
"""
System3 - Complete Signal Rebuild Pipeline

Rebuilds angel_index_ai_signals.csv with ALL required feature columns:
- Greeks: delta, gamma, theta, vega
```

### rebuild_phase_registry_complete.py
- **Lines:** 93
- **Header:**
```python
#!/usr/bin/env python3
"""
Production-grade phase registry rebuild.
- Scans core/engine for all system3_phase*.py files
- Detects run_phaseXXX callables when present
```

### run_all_fixes.py
- **Lines:** 108
- **Header:**
```python
#!/usr/bin/env python3
"""
Master Fix Script for Phases 311-330

Runs all fixes to optimize test results:
```

### run_full_verification_checklist.py
- **Lines:** 324
- **Header:**
```python
"""
System3 Full Verification Checklist Runner

Runs all verification commands from the validation master document
and generates a comprehensive report.
```

### run_phase221_222.py
- **Lines:** 39
- **Header:**
```python
#!/usr/bin/env python3
"""Run Phase 221 and 222 to generate forward returns and EV tables."""

import sys
from pathlib import Path
```

### run_phase222_on_clean_data.py
- **Lines:** 100
- **Header:**
```python
"""
Run Phase 222 (Signal Edge Analysis) on Clean EV-Ready CSV

This script runs Phase 222 using the cleaned EV-ready CSV instead of the raw CSV.
"""
```

### run_phase223_on_clean_data.py
- **Lines:** 77
- **Header:**
```python
"""
Run Phase 223 (Threshold Optimizer) on Clean EV-Ready CSV

This script runs Phase 223 using the cleaned EV-ready CSV instead of the raw CSV.
"""
```

### run_phases_301_310_test.py
- **Lines:** 263
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Phases 301-310 Test Runner
Runs all phases 301-310 in test/analysis mode and collects results.
"""
```

### run_system3.py
- **Lines:** 1017
- **Header:**
```python
﻿from core.engine.train_angel_models import main as train_angel_models_main
from core.engine.build_angel_training_dataset import main as build_angel_training_main

import sys
import os
```

### run_threshold_proposer_on_clean_ev.py
- **Lines:** 38
- **Header:**
```python
"""
Run Threshold Proposer on Clean EV Tables from Phase 222

This script runs the threshold proposer which uses EV tables to propose optimal thresholds.
"""
```

### run_validation_report.py
- **Lines:** 129
- **Header:**
```python
"""
System3 Post-Validation Report Generator
Comprehensive validation of all priorities completed
"""

```

### split_system3_report.py
- **Lines:** 141
- **Header:**
```python
# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

### strict_verify_system3.py
- **Lines:** 314
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Strict Verification Script
Executes all commands with full Python path and strict error detection.
"""
```

### system3_auto_heal_scheduler.py
- **Lines:** 202
- **Header:**
```python
"""
System3 Auto-Heal Scheduler

Runs auto-heal orchestrator on a schedule:
- Every 10 minutes during market hours (9:15 AM - 3:30 PM)
```

### system3_autorun_master.py
- **Lines:** 686
- **Header:**
```python
"""
System3 Autorun Master - HARDENED VERSION
Full-Day Autonomous Automation with Enhanced Safety & Self-Healing

This script orchestrates a complete trading day:
```

### system3_autorun_master_hardened.py
- **Lines:** 588
- **Header:**
```python
"""
System3 Autorun Master - HARDENED VERSION
Full-Day Autonomous Automation with Enhanced Safety & Self-Healing

This script orchestrates a complete trading day:
```

### system3_complete_orchestrator.py
- **Lines:** 321
- **Header:**
```python
"""
System3 Complete Orchestrator - THE ULTIMATE MASTER

Handles ALL phases (1-∞) across all tiers:
- Tier 1: Core/Baseline (1-200) - Integrated in signal engine
```

### system3_comprehensive_validation.py
- **Lines:** 533
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Comprehensive Deep Analysis & Multi-Validation
- Analyzes all MD files
- Validates all phases
```

### system3_csv_cleanup_fix.py
- **Lines:** 128
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 CSV Cleanup and Fix Script
Removes duplicate headers and fixes data quality issues
"""
```

### system3_csv_deep_validation.py
- **Lines:** 591
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 CSV Deep Validation - Data Quality & Quant Analysis
Comprehensive validation of angel_index_ai_signals_with_forward.csv
"""
```

### system3_csv_ultra_audit.py
- **Lines:** 376
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 CSV Ultra Audit - Comprehensive Quality Control
Analyzes angel_index_ai_signals_with_forward.csv in extreme detail
"""
```

### system3_debug_signals_pipeline.py
- **Lines:** 216
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Debug Signals Pipeline - STEP 5 Health Script

Quick signal pipeline diagnostic tool.
```

### system3_dynamic_phase_controller.py
- **Lines:** 430
- **Header:**
```python
"""
System3 Dynamic Phase Controller - FUTURE-PROOF PHASE EXECUTION

Automatically discovers and executes ALL phases (1-∞) without hardcoding.
This controller dynamically loads phases from the phase registry and executes them.
```

### system3_edge_by_score_bucket_tracker.py
- **Lines:** 118
- **Header:**
```python
"""
System3 Phase 247 - Edge-by-Score-Bucket Tracker
"""

import sys
```

### system3_forensic_verification.py
- **Lines:** 426
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Full Forensic Verification
Analyzes logs, JSON files, CSV files, and codebase to determine:
- What happened when laptop was closed
```

### system3_full_forensic.py
- **Lines:** 91
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Full Forensic Verification - Complete 7-Step Analysis
"""

```

### system3_full_inspector.py
- **Lines:** 362
- **Header:**
```python
﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYSTEM3 FULL INSPECTION SCRIPT
 
```

### system3_generate_tests.py
- **Lines:** 19
- **Header:**
```python
"""
Convenience script to run the System3 Auto-Test Generator.

Usage:
    python system3_generate_tests.py
```

### system3_geni_master.py
- **Lines:** 76
- **Header:**
```python
"""
System3 GENI Ultra Master Agent

High-level orchestration and validation entry point.
All operations are SAFE MODE - no real trades, no auto-promotion.
```

### system3_inspect_training_data.py
- **Lines:** 86
- **Header:**
```python
"""
System3 training data inspector.

DRY-RUN only: inspects curated/live training CSVs used by the ML predictor.
"""
```

### system3_live_day_autopilot.py
- **Lines:** 572
- **Header:**
```python
"""
System3 Live Day Autopilot - Single-Button Full-Day Autopilot

This script orchestrates a complete trading day:
- OP1: Pre-market checks
```

### system3_magic_folder_report.py
- **Lines:** 386
- **Header:**
```python
﻿import os
import sys
import hashlib
import datetime
from pathlib import Path
```

### system3_master_inspector.py
- **Lines:** 479
- **Header:**
```python
"""
System3 Master Inspector - READ-ONLY Diagnostic Tool
====================================================

This script performs comprehensive READ-ONLY inspection of System3 project.
```

### system3_phase250_255_pipeline_test.py
- **Lines:** 205
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Phase 250-255 Pipeline End-to-End Test

Validates the complete Phase 250 → 251 → 252 pipeline:
```

### system3_phase331_signal_integrity.py
- **Lines:** 59
- **Header:**
```python
import os
import pandas as pd
import logging
from datetime import datetime

```

### system3_phase_201_230_diagnostics.py
- **Lines:** 132
- **Header:**
```python
"""
System3 Phases 201-230 Diagnostics Script

Runs all phases 201-230 in test mode and prints summary.
"""
```

### system3_phase_231_260_diagnostics.py
- **Lines:** 394
- **Header:**
```python
"""
System3 Phases 231-260 Diagnostics Script

Runs all phases 231-260 in test mode and prints summary.
"""
```

### system3_phase_261_300_diagnostics.py
- **Lines:** 104
- **Header:**
```python
"""
System3 Phases 261-300 Diagnostics Script

Runs all phases 261-300 in test mode and prints summary.
"""
```

### system3_phase_331_340_diagnostics.py
- **Lines:** 33
- **Header:**
```python
"""
System3 Phases 331-340 Diagnostics Module

Provides phase imports for autorun master integration.
"""
```

### system3_phase_registry_builder.py
- **Lines:** 309
- **Header:**
```python
"""
System3 Phase Registry Builder

Scans docs and code to build a comprehensive phase registry.
Follows System3 MASTER AGENT INSTRUCTION pattern.
```

### system3_phases_301_310_diagnostics.py
- **Lines:** 116
- **Header:**
```python
"""
System3 Phases 301-310 Diagnostics Script

Runs all phases 301-310 in test mode and prints summary.
"""
```

### system3_pre_autorun_validation.py
- **Lines:** 603
- **Header:**
```python
"""
System3 Pre-Autorun Validation & Hardening Script

Performs comprehensive validation before relying on START_AUTORUN_AND_WATCHDOG.bat
Completes Phases A-E as specified in the validation request.
```

### system3_preflight_check.py
- **Lines:** 461
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Pre-Flight Check
Comprehensive validation before starting autorun.
"""
```

### system3_premarket_checklist.py
- **Lines:** 723
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Pre-Market Checklist
Comprehensive 20-point validation with auto-diagnosis and repair.
"""
```

### system3_premarket_health_check.py
- **Lines:** 489
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Pre-Market Health Check
Comprehensive health check to run before market open.

```

### system3_premarket_validator.py
- **Lines:** 188
- **Header:**
```python
#!/usr/bin/env python
"""
System3 Pre-Market Validator
Comprehensive check before tomorrow's market open
"""
```

### system3_prep_for_new_day.py
- **Lines:** 192
- **Header:**
```python
import os
from pathlib import Path
from datetime import datetime
import shutil
from typing import List
```

### system3_score_to_trade_attribution.py
- **Lines:** 107
- **Header:**
```python
"""
System3 Phase 244 - Score-to-Trade Attribution Report
"""

import sys
```

### system3_session_diagnostic_20251204.py
- **Lines:** 139
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Session Diagnostic - December 4, 2025
Analyzes today's market session to identify issues.
"""
```

### system3_signal_test_mode.py
- **Lines:** 384
- **Header:**
```python
"""
System3 Signal Test Mode - DRY-RUN analysis of recent signals.

Reads recent rows from storage/live/angel_index_ai_signals.csv and reports:
- Distribution of component scores (trend/volatility/momentum/ai/final)
```

### system3_startup_verification.py
- **Lines:** 129
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Startup Verification
Quick check before starting autorun to ensure everything is ready.
"""
```

### system3_symbol_participation_summary.py
- **Lines:** 98
- **Header:**
```python
"""
System3 Phase 245 - Symbol Participation Summary
"""

import sys
```

### system3_threshold_evolution_tracker.py
- **Lines:** 130
- **Header:**
```python
"""
System3 Phase 243 - Threshold Evolution Tracker

Track how thresholds change over time.
"""
```

### system3_trade_density_vs_regime.py
- **Lines:** 91
- **Header:**
```python
"""
System3 Phase 246 - Trade Density vs Volatility Regime
"""

import sys
```

### system3_ultimate_ai_controller.py
- **Lines:** 576
- **Header:**
```python
"""
System3 Ultimate AI Controller - PRODUCTION HARDENED VERSION

The most advanced autonomous system controller with complete resilience:
- Network disconnection handling
```

### system3_ultimate_heartbeat_manager.py
- **Lines:** 557
- **Header:**
```python
"""
Ultimate Heartbeat Manager - Comprehensive System Status Tracking

Updates system3_daily_heartbeat.json with complete system metrics.
Integrates with Ultimate AI Controller and all subsystems.
```

### system3_ultra.py
- **Lines:** 740
- **Header:**
```python
"""
System3 Ultra Control Panel

Master entry point for all System3 operations (baseline + ultra).
Provides unified menu interface with 100+ options organized into logical sections.
```

### system3_ultra_daily_runner.py
- **Lines:** 156
- **Header:**
```python
"""
System3 Ultra Daily Runner

Runs daily operational phases automatically:
- OP1: Pre-Market Diagnostic
```

### system3_ultra_micro_documentation_generator.py
- **Lines:** 529
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Ultra Micro Documentation Generator
Creates comprehensive, ultra-detailed documentation for the entire project and all phases.
"""
```

### system3_ultra_runtime_loops.py
- **Lines:** 244
- **Header:**
```python
"""
System3 Ultra Runtime Loops

Provides continuous runtime loops for:
- Live signal generation
```

### system3_ultra_validation.py
- **Lines:** 349
- **Header:**
```python
"""
System3 Ultra Control Panel - Validation Engine

Validates 30+ conditions:
- File-level validation
```

### system3_ultra_weekly_runner.py
- **Lines:** 190
- **Header:**
```python
"""
System3 Ultra Weekly Runner

Runs weekly operational phases automatically:
- OP5: Weekly Governance Review
```

### system3_universal_autophase_engine.py
- **Lines:** 1019
- **Header:**
```python
"""
System3 Universal Auto-Phase Engine (1-∞)

Automatically detects, validates, implements, repairs, upgrades, and future-proofs
ALL PHASES from 1 to infinity.
```

### system3_virtual_orders_schema_check.py
- **Lines:** 135
- **Header:**
```python
"""
System3 Phase 238 - Virtual Orders Schema Guard

Ensure angel_virtual_orders.csv is consistent and well-formed.
"""
```

### system3_virtual_trades_diagnostics.py
- **Lines:** 128
- **Header:**
```python
"""
System3 Phase 241 - Virtual Trade Diagnostics & Sanity Checks
"""

import sys
```

### system3_virtual_trades_enrichment.py
- **Lines:** 152
- **Header:**
```python
"""
System3 Phase 239 - Virtual PnL Joiner

Join virtual trades with forward returns to measure edge.
"""
```

### system3_virtual_trades_summary.py
- **Lines:** 207
- **Header:**
```python
"""
System3 Phase 240 - Virtual PnL Daily Report

Produce daily PnL summaries by underlying and overall.
"""
```

### system3_watchdog.py
- **Lines:** 273
- **Header:**
```python
"""
System3 Watchdog - HARDENED VERSION
Monitors and Restarts Autorun Master with Enhanced Safety Checks

Checks if system3_autorun_master.py is running every 60 seconds.
```

### system3_watchdog_hardened.py
- **Lines:** 270
- **Header:**
```python
"""
System3 Watchdog - HARDENED VERSION
Monitors and Restarts Autorun Master with Enhanced Safety Checks

Checks if system3_autorun_master.py is running every 60 seconds.
```

### test_auto_heal_comprehensive.py
- **Lines:** 347
- **Header:**
```python
"""
System3 Auto-Heal Comprehensive Test Suite

Tests all auto-healing functionality:
- Stale data detection and recovery
```

### test_autorun_integration.py
- **Lines:** 391
- **Header:**
```python
"""
System3 Autorun Integration Test Suite

Tests START_AUTORUN_AND_WATCHDOG.bat integration with all safety checks
in various scenarios.
```

### test_csv_parsing_fixes.py
- **Lines:** 174
- **Header:**
```python
"""
Test Script to Verify CSV Parsing Fixes
Tests all 3 fixed files to ensure they handle malformed CSV lines gracefully
"""

```

### test_dynamic_phase_controller.py
- **Lines:** 190
- **Header:**
```python
"""
Test Dynamic Phase Controller - Verify Future-Proof Phase Execution

Tests the dynamic phase controller to ensure it can:
1. Load phases from registry
```

### test_heartbeat_schema.py
- **Lines:** 34
- **Header:**
```python
#!/usr/bin/env python3
"""
Schema guard for system3_daily_heartbeat.json
Ensures required sections are present and version is 2.0.0.
Run standalone or via test runner.
```

### test_phases_261_300.py
- **Lines:** 79
- **Header:**
```python
"""
Test script for phases 261-300
Verifies that all phases can be imported and run without errors.
"""

```

### test_phases_311_330.py
- **Lines:** 98
- **Header:**
```python
"""
Test Phases 311-330 Implementation
Quick validation of all new phases
"""

```

### test_phases_31_38.py
- **Lines:** 280
- **Header:**
```python
"""
Test script for Phases 31-38
Run this to test all phases sequentially and verify outputs.
"""

```

### test_phases_331_340.py
- **Lines:** 101
- **Header:**
```python
"""
Test Phases 331-340 Implementation

Validates all new phases are working correctly.
"""
```

### test_phases_361_380_full_block.py
- **Lines:** 89
- **Header:**
```python
"""
Full block test for all 20 phases (361-380)
"""

import sys
```

### test_phases_361_380_full_integration.py
- **Lines:** 145
- **Header:**
```python
"""
Full integration test for phases 361-380 registry and autorun master.
Tests all 15 implemented phases in sequence.
"""

```

### test_phases_366_369.py
- **Lines:** 89
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Phases 366-369 Block Test
Tests all new phases for execution integrity
"""
```

### test_phases_39_45.py
- **Lines:** 170
- **Header:**
```python
"""
System3 Ultra Phases 39-45: Verification Test Suite

Run this script to verify all phases are working correctly.
"""
```

### test_phases_46_55.py
- **Lines:** 82
- **Header:**
```python
"""
Test script for Phases 46-55
Runs dry-run tests for all new Ultra phases.
"""

```

### test_phases_76_100.py
- **Lines:** 164
- **Header:**
```python
"""
System3 Phases 76-100 - Complete Test Suite

Runs all 25 phases (76-100) and validates outputs.
"""
```

### test_smartapi_login.py
- **Lines:** 15
- **Header:**
```python

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
```

### test_system3_signal_engine.py
- **Lines:** 151
- **Header:**
```python
"""
Test Script for System3 Signal Engine

Tests all components and verifies non-zero scores.
"""
```

### test_ultimate_ai_controller.py
- **Lines:** 147
- **Header:**
```python
"""
Test Suite for Ultimate AI Controller

Comprehensive testing of all AI Controller functionality.
"""
```

### tests\auto\system3_generated_tests\test_phase_021.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 21

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase21_adaptive_risk_engine
```

### tests\auto\system3_generated_tests\test_phase_022.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 22

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase22_position_sizing
```

### tests\auto\system3_generated_tests\test_phase_023.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 23

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase23_volatility_impact
```

### tests\auto\system3_generated_tests\test_phase_024.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 24

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase24_confidence_drift
```

### tests\auto\system3_generated_tests\test_phase_025.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 25

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase25_stoploss_engine
```

### tests\auto\system3_generated_tests\test_phase_026.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 26

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase26_target_engine
```

### tests\auto\system3_generated_tests\test_phase_027.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 27

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase27_rr_balancer
```

### tests\auto\system3_generated_tests\test_phase_028.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 28

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase28_auto_corrector
```

### tests\auto\system3_generated_tests\test_phase_029.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 29

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase29_sensitivity
```

### tests\auto\system3_generated_tests\test_phase_030.py
- **Lines:** 245
- **Header:**
```python
"""
Auto-generated test for System3 Phase 30

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase30_calibration_engine
```

### tests\auto\system3_generated_tests\test_phase_031.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 31

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase31_ultra_fusion
```

### tests\auto\system3_generated_tests\test_phase_032.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 32

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase32_ultra_vs_baseline
```

### tests\auto\system3_generated_tests\test_phase_033.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 33

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase33_promotion_planner
```

### tests\auto\system3_generated_tests\test_phase_034.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 34

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase34_ultra_shadow_exec
```

### tests\auto\system3_generated_tests\test_phase_035.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 35

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase35_ultra_auditor
```

### tests\auto\system3_generated_tests\test_phase_036.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 36

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase36_cull_orchestrator
```

### tests\auto\system3_generated_tests\test_phase_037.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 37

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase37_policy_risk_monitor
```

### tests\auto\system3_generated_tests\test_phase_038.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 38

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase38_governance_summary
```

### tests\auto\system3_generated_tests\test_phase_039.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 39

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase39_shadow_campaign
```

### tests\auto\system3_generated_tests\test_phase_040.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 40

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase40_weekly_governance_pack
```

### tests\auto\system3_generated_tests\test_phase_041.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 41

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase41_promotion_executor
```

### tests\auto\system3_generated_tests\test_phase_042.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 42

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase42_snapshot_manager
```

### tests\auto\system3_generated_tests\test_phase_043.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 43

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase43_env_guard
```

### tests\auto\system3_generated_tests\test_phase_046.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 46

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase46_meta_fusion
```

### tests\auto\system3_generated_tests\test_phase_047.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 47

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase47_confidence_vector
```

### tests\auto\system3_generated_tests\test_phase_048.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 48

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase48_error_scanner
```

### tests\auto\system3_generated_tests\test_phase_049.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 49

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase49_risk_regulator
```

### tests\auto\system3_generated_tests\test_phase_050.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 50

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase50_prediction_explainer
```

### tests\auto\system3_generated_tests\test_phase_051.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 51

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase51_probability_engine
```

### tests\auto\system3_generated_tests\test_phase_052.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 52

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase52_multi_broker
```

### tests\auto\system3_generated_tests\test_phase_053.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 53

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase53_monitoring_agent
```

### tests\auto\system3_generated_tests\test_phase_054.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 54

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase54_back_reconstruction
```

### tests\auto\system3_generated_tests\test_phase_055.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 55

Generated: 2025-12-03 00:26:01
Module: core.ultra.phase55_intelligence_dashboard
```

### tests\auto\system3_generated_tests\test_phase_076.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 76

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase76_geni_self_critique
```

### tests\auto\system3_generated_tests\test_phase_077.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 77

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase77_geni_self_correction
```

### tests\auto\system3_generated_tests\test_phase_078.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 78

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase78_geni_consensus
```

### tests\auto\system3_generated_tests\test_phase_079.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 79

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase79_adaptive_thresholds
```

### tests\auto\system3_generated_tests\test_phase_080.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 80

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase80_geni_evolution_status
```

### tests\auto\system3_generated_tests\test_phase_081.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 81

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase81_latency_profiler
```

### tests\auto\system3_generated_tests\test_phase_082.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 82

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase82_job_scheduler
```

### tests\auto\system3_generated_tests\test_phase_083.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 83

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase83_tick_to_trade_latency
```

### tests\auto\system3_generated_tests\test_phase_084.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 84

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase84_resource_optimizer
```

### tests\auto\system3_generated_tests\test_phase_085.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 85

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase85_heartbeat
```

### tests\auto\system3_generated_tests\test_phase_086.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 86

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase86_position_sizing
```

### tests\auto\system3_generated_tests\test_phase_087.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 87

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase87_expected_value
```

### tests\auto\system3_generated_tests\test_phase_088.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 88

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase88_portfolio_risk
```

### tests\auto\system3_generated_tests\test_phase_089.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 89

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase89_optimal_entry
```

### tests\auto\system3_generated_tests\test_phase_090.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 90

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase90_optimal_exit
```

### tests\auto\system3_generated_tests\test_phase_091.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 91

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase91_live_dashboard
```

### tests\auto\system3_generated_tests\test_phase_092.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 92

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase92_session_replay
```

### tests\auto\system3_generated_tests\test_phase_093.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 93

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase93_operator_override
```

### tests\auto\system3_generated_tests\test_phase_094.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 94

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase94_notification_engine
```

### tests\auto\system3_generated_tests\test_phase_095.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 95

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase95_operator_activity_log
```

### tests\auto\system3_generated_tests\test_phase_096.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 96

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase96_chaos_test
```

### tests\auto\system3_generated_tests\test_phase_097.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 97

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase97_backup_recovery
```

### tests\auto\system3_generated_tests\test_phase_098.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 98

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase98_rollback
```

### tests\auto\system3_generated_tests\test_phase_099.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 99

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase99_version_freeze
```

### tests\auto\system3_generated_tests\test_phase_100.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 100

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase100_final_certification
```

### tests\auto\system3_generated_tests\test_phase_101.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 101

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase101_live_trade_config_check
```

### tests\auto\system3_generated_tests\test_phase_102.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 102

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase102_order_ledger_schema
```

### tests\auto\system3_generated_tests\test_phase_104.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 104

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase104_tradeplan_to_orders
```

### tests\auto\system3_generated_tests\test_phase_105.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 105

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase105_ledger_integrity_check
```

### tests\auto\system3_generated_tests\test_phase_106.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 106

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase106_dryrun_execution_bridge
```

### tests\auto\system3_generated_tests\test_phase_107.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 107

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase107_live_execution_engine
```

### tests\auto\system3_generated_tests\test_phase_108.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 108

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase108_order_status_refresher
```

### tests\auto\system3_generated_tests\test_phase_109.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 109

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase109_intraday_risk_guard
```

### tests\auto\system3_generated_tests\test_phase_110.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 110

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase110_exit_rule_builder
```

### tests\auto\system3_generated_tests\test_phase_111.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 111

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase111_live_session_brain
```

### tests\auto\system3_generated_tests\test_phase_112.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 112

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase112_session_loop_controller
```

### tests\auto\system3_generated_tests\test_phase_113.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 113

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase113_kill_switch_monitor
```

### tests\auto\system3_generated_tests\test_phase_114.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 114

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase114_live_session_health
```

### tests\auto\system3_generated_tests\test_phase_115.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 115

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase115_intraday_alert_summary
```

### tests\auto\system3_generated_tests\test_phase_116.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 116

Generated: 2025-12-03 00:26:01
Module: core.engine.system3_phase116_end_session_auto_stop
```

### tests\auto\system3_generated_tests\test_phase_117.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 117

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase117_live_to_learning_bridge
```

### tests\auto\system3_generated_tests\test_phase_118.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 118

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase118_daily_live_pnl_snapshot
```

### tests\auto\system3_generated_tests\test_phase_119.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 119

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase119_live_safety_audit
```

### tests\auto\system3_generated_tests\test_phase_120.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 120

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase120_eod_live_summary_pack
```

### tests\auto\system3_generated_tests\test_phase_121.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 121

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase121_reserved
```

### tests\auto\system3_generated_tests\test_phase_122.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 122

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase122_reserved
```

### tests\auto\system3_generated_tests\test_phase_123.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 123

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase123_reserved
```

### tests\auto\system3_generated_tests\test_phase_124.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 124

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase124_reserved
```

### tests\auto\system3_generated_tests\test_phase_125.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 125

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase125_reserved
```

### tests\auto\system3_generated_tests\test_phase_126.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 126

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase126_control_panel_stub
```

### tests\auto\system3_generated_tests\test_phase_127.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 127

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase127_control_panel_stub
```

### tests\auto\system3_generated_tests\test_phase_128.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 128

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase128_control_panel_stub
```

### tests\auto\system3_generated_tests\test_phase_129.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 129

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase129_control_panel_stub
```

### tests\auto\system3_generated_tests\test_phase_130.py
- **Lines:** 240
- **Header:**
```python
"""
Auto-generated test for System3 Phase 130

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase130_control_panel_stub
```

### tests\auto\system3_generated_tests\test_phase_131.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 131

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase131_master_session_config
```

### tests\auto\system3_generated_tests\test_phase_132.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 132

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase132_master_health_snapshot
```

### tests\auto\system3_generated_tests\test_phase_133.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 133

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase133_master_safety_guard
```

### tests\auto\system3_generated_tests\test_phase_134.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 134

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase134_master_session_plan
```

### tests\auto\system3_generated_tests\test_phase_135.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 135

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase135_master_session_summary
```

### tests\auto\system3_generated_tests\test_phase_136.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 136

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase136_angel_symbol_universe
```

### tests\auto\system3_generated_tests\test_phase_137.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 137

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase137_expiry_calendar_map
```

### tests\auto\system3_generated_tests\test_phase_138.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 138

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase138_risk_tier_assignment
```

### tests\auto\system3_generated_tests\test_phase_139.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 139

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase139_lot_margin_estimator
```

### tests\auto\system3_generated_tests\test_phase_140.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 140

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase140_capital_guardrail
```

### tests\auto\system3_generated_tests\test_phase_141.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 141

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase141_spread_liquidity_estimator
```

### tests\auto\system3_generated_tests\test_phase_142.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 142

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase142_slippage_calculator
```

### tests\auto\system3_generated_tests\test_phase_143.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 143

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase143_execution_quality
```

### tests\auto\system3_generated_tests\test_phase_144.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 144

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase144_pnl_vs_execution_scenario
```

### tests\auto\system3_generated_tests\test_phase_145.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 145

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase145_one_lot_health_report
```

### tests\auto\system3_generated_tests\test_phase_146.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 146

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase146_index_catalog
```

### tests\auto\system3_generated_tests\test_phase_147.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 147

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase147_config_inventory
```

### tests\auto\system3_generated_tests\test_phase_148.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 148

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase148_storage_inventory
```

### tests\auto\system3_generated_tests\test_phase_149.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 149

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase149_log_inventory
```

### tests\auto\system3_generated_tests\test_phase_150.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 150

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase150_dependency_graph
```

### tests\auto\system3_generated_tests\test_phase_151.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 151

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase151_reserved_stub
```

### tests\auto\system3_generated_tests\test_phase_152.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 152

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase152_reserved_stub
```

### tests\auto\system3_generated_tests\test_phase_153.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 153

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase153_reserved_stub
```

### tests\auto\system3_generated_tests\test_phase_154.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 154

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase154_reserved_stub
```

### tests\auto\system3_generated_tests\test_phase_155.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 155

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase155_reserved_stub
```

### tests\auto\system3_generated_tests\test_phase_156.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 156

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase156_capital_curve_analysis
```

### tests\auto\system3_generated_tests\test_phase_157.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 157

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase157_misfire_breakdown
```

### tests\auto\system3_generated_tests\test_phase_158.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 158

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase158_regime_stability
```

### tests\auto\system3_generated_tests\test_phase_159.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 159

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase159_threshold_drift
```

### tests\auto\system3_generated_tests\test_phase_160.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 160

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase160_error_attribution
```

### tests\auto\system3_generated_tests\test_phase_161.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 161

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase161_risk_attribution
```

### tests\auto\system3_generated_tests\test_phase_162.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 162

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase162_capital_efficiency
```

### tests\auto\system3_generated_tests\test_phase_163.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 163

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase163_trade_frequency
```

### tests\auto\system3_generated_tests\test_phase_164.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 164

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase164_win_rate
```

### tests\auto\system3_generated_tests\test_phase_165.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 165

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase165_risk_reward
```

### tests\auto\system3_generated_tests\test_phase_166.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 166

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase166_underlying_performance
```

### tests\auto\system3_generated_tests\test_phase_167.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 167

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase167_time_of_day
```

### tests\auto\system3_generated_tests\test_phase_168.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 168

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase168_volatility_impact
```

### tests\auto\system3_generated_tests\test_phase_169.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 169

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase169_confidence_calibration
```

### tests\auto\system3_generated_tests\test_phase_170.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 170

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase170_stability_metrics
```

### tests\auto\system3_generated_tests\test_phase_171.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 171

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase171_file_backup
```

### tests\auto\system3_generated_tests\test_phase_172.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 172

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase172_schema_guard
```

### tests\auto\system3_generated_tests\test_phase_173.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 173

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase173_holiday_detection
```

### tests\auto\system3_generated_tests\test_phase_174.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 174

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase174_retention_policy
```

### tests\auto\system3_generated_tests\test_phase_175.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 175

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase175_exception_catalog
```

### tests\auto\system3_generated_tests\test_phase_176.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 176

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase176_long_run_summary
```

### tests\auto\system3_generated_tests\test_phase_177.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 177

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase177_performance_trends
```

### tests\auto\system3_generated_tests\test_phase_178.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 178

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase178_system_health_dashboard
```

### tests\auto\system3_generated_tests\test_phase_179.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 179

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase179_resource_usage_summary
```

### tests\auto\system3_generated_tests\test_phase_180.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 180

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase180_error_rate_analysis
```

### tests\auto\system3_generated_tests\test_phase_181.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 181

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase181_config_drift_detection
```

### tests\auto\system3_generated_tests\test_phase_182.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 182

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase182_data_quality_report
```

### tests\auto\system3_generated_tests\test_phase_183.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 183

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase183_model_performance_tracking
```

### tests\auto\system3_generated_tests\test_phase_184.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 184

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase184_signal_quality_metrics
```

### tests\auto\system3_generated_tests\test_phase_185.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 185

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase185_trade_execution_summary
```

### tests\auto\system3_generated_tests\test_phase_186.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 186

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase186_risk_metrics_summary
```

### tests\auto\system3_generated_tests\test_phase_187.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 187

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase187_capital_utilization_report
```

### tests\auto\system3_generated_tests\test_phase_188.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 188

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase188_underlying_performance_trends
```

### tests\auto\system3_generated_tests\test_phase_189.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 189

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase189_time_series_analysis
```

### tests\auto\system3_generated_tests\test_phase_190.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 190

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase190_correlation_analysis
```

### tests\auto\system3_generated_tests\test_phase_191.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 191

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase191_feature_importance_summary
```

### tests\auto\system3_generated_tests\test_phase_192.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 192

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase192_model_comparison_report
```

### tests\auto\system3_generated_tests\test_phase_193.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 193

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase193_system_status_dashboard
```

### tests\auto\system3_generated_tests\test_phase_194.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 194

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase194_operational_metrics
```

### tests\auto\system3_generated_tests\test_phase_195.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 195

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase195_master_summary_report
```

### tests\auto\system3_generated_tests\test_phase_196.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 196

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase196_dry_run_readiness
```

### tests\auto\system3_generated_tests\test_phase_197.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 197

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase197_micro_capital_test_plan
```

### tests\auto\system3_generated_tests\test_phase_198.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 198

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase198_human_gate_checklist
```

### tests\auto\system3_generated_tests\test_phase_199.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 199

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase199_live_mode_guard_stub
```

### tests\auto\system3_generated_tests\test_phase_200.py
- **Lines:** 231
- **Header:**
```python
"""
Auto-generated test for System3 Phase 200

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase200_master_status_snapshot
```

### tests\auto\system3_generated_tests\test_phase_201.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 201

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase201_filesystem_integrity
```

### tests\auto\system3_generated_tests\test_phase_202.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 202

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase202_permissions_self_repair
```

### tests\auto\system3_generated_tests\test_phase_203.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 203

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase203_config_consistency
```

### tests\auto\system3_generated_tests\test_phase_204.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 204

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase204_python_env_validator
```

### tests\auto\system3_generated_tests\test_phase_205.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 205

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase205_broker_selftest
```

### tests\auto\system3_generated_tests\test_phase_206.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 206

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase206_model_compatibility
```

### tests\auto\system3_generated_tests\test_phase_207.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 207

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase207_hotfix_registry
```

### tests\auto\system3_generated_tests\test_phase_208.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 208

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase208_signal_consistency
```

### tests\auto\system3_generated_tests\test_phase_209.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 209

Generated: 2025-12-03 00:26:02
Module: core.engine.system3_phase209_duplicate_purger
```

### tests\auto\system3_generated_tests\test_phase_210.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 210

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase210_timegap_analyzer
```

### tests\auto\system3_generated_tests\test_phase_211.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 211

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase211_feature_drift
```

### tests\auto\system3_generated_tests\test_phase_212.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 212

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase212_label_quality
```

### tests\auto\system3_generated_tests\test_phase_213.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 213

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase213_training_window
```

### tests\auto\system3_generated_tests\test_phase_214.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 214

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase214_hyperparam_snapshot
```

### tests\auto\system3_generated_tests\test_phase_215.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 215

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase215_overfit_sentinel
```

### tests\auto\system3_generated_tests\test_phase_216.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 216

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase216_greeks_audit
```

### tests\auto\system3_generated_tests\test_phase_217.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 217

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase217_vol_regime
```

### tests\auto\system3_generated_tests\test_phase_218.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 218

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase218_momentum_scanner
```

### tests\auto\system3_generated_tests\test_phase_219.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 219

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase219_breakout_analyzer
```

### tests\auto\system3_generated_tests\test_phase_220.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 220

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase220_correlation_map
```

### tests\auto\system3_generated_tests\test_phase_221.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 221

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase221_forward_returns
```

### tests\auto\system3_generated_tests\test_phase_222.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 222

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase222_signal_edge
```

### tests\auto\system3_generated_tests\test_phase_223.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 223

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase223_threshold_optimizer
```

### tests\auto\system3_generated_tests\test_phase_224.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 224

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase224_score_attribution
```

### tests\auto\system3_generated_tests\test_phase_225.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 225

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase225_label_reconciliation
```

### tests\auto\system3_generated_tests\test_phase_226.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 226

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase226_feature_importance
```

### tests\auto\system3_generated_tests\test_phase_227.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 227

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase227_latency_profiler
```

### tests\auto\system3_generated_tests\test_phase_228.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 228

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase228_snapshot_coverage
```

### tests\auto\system3_generated_tests\test_phase_229.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 229

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase229_schema_guard
```

### tests\auto\system3_generated_tests\test_phase_230.py
- **Lines:** 255
- **Header:**
```python
"""
Auto-generated test for System3 Phase 230

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase230_ai_fallback_audit
```

### tests\auto\system3_generated_tests\test_phase_231.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 231

Generated: 2025-12-03 00:26:03
Module: core.engine.threshold_loader
```

### tests\auto\system3_generated_tests\test_phase_261.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 261

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase261_portfolio_risk_analyzer
```

### tests\auto\system3_generated_tests\test_phase_262.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 262

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase262_multitimeframe_consistency
```

### tests\auto\system3_generated_tests\test_phase_263.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 263

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase263_advanced_pnl_attribution
```

### tests\auto\system3_generated_tests\test_phase_264.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 264

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase264_signal_quality_metrics
```

### tests\auto\system3_generated_tests\test_phase_265.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 265

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase265_execution_quality_analyzer
```

### tests\auto\system3_generated_tests\test_phase_266.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 266

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase266_capital_efficiency_tracker
```

### tests\auto\system3_generated_tests\test_phase_267.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 267

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase267_drawdown_analyzer
```

### tests\auto\system3_generated_tests\test_phase_268.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 268

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase268_sharpe_ratio_calculator
```

### tests\auto\system3_generated_tests\test_phase_269.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 269

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase269_winrate_by_time
```

### tests\auto\system3_generated_tests\test_phase_270.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 270

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase270_regime_performance_comparison
```

### tests\auto\system3_generated_tests\test_phase_271.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 271

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase271_hyperparameter_search
```

### tests\auto\system3_generated_tests\test_phase_272.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 272

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase272_feature_selection_optimizer
```

### tests\auto\system3_generated_tests\test_phase_273.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 273

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase273_model_ensemble_builder
```

### tests\auto\system3_generated_tests\test_phase_274.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 274

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase274_threshold_auto_tuner
```

### tests\auto\system3_generated_tests\test_phase_275.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 275

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase275_position_sizing_optimizer
```

### tests\auto\system3_generated_tests\test_phase_276.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 276

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase276_risk_reward_optimizer
```

### tests\auto\system3_generated_tests\test_phase_277.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 277

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase277_entry_timing_optimizer
```

### tests\auto\system3_generated_tests\test_phase_278.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 278

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase278_exit_timing_optimizer
```

### tests\auto\system3_generated_tests\test_phase_279.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 279

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase279_portfolio_rebalancer
```

### tests\auto\system3_generated_tests\test_phase_280.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 280

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase280_strategy_backtester
```

### tests\auto\system3_generated_tests\test_phase_281.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 281

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase281_realtime_performance_monitor
```

### tests\auto\system3_generated_tests\test_phase_282.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 282

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase282_anomaly_detector
```

### tests\auto\system3_generated_tests\test_phase_283.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 283

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase283_drift_monitor
```

### tests\auto\system3_generated_tests\test_phase_284.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 284

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase284_alert_aggregator
```

### tests\auto\system3_generated_tests\test_phase_285.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 285

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase285_health_dashboard_generator
```

### tests\auto\system3_generated_tests\test_phase_286.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 286

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase286_performance_degradation_detector
```

### tests\auto\system3_generated_tests\test_phase_287.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 287

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase287_resource_usage_monitor
```

### tests\auto\system3_generated_tests\test_phase_288.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 288

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase288_latency_monitor
```

### tests\auto\system3_generated_tests\test_phase_289.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 289

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase289_error_rate_tracker
```

### tests\auto\system3_generated_tests\test_phase_290.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 290

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase290_system_health_score
```

### tests\auto\system3_generated_tests\test_phase_291.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 291

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase291_daily_performance_report
```

### tests\auto\system3_generated_tests\test_phase_292.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 292

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase292_weekly_summary_report
```

### tests\auto\system3_generated_tests\test_phase_293.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 293

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase293_monthly_analytics_report
```

### tests\auto\system3_generated_tests\test_phase_294.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 294

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase294_strategy_performance_report
```

### tests\auto\system3_generated_tests\test_phase_295.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 295

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase295_risk_metrics_report
```

### tests\auto\system3_generated_tests\test_phase_296.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 296

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase296_model_performance_report
```

### tests\auto\system3_generated_tests\test_phase_297.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 297

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase297_trade_execution_report
```

### tests\auto\system3_generated_tests\test_phase_298.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 298

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase298_system_status_report
```

### tests\auto\system3_generated_tests\test_phase_299.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 299

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase299_master_summary_report
```

### tests\auto\system3_generated_tests\test_phase_300.py
- **Lines:** 250
- **Header:**
```python
"""
Auto-generated test for System3 Phase 300

Generated: 2025-12-03 00:26:03
Module: core.engine.system3_phase300_phase_completion_validator
```

### tests\auto\system3_generated_tests\test_phases_201_230.py
- **Lines:** 852
- **Header:**
```python
"""
Auto-generated test for System3 Phases 201-230

Generated: 2025-12-03 00:26:03
Total Phases: 30
```

### tests\auto\system3_generated_tests\test_phases_231_260.py
- **Lines:** 98
- **Header:**
```python
"""
Auto-generated test for System3 Phases 231-260

Generated: 2025-12-03 00:26:03
Total Phases: 1
```

### tests\auto\system3_generated_tests\test_phases_261_300.py
- **Lines:** 1112
- **Header:**
```python
"""
Auto-generated test for System3 Phases 261-300

Generated: 2025-12-03 00:26:03
Total Phases: 40
```

### tests\test_geni_master.py
- **Lines:** 159
- **Header:**
```python
"""
Tests for System3 GENI Master Agent

Tests import checks, path correctness, state management, and orchestrator.
"""
```

### tmp_profile_signals.py
- **Lines:** 32
- **Header:**
```python
import pandas as pd, json, pathlib
root = pathlib.Path('c:/Genesis_System3')
files = {
    'angel_index_ai_signals.csv': root / 'storage/live/angel_index_ai_signals.csv',
    'angel_index_ai_signals_curated.csv': root / 'storage/live/angel_index_ai_signals_curated.csv',
```

### tools\auto_verify_until_pass.py
- **Lines:** 65
- **Header:**
```python
"""Auto-run the full verification checklist (safe env) until it passes or max attempts reached.

This script calls `run_full_verification_with_env.bat` and captures each attempt's
output into `logs/inspector/verification_attempt_<timestamp>_<n>.log`.

```

### tools\check_cleaned_csv.py
- **Lines:** 15
- **Header:**
```python
from pathlib import Path
import sys
p=Path('storage/training/angel_index_options_training.csv')
if not p.exists():
    print('missing',p)
```

### tools\clean_training_csv.py
- **Lines:** 45
- **Header:**
```python
"""Attempt to clean malformed CSV rows by using pandas with tolerant parsing.

This script will:
 - back up the original CSV to `*.bak`
 - attempt to read with `engine='python'` and `on_bad_lines='skip'`
```

### tools\compute_mark_to_market_pnl.py
- **Lines:** 202
- **Header:**
```python
"""Compute mark-to-market P&L from ledger and market snapshot.

Reads:
  - `storage/live/live_orders_ledger.csv` (ledger of orders)
  - `storage/market_snapshot.json` (optional) or `storage/live/market_snapshot.json`
```

### tools\fix_csv_by_joining_lines.py
- **Lines:** 50
- **Header:**
```python
"""Attempt to fix CSV by joining subsequent physical lines until expected field count is reached.

This is a heuristic: it assumes rows were broken into multiple lines but fields do not contain unescaped newlines.
"""
from pathlib import Path
```

### tools\fix_csv_skip_bad.py
- **Lines:** 27
- **Header:**
```python
"""Skip bad rows by using pandas with on_bad_lines='skip'."""
from pathlib import Path
import shutil
import pandas as pd

```

### tools\fix_csv_with_csvmodule.py
- **Lines:** 66
- **Header:**
```python
"""Fix CSV by accumulating physical lines until csv.reader returns expected field count.

This is more robust than naive split(). It preserves quoting behavior.
"""
from pathlib import Path
```

### tools\inspect_training_csv.py
- **Lines:** 29
- **Header:**
```python
"""Inspect lines around a problematic CSV row for debugging.

Usage:
  .\venv\Scripts\python.exe tools\inspect_training_csv.py --start 2988 --end 3005
"""
```

### tools\quick_inspector.py
- **Lines:** 136
- **Header:**
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick inspector that writes `SYSTEM3_QUICK_INSPECTION_REPORT.md` in project root.
Safe, read-only.
```

### tools\run_paper_trading_e2e_test.py
- **Lines:** 154
- **Header:**
```python
"""E2E Paper Trading Test - Phase 106
Clean single-file implementation.

Run with the repository venv Python, e.g.:
  .\venv\Scripts\python.exe tools\run_paper_trading_e2e_test.py
```

### tools\run_phases_331_360_block_test.py
- **Lines:** 207
- **Header:**
```python
"""
System3 Block Test: Phases 331-360

Runs all new phases 331-360 in sequence with DRY-RUN mode.
Validates that all phases load correctly, execute without critical errors,
```

### tools\visualize_live_fills.py
- **Lines:** 138
- **Header:**
```python
"""Live visualizer for filled orders (quick view).

Usage:
  .\venv\Scripts\python.exe tools\visualize_live_fills.py --live

```

### update_phase_registry_311_330.py
- **Lines:** 76
- **Header:**
```python
"""
Add phases 311-330 to the System3 phase registry
"""

import json
```

### validate_auto_heal_implementation.py
- **Lines:** 286
- **Header:**
```python
"""
Final Validation Report - System3 Auto-Heal Implementation

This script runs a complete end-to-end validation of all auto-heal functionality.
"""
```

### validate_core_commands.py
- **Lines:** 206
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Core Commands Validation Script
Runs critical System3 commands and logs results with strict error detection.
"""
```

### validate_csv_fixes_and_system3.py
- **Lines:** 359
- **Header:**
```python
"""
System3 CSV Fixes Validation + Full System3 Validation
Tests CSV parsing fixes and runs comprehensive System3 validation
"""

```

### validate_integrity_tests.py
- **Lines:** 156
- **Header:**
```python
#!/usr/bin/env python3
"""
System3 Integrity Validation Test Suite
Tests phases 361-365 and 370-375 for runtime integrity
"""
```

### validate_pipeline_consistency.py
- **Lines:** 146
- **Header:**
```python
#!/usr/bin/env python3
"""
Pipeline Consistency Validation
Tests Phase 339 and 340 with new normalized/deduplicated data
"""
```

### validate_signal_files.py
- **Lines:** 166
- **Header:**
```python
"""
Signal Files Validation Report

Checks all three signal CSV files for schema completeness and data quality.
"""
```

### verify_all_warnings.py
- **Lines:** 152
- **Header:**
```python
"""
Verify All Warnings from System3 Validation
"""

import sys
```

### verify_expected_failures.py
- **Lines:** 207
- **Header:**
```python
#!/usr/bin/env python3
"""
Verify that the 4 "failed" checks are actually expected and will work correctly.
"""

```

### verify_fixes.py
- **Lines:** 114
- **Header:**
```python
"""
System3 Fixes Verification Script
Verifies that all critical fixes are working correctly.
"""

```

### verify_phase33_fix.py
- **Lines:** 53
- **Header:**
```python
"""
Quick verification script for Phase 33 fix
"""

import sys
```

### verify_phase_366_369_outputs.py
- **Lines:** 44
- **Header:**
```python
#!/usr/bin/env python3
"""Verify Phase 366-369 JSON outputs"""

import json
from pathlib import Path
```

### verify_phase_count.py
- **Lines:** 20
- **Header:**
```python
"""Quick script to verify phase count in registry."""
import json
from pathlib import Path

reg_path = Path("storage/meta/system3_phase_registry.json")
```

### verify_phases_331_360_implementation.py
- **Lines:** 191
- **Header:**
```python
"""
System3 Phases 331-360 Implementation Verification Script

Confirms all 30 phases are in place, registered, and callable.
Validates DRY-RUN safety settings.
```

### verify_phases_39_45.py
- **Lines:** 413
- **Header:**
```python
"""
System3 Ultra Phases 39-45: Complete Verification Script

This script verifies all phases 39-45 are working correctly.
Run this after implementation to confirm everything is operational.
```

### wait_and_run_live_watch.py
- **Lines:** 120
- **Header:**
```python
﻿"""
wait_and_run_live_watch.py

Scheduler script for Genesis_System3.

```

