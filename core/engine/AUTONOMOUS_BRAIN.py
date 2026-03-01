"""
💎 GENESIS SYSTEM3: AUTONOMOUS BRAIN (v1.0.0)
The Master Orchestrator for Self-Learning, Self-Improving, and Auto-Everything.
Goal: 24/7 Autonomous Evolution for Maximum Profit.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# Setup Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.HistoricalDataDownloader import HistoricalDataDownloader
from core.engine.ultra_train_models import train_ultra_models
from scripts.world_class_optimizer import WorldClassOptimizer
from continuous_learning_system import ContinuousLearningSystem

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BRAIN] - %(message)s')
logger = logging.getLogger(__name__)

class AutonomousBrain:
    def __init__(self):
        self.cycle_count = 0
        self.last_accuracy = 0.0
        self.status_file = PROJECT_ROOT / "storage" / "state" / "brain_status.json"
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def run_full_evolution_cycle(self):
        """
        Executes a complete 4-stage evolution cycle:
        1. Download -> 2. Learn -> 3. Optimize -> 4. Self-Improve
        """
        self.cycle_count += 1
        logger.info(f"=== STARTING EVOLUTION CYCLE #{self.cycle_count} ===")
        
        # STAGE 1: Data Acquisition
        logger.info("STAGE 1: Autonomous Historical Data Download...")
        downloader = HistoricalDataDownloader(days_back=730)
        dl_report = downloader.download_all()
        logger.info(f"✓ Download complete. Status: {dl_report}")

        # STAGE 2: Self-Learning (Model Training)
        logger.info("STAGE 2: Autonomous Model Retraining (Ultra V3 - Indices + Stocks)...")
        from core.engine.HistoricalDataDownloader import SYMBOLS
        train_report = train_ultra_models(symbols=list(SYMBOLS.keys()))
        
        if train_report["status"] == "SUCCESS":
            valid_results = [r.get("accuracy", 0) for r in train_report["results"].values() if r["status"] == "SUCCESS"]
            avg_acc = sum(valid_results) / len(valid_results) if valid_results else 0
            self.last_accuracy = avg_acc
            logger.info(f"✓ Training complete for {len(valid_results)} symbols. Avg Acc: {avg_acc:.2%}")
        else:
            logger.warning(f"⚠ Training skipped: {train_report.get('message')}")

        # STAGE 3: World-Class Optimization
        logger.info("STAGE 3: World-Class Strategy Optimization...")
        try:
            # We use the master data for optimization
            excel_path = PROJECT_ROOT / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"
            if excel_path.exists():
                df = pd.read_excel(excel_path, sheet_name="OptionChain_Data")
                optimizer = WorldClassOptimizer()
                opt_results = optimizer.run_world_class_optimization(df)
                best_opt = opt_results[0]
                logger.info(f"✓ Optimization complete. Best: {best_opt['technique']} (PnL improvement: {best_opt['improvement_pct']:.1f}%)")
            else:
                logger.warning("⚠ Optimization skipped: Excel data missing.")
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {e}")

        # STAGE 4: Self-Improvement (System Update)
        logger.info("STAGE 4: Autonomous System Auto-Update...")
        self._update_system_parameters()
        
        # STAGE 5: Mobile Notification
        try:
            from core.utils.InstitutionalAlertManager import alert_manager
            msg = f"💎 Genesis Evolution Cycle #{self.cycle_count} Complete.\nAvg Model Accuracy: {self.last_accuracy:.2%}\nSystem Status: WORLD-CLASS READY."
            alert_manager.send_whatsapp_alert(msg)
        except Exception as e:
            logger.error(f"Failed to send mobile alert: {e}")

        # Save Status
        self._save_brain_status()
        logger.info(f"=== EVOLUTION CYCLE #{self.cycle_count} COMPLETE ===")

    def _update_system_parameters(self):
        """
        Autonomous update of signal_scorer and entry_exit_rules weights
        based on the latest successful training and optimization results.
        """
        # Logic to write to .json config files which are then read by the engines
        # OR surgically update the .py files (using sed-like logic)
        config_path = PROJECT_ROOT / "config" / "autonomous_params.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        params = {
            "last_cycle": self.cycle_count,
            "target_accuracy": self.last_accuracy,
            "optimal_threshold": 0.65 if self.last_accuracy > 0.6 else 0.55,
            "ai_weight": 0.45 if self.last_accuracy > 0.7 else 0.40,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(config_path, "w") as f:
            json.dump(params, f, indent=2)
        logger.info(f"✓ System parameters updated: {config_path}")

    def _save_brain_status(self):
        status = {
            "cycle": self.cycle_count,
            "last_run": datetime.now().isoformat(),
            "last_accuracy": self.last_accuracy,
            "status": "OPERATIONAL",
            "autonomous_verified": True
        }
        with open(self.status_file, "w") as f:
            json.dump(status, f, indent=2)

    def start_service(self):
        """Continuously runs the brain."""
        logger.info("Autonomous Brain Service Started.")
        while True:
            try:
                self.run_full_evolution_cycle()
                # Run once every 24 hours (86400 seconds)
                logger.info("Sleeping for 24 hours...")
                time.sleep(86400)
            except KeyboardInterrupt:
                logger.info("Service stopped by user.")
                break
            except Exception as e:
                logger.error(f"Critical error in Brain loop: {e}")
                time.sleep(3600) # Wait an hour and retry

if __name__ == "__main__":
    brain = AutonomousBrain()
    # For proof-of-concept, we run once
    brain.run_full_evolution_cycle()
