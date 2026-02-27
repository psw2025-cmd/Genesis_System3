#!/usr/bin/env python3
"""
Final comprehensive System3 validation and test suite
Tests all critical components and generates detailed results
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, r'C:\Genesis_System3')

def test_heartbeat():
    """Test 1: Check heartbeat status"""
    print("\n" + "="*80)
    print("TEST 1: HEARTBEAT INTEGRITY")
    print("="*80)
    
    heartbeat_file = r'C:\Genesis_System3\system3_daily_heartbeat.json'
    try:
        with open(heartbeat_file, 'r') as f:
            heartbeat = json.load(f)
        
        print(f"✓ Heartbeat file exists and is valid JSON")
        print(f"  Status: {heartbeat.get('status')}")
        print(f"  Timestamp: {heartbeat.get('timestamp')}")
        print(f"  Autopilot running: {heartbeat.get('autopilot_running')}")
        
        return True, heartbeat
    except Exception as e:
        print(f"✗ Heartbeat test FAILED: {e}")
        return False, None

def test_csv_files():
    """Test 2: Validate CSV files"""
    print("\n" + "="*80)
    print("TEST 2: CSV FILE INTEGRITY")
    print("="*80)
    
    csv_dir = r'C:\Genesis_System3\storage\live'
    required_files = [
        'angel_index_ai_signals.csv',
        'angel_index_ai_signals_curated.csv',
        'angel_index_ai_trades_exec_log.csv',
        'angel_index_ai_pnl_log.csv',
    ]
    
    results = {}
    for csv_file in required_files:
        csv_path = os.path.join(csv_dir, csv_file)
        try:
            if os.path.exists(csv_path):
                size = os.path.getsize(csv_path)
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                results[csv_file] = {
                    'exists': True,
                    'size': size,
                    'rows': len(lines),
                    'status': 'OK'
                }
                print(f"✓ {csv_file}: {len(lines)} rows, {size} bytes")
            else:
                results[csv_file] = {'exists': False, 'status': 'MISSING'}
                print(f"✗ {csv_file}: NOT FOUND")
        except Exception as e:
            results[csv_file] = {'exists': True, 'status': 'ERROR', 'error': str(e)}
            print(f"✗ {csv_file}: ERROR - {e}")
    
    return all(r.get('status') == 'OK' for r in results.values()), results

def test_phase_engine():
    """Test 3: Validate phase engine modules"""
    print("\n" + "="*80)
    print("TEST 3: PHASE ENGINE MODULES")
    print("="*80)
    
    phase_dir = r'C:\Genesis_System3\core\engine'
    
    try:
        # Count phase files
        phase_files = [f for f in os.listdir(phase_dir) if f.startswith('system3_phase_') and f.endswith('.py')]
        print(f"✓ Found {len(phase_files)} phase modules")
        
        # Check critical phases
        critical_phases = [249, 250, 251, 252, 253, 254, 255]
        missing = []
        for phase_num in critical_phases:
            phase_file = f'system3_phase_{phase_num:03d}.py'
            if phase_file not in phase_files:
                missing.append(phase_num)
            else:
                print(f"  ✓ Phase {phase_num}: present")
        
        if missing:
            print(f"✗ Missing phases: {missing}")
            return False, {'phase_count': len(phase_files), 'missing': missing}
        
        return True, {'phase_count': len(phase_files), 'critical_phases_found': critical_phases}
        
    except Exception as e:
        print(f"✗ Phase engine test FAILED: {e}")
        return False, {'error': str(e)}

def test_json_outputs():
    """Test 4: Validate JSON output files"""
    print("\n" + "="*80)
    print("TEST 4: JSON OUTPUT FILES (LSTM PIPELINE)")
    print("="*80)
    
    logs_dir = r'C:\Genesis_System3\logs'
    
    json_files = {
        'phase249_model_evaluation': 'phase249_model_evaluation_*.json',
        'phase251_promotion_decision': 'phase251_promotion_decision.json',
        'retraining_queue': 'retraining_queue.json',
    }
    
    results = {}
    
    # Check phase 251 promotion decision
    phase251_file = os.path.join(logs_dir, 'phase251_promotion_decision.json')
    try:
        with open(phase251_file, 'r') as f:
            phase251_data = json.load(f)
        
        print(f"✓ Phase 251 promotion decision:")
        print(f"  Timestamp: {phase251_data.get('decision_timestamp')}")
        print(f"  Drift alerts: {len(phase251_data.get('drift_alerts', []))} models")
        print(f"  Promotion candidates: {len(phase251_data.get('promotion_candidates', []))} models")
        results['phase251'] = {'status': 'OK', 'data': phase251_data}
    except Exception as e:
        print(f"✗ Phase 251 file ERROR: {e}")
        results['phase251'] = {'status': 'ERROR', 'error': str(e)}
    
    # Check retraining queue
    queue_file = os.path.join(logs_dir, 'retraining_queue.json')
    try:
        with open(queue_file, 'r') as f:
            queue_data = json.load(f)
        
        print(f"✓ Retraining queue:")
        print(f"  Total jobs: {queue_data.get('Count', 0)}")
        pending = sum(1 for job in queue_data.get('value', []) if job.get('status') == 'PENDING')
        print(f"  Pending jobs: {pending}")
        results['queue'] = {'status': 'OK', 'count': queue_data.get('Count', 0)}
    except Exception as e:
        print(f"✗ Retraining queue ERROR: {e}")
        results['queue'] = {'status': 'ERROR', 'error': str(e)}
    
    return all(r.get('status') == 'OK' for r in results.values()), results

def test_safety_flags():
    """Test 5: Verify safety flags"""
    print("\n" + "="*80)
    print("TEST 5: SAFETY FLAGS VERIFICATION")
    print("="*80)
    
    try:
        # Import config to check safety flags
        from config.system3_config import (
            LIVE_TRADING_ENABLED,
            USE_LIVE_EXECUTION_ENGINE,
            AUTO_EXECUTE_TRADES
        )
        
        print(f"LIVE_TRADING_ENABLED: {LIVE_TRADING_ENABLED}")
        print(f"USE_LIVE_EXECUTION_ENGINE: {USE_LIVE_EXECUTION_ENGINE}")
        print(f"AUTO_EXECUTE_TRADES: {AUTO_EXECUTE_TRADES}")
        
        if not LIVE_TRADING_ENABLED and not USE_LIVE_EXECUTION_ENGINE and not AUTO_EXECUTE_TRADES:
            print("✓ All safety flags are LOCKED (DRY-RUN mode confirmed)")
            return True, {
                'LIVE_TRADING_ENABLED': LIVE_TRADING_ENABLED,
                'USE_LIVE_EXECUTION_ENGINE': USE_LIVE_EXECUTION_ENGINE,
                'AUTO_EXECUTE_TRADES': AUTO_EXECUTE_TRADES
            }
        else:
            print("✗ WARNING: Some safety flags are not set to False")
            return False, {'status': 'safety_not_locked'}
            
    except Exception as e:
        print(f"✗ Safety flags test ERROR: {e}")
        return False, {'error': str(e)}

def test_logs_directory():
    """Test 6: Check logs directory structure"""
    print("\n" + "="*80)
    print("TEST 6: LOGS DIRECTORY STRUCTURE")
    print("="*80)
    
    logs_dir = r'C:\Genesis_System3\logs'
    
    try:
        # Check for dated subdirectories
        dated_dirs = [d for d in os.listdir(logs_dir) if d.startswith('2025-')]
        print(f"✓ Found {len(dated_dirs)} dated log directories")
        
        # Check latest log files
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        print(f"✓ Found {len(log_files)} log files")
        
        # Check for autorun master logs from today
        today_autorun = 'system3_autorun_master_20251206.log'
        today_path = os.path.join(logs_dir, today_autorun)
        if os.path.exists(today_path):
            size = os.path.getsize(today_path)
            print(f"✓ Today's autorun log: {size} bytes")
            return True, {
                'dated_dirs': len(dated_dirs),
                'log_files': len(log_files),
                'today_autorun': 'present'
            }
        else:
            print(f"! Today's autorun log not found yet")
            return True, {
                'dated_dirs': len(dated_dirs),
                'log_files': len(log_files),
                'today_autorun': 'not_yet_created'
            }
            
    except Exception as e:
        print(f"✗ Logs directory test ERROR: {e}")
        return False, {'error': str(e)}

def test_shutdown_flag():
    """Test 7: Check shutdown flag"""
    print("\n" + "="*80)
    print("TEST 7: SHUTDOWN FLAG STATUS")
    print("="*80)
    
    shutdown_file = r'C:\Genesis_System3\system3_shutdown_flag.json'
    try:
        with open(shutdown_file, 'r') as f:
            shutdown_data = json.load(f)
        
        print(f"✓ Shutdown flag file exists")
        print(f"  Timestamp: {shutdown_data.get('timestamp')}")
        print(f"  Status: {shutdown_data.get('status')}")
        print(f"  Reason: {shutdown_data.get('reason', 'N/A')}")
        
        return True, shutdown_data
    except Exception as e:
        print(f"✗ Shutdown flag test FAILED: {e}")
        return False, None

def main():
    """Run all tests"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "SYSTEM3 FINAL VALIDATION TEST SUITE" + " "*23 + "║")
    print("║" + " "*20 + f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*35 + "║")
    print("╚" + "="*78 + "╝")
    
    test_results = {}
    
    # Run all tests
    test_results['heartbeat'] = test_heartbeat()
    test_results['csv_files'] = test_csv_files()
    test_results['phase_engine'] = test_phase_engine()
    test_results['json_outputs'] = test_json_outputs()
    test_results['safety_flags'] = test_safety_flags()
    test_results['logs'] = test_logs_directory()
    test_results['shutdown_flag'] = test_shutdown_flag()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for name, (result, _) in test_results.items() if result)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Status: {'✓ ALL TESTS PASSED' if passed == total else '⚠ SOME TESTS FAILED'}")
    
    print("\nDetailed Results:")
    for test_name, (result, data) in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    # Write results to file
    results_file = r'C:\Genesis_System3\FINAL_VALIDATION_TEST_RESULTS.json'
    with open(results_file, 'w') as f:
        output = {
            'test_timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'overall_status': 'PASS' if passed == total else 'FAIL',
            'results': {k: {'passed': v[0], 'data': v[1]} for k, v in test_results.items()}
        }
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n✓ Results written to: {results_file}")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
