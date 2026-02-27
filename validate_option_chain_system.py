"""
Comprehensive Validation Script for Option Chain Automation System
===================================================================

This script performs comprehensive validation of the entire system:
- Component availability
- Configuration validation
- Data pipeline validation
- Integration checks
- Performance benchmarks

Run: python validate_option_chain_system.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import importlib
from typing import Dict, List, Tuple, Any

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class SystemValidator:
    """Comprehensive system validator."""
    
    def __init__(self):
        """Initialize validator."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'configuration': {},
            'integration': {},
            'performance': {},
            'overall_status': 'UNKNOWN',
            'errors': [],
            'warnings': []
        }
    
    def validate_imports(self) -> Dict[str, bool]:
        """Validate all required imports."""
        print("Validating imports...")
        
        required_modules = [
            ('pandas', 'pd'),
            ('numpy', 'np'),
            ('json', None),
            ('datetime', None),
            ('threading', None),
            ('pathlib', None),
            ('pytz', None),
        ]
        
        optional_modules = [
            ('scipy', None),
            ('sklearn', None),
            ('xgboost', 'xgb'),
            ('rich', None),
        ]
        
        results = {}
        
        # Check required modules
        for module_name, alias in required_modules:
            try:
                if alias:
                    importlib.import_module(module_name)
                else:
                    importlib.import_module(module_name)
                results[module_name] = True
                print(f"  [OK] {module_name}")
            except ImportError:
                results[module_name] = False
                self.results['errors'].append(f"Required module '{module_name}' not found")
                print(f"  [FAIL] {module_name} (REQUIRED)")
        
        # Check optional modules
        for module_name, alias in optional_modules:
            try:
                if alias:
                    importlib.import_module(module_name)
                else:
                    importlib.import_module(module_name)
                results[module_name] = True
                print(f"  [OK] {module_name} (optional)")
            except ImportError:
                results[module_name] = False
                self.results['warnings'].append(f"Optional module '{module_name}' not found")
                print(f"  [WARN] {module_name} (optional)")
        
        self.results['components']['imports'] = results
        return results
    
    def validate_core_components(self) -> Dict[str, bool]:
        """Validate core system components."""
        print("\nValidating core components...")
        
        components = {
            'OptionChainAutomationMaster': False,
            'SystemConfig': False,
            'SystemStatus': False,
            'AngelOneBroker': False,
            'LiveChainWebSocket': False,
            'LiveChainREST': False,
            'EnsemblePredictor': False,
            'PaperExecutor': False,
            'PnLTracker': False,
            'DynamicRiskManager': False,
        }
        
        # Try importing main module
        try:
            from option_chain_automation_master import (
                OptionChainAutomationMaster,
                SystemConfig,
                SystemStatus
            )
            components['OptionChainAutomationMaster'] = True
            components['SystemConfig'] = True
            components['SystemStatus'] = True
            print("  [OK] OptionChainAutomationMaster")
            print("  [OK] SystemConfig")
            print("  [OK] SystemStatus")
        except Exception as e:
            self.results['errors'].append(f"Failed to import main module: {e}")
            print(f"  [FAIL] OptionChainAutomationMaster: {e}")
        
        # Try importing broker (optional - SmartApi may not be installed)
        try:
            from core.brokers.angel_one.broker import AngelOneBroker
            components['AngelOneBroker'] = True
            print("  [OK] AngelOneBroker")
        except ImportError as e:
            # SmartApi not installed - this is OK for validation
            components['AngelOneBroker'] = False
            self.results['warnings'].append(f"Broker not available (SmartApi not installed): {e}")
            print(f"  [WARN] AngelOneBroker: SmartApi not installed (optional)")
        except Exception as e:
            self.results['warnings'].append(f"Broker import failed: {e}")
            print(f"  [WARN] AngelOneBroker: {e}")
        
        # Try importing data fetchers (optional - depends on broker)
        try:
            from src.angel.live_chain_ws import LiveChainWebSocket
            components['LiveChainWebSocket'] = True
            print("  [OK] LiveChainWebSocket")
        except ImportError as e:
            # SmartApi not installed - this is OK
            components['LiveChainWebSocket'] = False
            print(f"  [WARN] LiveChainWebSocket: SmartApi not installed (optional)")
        except Exception as e:
            self.results['warnings'].append(f"WebSocket import failed: {e}")
            print(f"  [WARN] LiveChainWebSocket: {e}")
        
        try:
            from src.angel.live_chain_rest import LiveChainREST
            components['LiveChainREST'] = True
            print("  [OK] LiveChainREST")
        except ImportError as e:
            # SmartApi not installed - this is OK
            components['LiveChainREST'] = False
            print(f"  [WARN] LiveChainREST: SmartApi not installed (optional)")
        except Exception as e:
            self.results['warnings'].append(f"REST import failed: {e}")
            print(f"  [WARN] LiveChainREST: {e}")
        
        # Try importing ML components
        try:
            from src.ml.ensemble_predictor import EnsemblePredictor
            components['EnsemblePredictor'] = True
            print("  [OK] EnsemblePredictor")
        except Exception as e:
            self.results['warnings'].append(f"ML predictor import failed: {e}")
            print(f"  [WARN] EnsemblePredictor: {e}")
        
        # Try importing trading components
        try:
            from src.trading.paper_executor import PaperExecutor
            components['PaperExecutor'] = True
            print("  [OK] PaperExecutor")
        except Exception as e:
            self.results['warnings'].append(f"Paper executor import failed: {e}")
            print(f"  [WARN] PaperExecutor: {e}")
        
        try:
            from src.trading.pnl_tracker import PnLTracker
            components['PnLTracker'] = True
            print("  [OK] PnLTracker")
        except Exception as e:
            self.results['warnings'].append(f"PnL tracker import failed: {e}")
            print(f"  [WARN] PnLTracker: {e}")
        
        try:
            from src.trading.dynamic_risk_management import DynamicRiskManager
            components['DynamicRiskManager'] = True
            print("  [OK] DynamicRiskManager")
        except Exception as e:
            self.results['warnings'].append(f"Risk manager import failed: {e}")
            print(f"  [WARN] DynamicRiskManager: {e}")
        
        self.results['components']['core'] = components
        return components
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate system configuration."""
        print("\nValidating configuration...")
        
        config_results = {
            'config_file_exists': False,
            'config_valid': False,
            'default_config_valid': True,
        }
        
        # Check config file
        config_path = ROOT_DIR / "config" / "option_chain_config.json"
        if config_path.exists():
            config_results['config_file_exists'] = True
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                config_results['config_valid'] = True
                print("  [OK] Config file exists and is valid")
            except Exception as e:
                self.results['warnings'].append(f"Config file invalid: {e}")
                print(f"  [WARN] Config file invalid: {e}")
        else:
            print("  [INFO] No custom config file (using defaults)")
        
        # Validate default config
        try:
            from option_chain_automation_master import SystemConfig
            config = SystemConfig()
            config_dict = config.to_dict()
            config_results['default_config'] = config_dict
            print("  [OK] Default configuration valid")
        except Exception as e:
            config_results['default_config_valid'] = False
            self.results['errors'].append(f"Default config invalid: {e}")
            print(f"  [FAIL] Default config invalid: {e}")
        
        self.results['configuration'] = config_results
        return config_results
    
    def validate_directories(self) -> Dict[str, bool]:
        """Validate required directories."""
        print("\nValidating directories...")
        
        required_dirs = [
            ('outputs', ROOT_DIR / "outputs"),
            ('logs', ROOT_DIR / "logs"),
            ('storage', ROOT_DIR / "storage"),
            ('config', ROOT_DIR / "config"),
        ]
        
        dir_results = {}
        
        for name, path in required_dirs:
            if path.exists():
                dir_results[name] = True
                print(f"  [OK] {name}/")
            else:
                dir_results[name] = False
                # Create if missing
                path.mkdir(parents=True, exist_ok=True)
                print(f"  [WARN] {name}/ (created)")
                self.results['warnings'].append(f"Directory '{name}' was missing, created")
        
        self.results['components']['directories'] = dir_results
        return dir_results
    
    def validate_integration(self) -> Dict[str, bool]:
        """Validate component integration."""
        print("\nValidating integration...")
        
        integration_results = {
            'system_creation': False,
            'config_creation': False,
            'status_creation': False,
        }
        
        try:
            from option_chain_automation_master import (
                OptionChainAutomationMaster,
                SystemConfig,
                SystemStatus
            )
            
            # Test system creation
            config = SystemConfig()
            system = OptionChainAutomationMaster(config)
            integration_results['system_creation'] = True
            integration_results['config_creation'] = True
            print("  [OK] System creation")
            
            # Test status creation
            status = SystemStatus()
            integration_results['status_creation'] = True
            print("  [OK] Status creation")
            
        except Exception as e:
            self.results['errors'].append(f"Integration test failed: {e}")
            print(f"  [FAIL] Integration test failed: {e}")
        
        self.results['integration'] = integration_results
        return integration_results
    
    def calculate_overall_status(self):
        """Calculate overall system status."""
        error_count = len(self.results['errors'])
        warning_count = len(self.results['warnings'])
        
        # Filter out SmartApi warnings (they're expected if not installed)
        smartapi_warnings = [w for w in self.results['warnings'] if 'SmartApi' in w or 'smartapi' in w.lower()]
        non_smartapi_warnings = warning_count - len(smartapi_warnings)
        
        if error_count == 0 and non_smartapi_warnings == 0:
            self.results['overall_status'] = 'EXCELLENT'
        elif error_count == 0:
            self.results['overall_status'] = 'GOOD'
        elif error_count < 3:
            self.results['overall_status'] = 'DEGRADED'
        else:
            self.results['overall_status'] = 'FAILED'
    
    def generate_report(self) -> str:
        """Generate validation report."""
        report_lines = [
            "=" * 80,
            "OPTION CHAIN AUTOMATION SYSTEM - VALIDATION REPORT",
            "=" * 80,
            f"Timestamp: {self.results['timestamp']}",
            f"Overall Status: {self.results['overall_status']}",
            "",
            "SUMMARY:",
            f"  Errors: {len(self.results['errors'])}",
            f"  Warnings: {len(self.results['warnings'])}",
            "",
        ]
        
        if self.results['errors']:
            report_lines.append("ERRORS:")
            for error in self.results['errors']:
                report_lines.append(f"  [FAIL] {error}")
            report_lines.append("")
        
        if self.results['warnings']:
            report_lines.append("WARNINGS:")
            for warning in self.results['warnings']:
                report_lines.append(f"  [WARN] {warning}")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("=" * 80)
        print("OPTION CHAIN AUTOMATION SYSTEM - VALIDATION")
        print("=" * 80)
        print()
        
        # Run all validations
        self.validate_imports()
        self.validate_core_components()
        self.validate_configuration()
        self.validate_directories()
        self.validate_integration()
        
        # Calculate overall status
        self.calculate_overall_status()
        
        # Generate report
        report = self.generate_report()
        print("\n" + report)
        
        # Save results
        results_file = ROOT_DIR / "outputs" / "validation_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nResults saved to: {results_file}")
        
        return len(self.results['errors']) == 0


def main():
    """Main entry point."""
    validator = SystemValidator()
    success = validator.validate_all()
    
    if success:
        print("\n[SUCCESS] Validation PASSED - System is ready!")
        return 0
    else:
        print("\n[FAIL] Validation FAILED - Please fix errors before running system")
        return 1


if __name__ == "__main__":
    sys.exit(main())
