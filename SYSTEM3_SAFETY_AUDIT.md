# System3 Safety Audit
**Generated:** 2025-12-07 13:56:16

## ⚠️ SAFETY FINDINGS

### CRITICAL: AUTO_EXECUTE_TRADES=True
**Count:** 1

- system3_master_inspector.py:119 - (r'AUTO_EXECUTE_TRADES\s*=\s*True', 'CRITICAL: AUTO_EXECUTE_TRADES=True'),

### CRITICAL: LIVE_TRADING_ENABLED=True
**Count:** 4

- system3_master_inspector.py:118 - (r'LIVE_TRADING_ENABLED\s*=\s*True', 'CRITICAL: LIVE_TRADING_ENABLED=True'),
- verify_phases_331_360_implementation.py:135 - print("  ❌ LIVE_TRADING_ENABLED = True (should be False)")
- core\engine\system3_phase101_live_trade_config_check.py:61 - warnings.append("WARNING: LIVE_TRADING_ENABLED=True")
- core\engine\system3_phase376_self_test_suite.py:194 - "LIVE_TRADING_ENABLED = True",

### CRITICAL: USE_LIVE_EXECUTION_ENGINE=True
**Count:** 1

- system3_master_inspector.py:120 - (r'USE_LIVE_EXECUTION_ENGINE\s*=\s*True', 'CRITICAL: USE_LIVE_EXECUTION_ENGINE=True'),

### WARNING: execute_trade() call detected
**Count:** 1

- system3_master_inspector.py:122 - (r'execute_trade\(', 'WARNING: execute_trade() call detected'),

### WARNING: live=True assignment
**Count:** 1

- system3_master_inspector.py:123 - (r'live\s*=\s*True', 'WARNING: live=True assignment'),

### WARNING: place_order() call detected
**Count:** 4

- system3_master_inspector.py:121 - (r'place_order\(', 'WARNING: place_order() call detected'),
- core\engine\angel_executor_live_prep.py:112 - # response = broker.place_order(payload)
- core\ultra\phase52_multi_broker.py:50 - def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
- core\ultra\phase52_multi_broker.py:83 - order_result = broker.place_order({

