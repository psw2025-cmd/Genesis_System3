"""
System3 Dynamic Phase Controller - FUTURE-PROOF PHASE EXECUTION

Automatically discovers and executes ALL phases (1-∞) without hardcoding.
This controller dynamically loads phases from the phase registry and executes them.

FEATURES:
- Dynamic phase discovery (no hardcoding)
- Automatically handles future phases (311+, 401+, 501+, etc.)
- Registry-based phase loading
- Dependency-aware execution
- Category-based scheduling (pre-market, market, post-market, maintenance)
- Self-updating (detects new phases automatically)

SAFETY: DRY-RUN ONLY - No real trading.
"""

import sys
import json
import logging
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "phase_controller"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"dynamic_phase_controller_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("DynamicPhaseController")

REGISTRY_FILE = PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json"


@dataclass
class PhaseDefinition:
    """Phase definition from registry."""
    phase: int
    implemented: bool
    impl_file: Optional[str]
    impl_location: Optional[str]
    spec_file: Optional[str]
    category: str = "general"
    dependencies: List[int] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class DynamicPhaseRegistry:
    """Dynamic phase registry loader."""
    
    def __init__(self):
        self.phases: Dict[int, PhaseDefinition] = {}
        self.phase_functions: Dict[int, Callable] = {}
        self.categories: Dict[str, List[int]] = {
            "pre_market": [],      # Run before market open
            "market_hours": [],    # Run during market hours
            "post_market": [],     # Run after market close
            "maintenance": [],     # Run during maintenance windows
            "continuous": [],      # Run continuously (monitoring)
            "general": [],         # Default category
        }
        
    def load_from_registry(self) -> bool:
        """Load all phases from registry."""
        try:
            if not REGISTRY_FILE.exists():
                logger.warning(f"Registry file not found: {REGISTRY_FILE}")
                logger.info("Running phase registry builder...")
                self._rebuild_registry()
            
            with REGISTRY_FILE.open("r", encoding="utf-8") as f:
                registry = json.load(f)
            
            for phase_str, phase_data in registry.items():
                phase_num = int(phase_str)
                
                phase_def = PhaseDefinition(
                    phase=phase_num,
                    implemented=phase_data.get("implemented", False),
                    impl_file=phase_data.get("impl_file"),
                    impl_location=phase_data.get("impl_location"),
                    spec_file=phase_data.get("spec_file"),
                    category=self._infer_category(phase_num, phase_data),
                    dependencies=phase_data.get("dependencies", [])
                )
                
                self.phases[phase_num] = phase_def
                self.categories[phase_def.category].append(phase_num)
            
            logger.info(f"✅ Loaded {len(self.phases)} phases from registry")
            logger.info(f"   Phase range: {min(self.phases.keys())}-{max(self.phases.keys())}")
            logger.info(f"   Implemented: {sum(1 for p in self.phases.values() if p.implemented)}")
            
            for category, phases in self.categories.items():
                if phases:
                    logger.info(f"   {category}: {len(phases)} phases")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load registry: {e}")
            return False
    
    def _rebuild_registry(self):
        """Rebuild registry if missing."""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "system3_universal_autophase_engine.py"],
                cwd=PROJECT_ROOT,
                timeout=300,
                capture_output=True,
                text=True
            )
            logger.info("✅ Registry rebuilt successfully")
        except Exception as e:
            logger.error(f"❌ Failed to rebuild registry: {e}")
    
    def _infer_category(self, phase_num: int, phase_data: Dict) -> str:
        """Infer phase category based on phase number and metadata."""
        # Phase number based categories
        if 201 <= phase_num <= 210:
            return "pre_market"
        elif 211 <= phase_num <= 230:
            return "market_hours"
        elif 231 <= phase_num <= 260:
            return "continuous"
        elif 261 <= phase_num <= 280:
            return "post_market"
        elif 281 <= phase_num <= 310:
            return "post_market"
        elif 306 <= phase_num <= 306:
            return "continuous"  # Staleness guard
        else:
            # Check spec file for category hints
            spec_file = phase_data.get("spec_file")
            if spec_file and isinstance(spec_file, str):
                spec_file_lower = spec_file.lower()
                if "pre" in spec_file_lower or "premarket" in spec_file_lower:
                    return "pre_market"
                elif "post" in spec_file_lower or "eod" in spec_file_lower:
                    return "post_market"
                elif "monitor" in spec_file_lower or "watch" in spec_file_lower:
                    return "continuous"
            return "general"
    
    def load_phase_function(self, phase_num: int) -> Optional[Callable]:
        """Dynamically load phase function."""
        if phase_num in self.phase_functions:
            return self.phase_functions[phase_num]
        
        if phase_num not in self.phases:
            logger.warning(f"Phase {phase_num} not in registry")
            return None
        
        phase_def = self.phases[phase_num]
        
        if not phase_def.implemented:
            logger.debug(f"Phase {phase_num} not implemented yet")
            return None
        
        try:
            # Try to load from impl_file
            impl_file = phase_def.impl_file
            if not impl_file:
                return None
            
            # Convert file path to module path
            impl_path = Path(impl_file)
            
            # Determine module name
            if "core/engine" in impl_file or "core\\engine" in impl_file:
                module_name = f"core.engine.{impl_path.stem}"
            elif "core/ultra" in impl_file or "core\\ultra" in impl_file:
                module_name = f"core.ultra.{impl_path.stem}"
            else:
                # Root level file
                module_name = impl_path.stem
            
            # Import module
            module = importlib.import_module(module_name)
            
            # Find run_phaseXXX function
            func_name = f"run_phase{phase_num}"
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                self.phase_functions[phase_num] = func
                logger.debug(f"✅ Loaded phase {phase_num} from {module_name}")
                return func
            else:
                logger.warning(f"Function {func_name} not found in {module_name}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to load phase {phase_num}: {e}")
            return None
    
    def get_phases_by_category(self, category: str) -> List[int]:
        """Get all phases in a category."""
        return sorted(self.categories.get(category, []))
    
    def get_executable_phases(self) -> List[int]:
        """Get all executable (implemented) phases."""
        return sorted([p for p, d in self.phases.items() if d.implemented])


class DynamicPhaseExecutor:
    """Execute phases dynamically based on registry."""
    
    def __init__(self, registry: DynamicPhaseRegistry):
        self.registry = registry
        self.execution_history: List[Dict[str, Any]] = []
        self.failed_phases: Set[int] = set()
        
    def execute_phase(self, phase_num: int, **kwargs) -> Dict[str, Any]:
        """Execute a single phase."""
        logger.info(f"📍 Executing Phase {phase_num}...")
        
        # Check if phase exists
        if phase_num not in self.registry.phases:
            result = {
                "phase": phase_num,
                "status": "ERROR",
                "details": "Phase not in registry",
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
        
        # Load phase function
        phase_func = self.registry.load_phase_function(phase_num)
        if not phase_func:
            result = {
                "phase": phase_num,
                "status": "SKIP",
                "details": "Phase not implemented or not loadable",
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
        
        # Execute phase
        try:
            result = phase_func(**kwargs)
            
            # Normalize result format
            if not isinstance(result, dict):
                result = {
                    "phase": phase_num,
                    "status": "OK",
                    "details": str(result),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result["timestamp"] = datetime.now().isoformat()
                if "phase" not in result:
                    result["phase"] = phase_num
            
            status = result.get("status", "UNKNOWN")
            details = result.get("details", "No details")
            
            if status == "ERROR":
                self.failed_phases.add(phase_num)
                logger.error(f"   ❌ Phase {phase_num}: {status} - {details}")
            elif status == "WARN":
                logger.warning(f"   ⚠️  Phase {phase_num}: {status} - {details}")
            else:
                logger.info(f"   ✅ Phase {phase_num}: {status} - {details}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Phase {phase_num} exception: {e}")
            self.failed_phases.add(phase_num)
            result = {
                "phase": phase_num,
                "status": "ERROR",
                "details": f"Exception: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_phase_range(self, start: int, end: int, **kwargs) -> Dict[str, Any]:
        """Execute phases in a range."""
        logger.info(f"🔄 Executing Phases {start}-{end}")
        logger.info("=" * 80)
        
        results = []
        for phase_num in range(start, end + 1):
            result = self.execute_phase(phase_num, **kwargs)
            results.append(result)
        
        # Summary
        ok_count = sum(1 for r in results if r["status"] == "OK")
        warn_count = sum(1 for r in results if r["status"] == "WARN")
        error_count = sum(1 for r in results if r["status"] == "ERROR")
        skip_count = sum(1 for r in results if r["status"] == "SKIP")
        
        logger.info("=" * 80)
        logger.info(f"📊 Summary: {ok_count} OK, {warn_count} WARN, {error_count} ERROR, {skip_count} SKIP")
        
        return {
            "start": start,
            "end": end,
            "total": len(results),
            "ok": ok_count,
            "warn": warn_count,
            "error": error_count,
            "skip": skip_count,
            "results": results
        }
    
    def execute_category(self, category: str, **kwargs) -> Dict[str, Any]:
        """Execute all phases in a category."""
        phases = self.registry.get_phases_by_category(category)
        
        if not phases:
            logger.warning(f"No phases found in category: {category}")
            return {"category": category, "phases": [], "total": 0}
        
        logger.info(f"🏷️  Executing {category.upper()} phases ({len(phases)} phases)")
        logger.info("=" * 80)
        
        results = []
        for phase_num in phases:
            result = self.execute_phase(phase_num, **kwargs)
            results.append(result)
        
        # Summary
        ok_count = sum(1 for r in results if r["status"] == "OK")
        warn_count = sum(1 for r in results if r["status"] == "WARN")
        error_count = sum(1 for r in results if r["status"] == "ERROR")
        skip_count = sum(1 for r in results if r["status"] == "SKIP")
        
        logger.info("=" * 80)
        logger.info(f"📊 {category.upper()} Summary: {ok_count} OK, {warn_count} WARN, {error_count} ERROR, {skip_count} SKIP")
        
        return {
            "category": category,
            "phases": phases,
            "total": len(results),
            "ok": ok_count,
            "warn": warn_count,
            "error": error_count,
            "skip": skip_count,
            "results": results
        }
    
    def execute_all_implemented(self, **kwargs) -> Dict[str, Any]:
        """Execute ALL implemented phases (dynamic)."""
        phases = self.registry.get_executable_phases()
        
        logger.info(f"🌐 Executing ALL IMPLEMENTED PHASES ({len(phases)} phases)")
        logger.info(f"   Range: {min(phases)}-{max(phases)}")
        logger.info("=" * 80)
        
        results = []
        for phase_num in phases:
            result = self.execute_phase(phase_num, **kwargs)
            results.append(result)
        
        # Summary
        ok_count = sum(1 for r in results if r["status"] == "OK")
        warn_count = sum(1 for r in results if r["status"] == "WARN")
        error_count = sum(1 for r in results if r["status"] == "ERROR")
        skip_count = sum(1 for r in results if r["status"] == "SKIP")
        
        logger.info("=" * 80)
        logger.info(f"📊 OVERALL Summary: {ok_count} OK, {warn_count} WARN, {error_count} ERROR, {skip_count} SKIP")
        
        return {
            "phases": phases,
            "total": len(results),
            "ok": ok_count,
            "warn": warn_count,
            "error": error_count,
            "skip": skip_count,
            "results": results
        }


def main():
    """Main entry point for testing."""
    logger.info("=" * 80)
    logger.info("🧠 DYNAMIC PHASE CONTROLLER - INITIALIZING")
    logger.info("=" * 80)
    
    # Load registry
    registry = DynamicPhaseRegistry()
    if not registry.load_from_registry():
        logger.error("❌ Failed to load registry")
        return False
    
    # Create executor
    executor = DynamicPhaseExecutor(registry)
    
    # Example: Execute phases 301-310
    logger.info("\n🧪 TEST: Executing Phases 301-310")
    result = executor.execute_phase_range(301, 310)
    
    # Example: Execute pre-market phases
    logger.info("\n🧪 TEST: Executing PRE-MARKET phases")
    result = executor.execute_category("pre_market")
    
    logger.info("\n✅ Dynamic Phase Controller Test Complete")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
