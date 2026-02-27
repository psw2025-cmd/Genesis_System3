#!/usr/bin/env python3
"""
Test Built App from Trader Perspective
Comprehensive testing of the built Electron app for real trader use
"""

import subprocess
import time
import requests
import json
from datetime import datetime
from pathlib import Path
import sys

API_BASE = "http://localhost:8000"
EXE_PATH = Path("desktop_app/dist/win-unpacked/System3 Ultra.exe")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def check_backend():
    """Check if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def test_trader_scenarios():
    """Test critical trader scenarios"""
    print_header("TRADER SCENARIO TESTING")
    
    scenarios = {
        "View Option Chain": {
            "endpoints": ["/api/chain/NIFTY", "/api/chain/BANKNIFTY"],
            "critical": True
        },
        "Check Trade Signals": {
            "endpoints": ["/api/signal/top", "/api/state"],
            "critical": True
        },
        "View Positions": {
            "endpoints": ["/api/positions", "/api/pnl"],
            "critical": True
        },
        "Check Risk": {
            "endpoints": ["/api/risk/portfolio", "/api/state"],
            "critical": True
        },
        "View Alerts": {
            "endpoints": ["/api/alerts/recent", "/api/state"],
            "critical": False
        },
        "Check Performance": {
            "endpoints": ["/api/perf", "/api/ml/performance"],
            "critical": False
        }
    }
    
    results = {}
    total_critical = 0
    passed_critical = 0
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n{Colors.BOLD}Testing: {scenario_name}{Colors.RESET}")
        scenario_passed = True
        
        for endpoint in scenario_data["endpoints"]:
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"  {Colors.GREEN}[OK]{Colors.RESET} {endpoint}")
                else:
                    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {endpoint} - Status {response.status_code}")
                    scenario_passed = False
            except Exception as e:
                print(f"  {Colors.RED}[FAIL]{Colors.RESET} {endpoint} - {e}")
                scenario_passed = False
        
        results[scenario_name] = {
            "passed": scenario_passed,
            "critical": scenario_data["critical"]
        }
        
        if scenario_data["critical"]:
            total_critical += 1
            if scenario_passed:
                passed_critical += 1
    
    print(f"\n{Colors.BOLD}Trader Scenario Summary:{Colors.RESET}")
    print(f"  Critical Scenarios: {passed_critical}/{total_critical} passed")
    
    return results, passed_critical == total_critical

def test_data_quality():
    """Test data quality for trading"""
    print_header("DATA QUALITY TESTING")
    
    # Test chain data quality
    try:
        response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
        if response.status_code == 200:
            data = response.json()
            contracts = data.get("contracts", [])
            spot = data.get("spot", 0)
            
            print(f"  Chain Data:")
            print(f"    Contracts: {len(contracts)}")
            print(f"    Spot Price: {spot}")
            
            # Validate data quality
            if len(contracts) > 0:
                sample = contracts[0]
                has_ltp = "ltp" in sample or "last_price" in sample
                has_iv = "iv" in sample or "implied_volatility" in sample
                has_greeks = any(g in sample for g in ["delta", "gamma", "theta", "vega"])
                
                print(f"    Has LTP: {Colors.GREEN if has_ltp else Colors.RED}{has_ltp}{Colors.RESET}")
                print(f"    Has IV: {Colors.GREEN if has_iv else Colors.RED}{has_iv}{Colors.RESET}")
                print(f"    Has Greeks: {Colors.GREEN if has_greeks else Colors.RED}{has_greeks}{Colors.RESET}")
                
                return has_ltp and has_iv
            else:
                print(f"    {Colors.YELLOW}No contracts in chain{Colors.RESET}")
                return False
        else:
            print(f"  {Colors.RED}Failed to fetch chain data{Colors.RESET}")
            return False
    except Exception as e:
        print(f"  {Colors.RED}Error: {e}{Colors.RESET}")
        return False

def test_performance_for_trading():
    """Test performance - critical for real-time trading"""
    print_header("PERFORMANCE TESTING (Trader Critical)")
    
    endpoints = [
        ("/api/chain/NIFTY", "Option Chain", 2000),  # Must be fast for trading
        ("/api/signal/top", "Trade Signals", 1500),
        ("/api/positions", "Positions", 1100),  # Slightly relaxed for consistency
        ("/api/state", "State (SSOT)", 1500)
    ]
    
    results = []
    all_pass = True
    
    for endpoint, name, max_ms in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            elapsed = (time.time() - start) * 1000
            
            passed = elapsed < max_ms and response.status_code == 200
            all_pass = all_pass and passed
            
            color = Colors.GREEN if passed else Colors.RED
            status = "PASS" if passed else "FAIL"
            
            print(f"  {name}: {color}{elapsed:.1f}ms{Colors.RESET} (Max: {max_ms}ms) [{status}]")
            
            results.append({
                "endpoint": endpoint,
                "name": name,
                "time_ms": elapsed,
                "max_ms": max_ms,
                "passed": passed
            })
        except Exception as e:
            print(f"  {name}: {Colors.RED}ERROR - {e}{Colors.RESET}")
            all_pass = False
            results.append({
                "endpoint": endpoint,
                "name": name,
                "error": str(e),
                "passed": False
            })
    
    return results, all_pass

def generate_trader_report(all_results):
    """Generate trader-focused report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = REPORTS_DIR / f"trader_test_{timestamp}.json"
    md_file = REPORTS_DIR / f"trader_test_{timestamp}.md"
    
    # Save JSON
    with open(json_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Generate Markdown
    md_content = f"""# Trader Perspective Test Report

**Generated:** {datetime.now().isoformat()}
**Purpose:** Validate app functionality from real trader perspective

## Summary

- **Trader Scenarios:** {all_results['scenarios']['passed']}/{all_results['scenarios']['total']} passed
- **Data Quality:** {'PASS' if all_results['data_quality'] else 'FAIL'}
- **Performance:** {'PASS' if all_results['performance']['all_pass'] else 'FAIL'}
- **Overall:** {'READY FOR TRADERS' if all_results['overall_pass'] else 'NEEDS IMPROVEMENT'}

## Trader Scenarios

"""
    
    for scenario, result in all_results['scenarios']['details'].items():
        status = "PASS" if result['passed'] else "FAIL"
        critical = "CRITICAL" if result['critical'] else "Optional"
        md_content += f"- **{scenario}**: {status} ({critical})\n"
    
    md_content += f"""
## Performance

Average response times:
"""
    
    for perf in all_results['performance']['results']:
        status = "PASS" if perf['passed'] else "FAIL"
        md_content += f"- {perf['name']}: {perf.get('time_ms', 'N/A'):.1f}ms (Max: {perf.get('max_ms', 'N/A')}ms) [{status}]\n"
    
    md_content += f"""
## Data Quality

- Chain data quality: {'PASS' if all_results['data_quality'] else 'FAIL'}

## Recommendations

"""
    
    if all_results['overall_pass']:
        md_content += "- ✅ **App is ready for trader use**\n"
        md_content += "- All critical scenarios passing\n"
        md_content += "- Performance within acceptable limits\n"
        md_content += "- Data quality validated\n"
    else:
        md_content += "- ⚠️ **Some improvements needed before trader use**\n"
        if not all_results['scenarios']['all_critical_pass']:
            md_content += "- Critical trader scenarios need attention\n"
        if not all_results['performance']['all_pass']:
            md_content += "- Performance optimization needed\n"
        if not all_results['data_quality']:
            md_content += "- Data quality improvements required\n"
    
    md_content += f"""
---
**Report generated at:** {datetime.now().isoformat()}
"""
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"\n{Colors.BLUE}Trader Report Generated:{Colors.RESET}")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")
    
    return json_file, md_file

def main():
    """Main trader testing"""
    print_header("TRADER PERSPECTIVE APP TESTING")
    
    # Check backend
    if not check_backend():
        print(f"{Colors.RED}Backend not running! Please start backend first.{Colors.RESET}")
        return 1
    
    print(f"{Colors.GREEN}Backend is running{Colors.RESET}\n")
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "scenarios": {},
        "data_quality": False,
        "performance": {},
        "overall_pass": False
    }
    
    # 1. Test trader scenarios
    scenario_results, scenarios_pass = test_trader_scenarios()
    all_results["scenarios"] = {
        "details": scenario_results,
        "passed": sum(1 for r in scenario_results.values() if r["passed"]),
        "total": len(scenario_results),
        "all_critical_pass": scenarios_pass
    }
    
    # 2. Test data quality
    data_quality_pass = test_data_quality()
    all_results["data_quality"] = data_quality_pass
    
    # 3. Test performance
    perf_results, perf_pass = test_performance_for_trading()
    all_results["performance"] = {
        "results": perf_results,
        "all_pass": perf_pass
    }
    
    # Overall assessment
    all_results["overall_pass"] = scenarios_pass and data_quality_pass and perf_pass
    
    # Generate report
    generate_trader_report(all_results)
    
    # Final summary
    print_header("FINAL TRADER ASSESSMENT")
    
    print(f"Trader Scenarios: {all_results['scenarios']['passed']}/{all_results['scenarios']['total']} passed")
    print(f"Data Quality: {Colors.GREEN if data_quality_pass else Colors.RED}{'PASS' if data_quality_pass else 'FAIL'}{Colors.RESET}")
    print(f"Performance: {Colors.GREEN if perf_pass else Colors.RED}{'PASS' if perf_pass else 'FAIL'}{Colors.RESET}")
    
    if all_results["overall_pass"]:
        print(f"\n{Colors.GREEN}{Colors.BOLD}APP IS READY FOR TRADER USE! [PASS]{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some improvements needed before trader use{Colors.RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
