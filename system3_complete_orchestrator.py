"""
System3 Complete Orchestrator - THE ULTIMATE MASTER

Handles ALL phases (1-∞) across all tiers:
- Tier 1: Core/Baseline (1-200) - Integrated in signal engine
- Tier 2: Operational (201-310) - Dynamic phase controller
- Tier 3: Future (311+) - Auto-discovery

This is the SINGLE POINT OF CONTROL for the entire System3 ecosystem.

USER NEVER NEEDS TO KNOW:
- What phases exist
- When to run them
- How to run them
- What order to run them

EVERYTHING IS AUTOMATIC.
"""

import sys
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from system3_dynamic_phase_controller import DynamicPhaseRegistry, DynamicPhaseExecutor

LOG_DIR = PROJECT_ROOT / "logs" / "complete_orchestrator"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"complete_orchestrator_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("CompleteOrchestrator")


class CompleteOrchestrator:
    """
    The Ultimate Master Orchestrator.
    
    Handles ALL phases across all tiers with ZERO user intervention.
    """
    
    def __init__(self):
        self.phase_registry = DynamicPhaseRegistry()
        self.phase_executor = None
        self.signal_engine_running = False
        self.operational_phases_running = False
        
        logger.info("=" * 80)
        logger.info("🎯 COMPLETE ORCHESTRATOR - INITIALIZING")
        logger.info("=" * 80)
        
    def initialize(self) -> bool:
        """Initialize all orchestration components."""
        logger.info("\n📋 Initialization")
        logger.info("-" * 80)
        
        # Load phase registry
        logger.info("1️⃣  Loading phase registry...")
        if not self.phase_registry.load_from_registry():
            logger.error("   ❌ Failed to load phase registry")
            return False
        
        logger.info(f"   ✅ Loaded {len(self.phase_registry.phases)} phases")
        
        # Initialize phase executor
        logger.info("2️⃣  Initializing phase executor...")
        self.phase_executor = DynamicPhaseExecutor(self.phase_registry)
        logger.info("   ✅ Phase executor ready")
        
        # Analyze phase distribution
        logger.info("\n3️⃣  Phase Distribution:")
        tier1_phases = [p for p in self.phase_registry.phases.keys() if p <= 200]
        tier2_phases = [p for p in self.phase_registry.phases.keys() if 201 <= p <= 310]
        tier3_phases = [p for p in self.phase_registry.phases.keys() if p > 310]
        
        logger.info(f"   Tier 1 (Core: 1-200): {len(tier1_phases)} phases")
        logger.info(f"   Tier 2 (Operational: 201-310): {len(tier2_phases)} phases")
        logger.info(f"   Tier 3 (Future: 311+): {len(tier3_phases)} phases")
        
        logger.info("\n✅ Initialization complete")
        logger.info("-" * 80)
        return True
    
    def get_current_tier(self) -> str:
        """Determine which tier should be active based on time."""
        now = datetime.now()
        current_time = now.time()
        
        # Market hours
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        pre_market_start = dt_time(7, 0)
        post_market_end = dt_time(18, 0)
        
        is_weekend = now.weekday() >= 5
        
        if is_weekend:
            return "maintenance"
        elif pre_market_start <= current_time < market_start:
            return "pre_market"
        elif market_start <= current_time <= market_end:
            return "market_hours"
        elif market_end < current_time <= post_market_end:
            return "post_market"
        else:
            return "maintenance"
    
    def execute_tier1_core_system(self) -> bool:
        """
        Execute Tier 1: Core/Baseline phases (1-200).
        
        These are integrated in the signal engine and always active.
        We don't need to run them separately.
        """
        logger.info("\n🎯 TIER 1: CORE SYSTEM (Phases 1-200)")
        logger.info("-" * 80)
        logger.info("ℹ️  Core phases are integrated in signal engine")
        logger.info("ℹ️  They execute automatically when generating signals")
        logger.info("ℹ️  No separate execution required")
        logger.info("✅ Tier 1 status: ALWAYS ACTIVE")
        logger.info("-" * 80)
        return True
    
    def execute_tier2_operational(self, category: Optional[str] = None) -> bool:
        """
        Execute Tier 2: Operational phases (201-310).
        
        These run on schedule based on market hours.
        """
        logger.info("\n🎯 TIER 2: OPERATIONAL PHASES (201-310)")
        logger.info("-" * 80)
        
        if category:
            logger.info(f"📍 Executing {category} phases...")
            result = self.phase_executor.execute_category(category)
        else:
            logger.info("📍 Executing all Tier 2 phases...")
            tier2_phases = [p for p in self.phase_registry.phases.keys() if 201 <= p <= 310]
            results = []
            for phase_num in sorted(tier2_phases):
                result = self.phase_executor.execute_phase(phase_num)
                results.append(result)
            
            ok_count = sum(1 for r in results if r["status"] == "OK")
            warn_count = sum(1 for r in results if r["status"] == "WARN")
            error_count = sum(1 for r in results if r["status"] == "ERROR")
            
            logger.info("-" * 80)
            logger.info(f"📊 Summary: {ok_count} OK, {warn_count} WARN, {error_count} ERROR")
            
            return error_count == 0
        
        logger.info("-" * 80)
        return result.get("error", 0) == 0
    
    def execute_tier3_future(self) -> bool:
        """
        Execute Tier 3: Future phases (311+).
        
        These are auto-discovered and executed dynamically.
        """
        logger.info("\n🎯 TIER 3: FUTURE PHASES (311+)")
        logger.info("-" * 80)
        
        tier3_phases = [p for p in self.phase_registry.phases.keys() if p > 310]
        
        if not tier3_phases:
            logger.info("ℹ️  No future phases (311+) implemented yet")
            logger.info("ℹ️  System ready for auto-discovery when implemented")
            logger.info("-" * 80)
            return True
        
        logger.info(f"📍 Found {len(tier3_phases)} future phases")
        logger.info(f"📍 Executing: {tier3_phases}")
        
        results = []
        for phase_num in sorted(tier3_phases):
            result = self.phase_executor.execute_phase(phase_num)
            results.append(result)
        
        ok_count = sum(1 for r in results if r["status"] == "OK")
        warn_count = sum(1 for r in results if r["status"] == "WARN")
        error_count = sum(1 for r in results if r["status"] == "ERROR")
        
        logger.info("-" * 80)
        logger.info(f"📊 Summary: {ok_count} OK, {warn_count} WARN, {error_count} ERROR")
        logger.info("-" * 80)
        
        return error_count == 0
    
    def execute_full_cycle(self) -> Dict[str, Any]:
        """
        Execute complete orchestration cycle for current time.
        
        Determines what should run based on current time and executes it.
        """
        logger.info("\n" + "=" * 80)
        logger.info("🔄 COMPLETE ORCHESTRATION CYCLE")
        logger.info("=" * 80)
        
        # Determine current tier
        tier = self.get_current_tier()
        logger.info(f"\n⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"🎯 Active Tier: {tier.upper()}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tier": tier,
            "tier1_status": "ALWAYS_ACTIVE",
            "tier2_status": None,
            "tier3_status": None,
        }
        
        # Tier 1 is always active
        self.execute_tier1_core_system()
        
        # Execute Tier 2 based on time
        if tier == "pre_market":
            logger.info("\n📍 Executing PRE-MARKET phases...")
            results["tier2_status"] = "EXECUTED" if self.execute_tier2_operational("pre_market") else "FAILED"
        
        elif tier == "market_hours":
            logger.info("\n📍 Executing MARKET HOURS phases...")
            results["tier2_status"] = "EXECUTED" if self.execute_tier2_operational("market_hours") else "FAILED"
        
        elif tier == "post_market":
            logger.info("\n📍 Executing POST-MARKET phases...")
            results["tier2_status"] = "EXECUTED" if self.execute_tier2_operational("post_market") else "FAILED"
        
        elif tier == "maintenance":
            logger.info("\n📍 Maintenance mode - running continuous monitoring...")
            results["tier2_status"] = "EXECUTED" if self.execute_tier2_operational("continuous") else "FAILED"
        
        # Execute Tier 3 (future phases)
        results["tier3_status"] = "EXECUTED" if self.execute_tier3_future() else "FAILED"
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ORCHESTRATION CYCLE COMPLETE")
        logger.info("=" * 80)
        
        return results
    
    def run_autonomous_orchestration(self):
        """
        Run continuous autonomous orchestration.
        
        Executes cycles based on priority and timing.
        """
        logger.info("\n" + "=" * 80)
        logger.info("🤖 STARTING AUTONOMOUS ORCHESTRATION")
        logger.info("=" * 80)
        logger.info("\nSystem will now run FULLY AUTONOMOUSLY")
        logger.info("All phases (1-∞) will be orchestrated automatically")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 80)
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                logger.info(f"\n\n{'=' * 80}")
                logger.info(f"🔄 AUTONOMOUS CYCLE #{cycle}")
                logger.info(f"{'=' * 80}")
                
                # Execute full cycle
                results = self.execute_full_cycle()
                
                # Determine sleep time based on tier
                tier = results["tier"]
                if tier == "market_hours":
                    sleep_time = 60  # 1 minute during market hours
                elif tier in ["pre_market", "post_market"]:
                    sleep_time = 300  # 5 minutes
                else:
                    sleep_time = 1800  # 30 minutes during maintenance
                
                logger.info(f"\n💤 Sleeping for {sleep_time} seconds ({sleep_time/60:.1f} minutes)...")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("\n\n" + "=" * 80)
            logger.info("🛑 STOPPING AUTONOMOUS ORCHESTRATION")
            logger.info("=" * 80)
            logger.info("✅ Clean shutdown complete")


def main():
    """Main entry point."""
    orchestrator = CompleteOrchestrator()
    
    if not orchestrator.initialize():
        logger.error("❌ Initialization failed")
        return False
    
    # Run autonomous orchestration
    orchestrator.run_autonomous_orchestration()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
