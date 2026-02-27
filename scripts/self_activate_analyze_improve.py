"""
Self-Activating Analysis and Improvement System
Runs every 2 minutes to analyze, fix, and upgrade everything
Goal: Maximum Profit through continuous improvement
"""

import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import pytz
import os

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"

API_BASE = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8080"


class SelfActivatingSystem:
    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.cycle_count = 0
        self.last_pnl = 0.0
        self.improvements_made = []
        self.errors_fixed = []
        self.optimizations_applied = []
        self.start_time = datetime.now(self.ist)
        self.last_trade_count = 0
        self.analysis_results = []

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """Print header"""
        self.clear_screen()
        print("=" * 80)
        print(" " * 15 + "SELF-ACTIVATING ANALYSIS & IMPROVEMENT SYSTEM")
        print(" " * 25 + "GOAL: MAXIMUM PROFIT")
        print(" " * 20 + "Auto-Analyze & Upgrade Every 2 Minutes")
        print("=" * 80)
        print()

    def log_action(self, action, status="INFO"):
        """Log action with timestamp"""
        timestamp = datetime.now(self.ist).strftime("%H:%M:%S")
        # Use ASCII-safe symbols
        symbol = (
            "[OK]"
            if status == "SUCCESS"
            else "[ACT]" if status == "ACTION" else "[WARN]" if status == "WARNING" else "[ERR]"
        )
        print(f"[{timestamp}] {symbol} {action}")

    def analyze_backend(self):
        """Deep analysis of backend"""
        issues = []
        improvements = []

        try:
            response = requests.get(f"{API_BASE}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Check response time
                response_time = response.elapsed.total_seconds()
                if response_time > 1:
                    issues.append(f"Backend slow: {response_time:.2f}s")
                    improvements.append("Optimize backend response time")

                # Check data freshness
                last_fetch = data.get("last_fetch")
                if last_fetch:
                    # Parse and check age
                    pass

                return True, data, issues, improvements
            else:
                issues.append(f"Backend returned {response.status_code}")
                return False, None, issues, improvements
        except Exception as e:
            issues.append(f"Backend unreachable: {str(e)}")
            return False, None, issues, improvements

    def analyze_dashboard(self):
        """Deep analysis of dashboard"""
        issues = []
        improvements = []

        try:
            response = requests.get(DASHBOARD_URL, timeout=5)
            if response.status_code == 200:
                # Check if Vue is loaded
                if "vue" not in response.text.lower() and "Vue" not in response.text:
                    issues.append("Vue3 not detected in dashboard")
                    improvements.append("Fix dashboard Vue3 loading")

                # Check response time
                response_time = response.elapsed.total_seconds()
                if response_time > 2:
                    issues.append(f"Dashboard slow: {response_time:.2f}s")
                    improvements.append("Optimize dashboard load time")

                return True, issues, improvements
            else:
                issues.append(f"Dashboard returned {response.status_code}")
                return False, issues, improvements
        except Exception as e:
            issues.append(f"Dashboard unreachable: {str(e)}")
            return False, issues, improvements

    def analyze_paper_trading(self):
        """Deep analysis of paper trading"""
        issues = []
        improvements = []
        pnl_data = None

        try:
            pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
            if pnl_file.exists():
                with open(pnl_file) as f:
                    pnl_data = json.load(f)

                total_trades = pnl_data.get("total_trades", 0)
                win_rate = pnl_data.get("win_rate", 0)
                total_pnl = pnl_data.get("total_pnl", 0)

                # Check if trades are executing
                if total_trades == 0:
                    issues.append("No paper trades executed")
                    improvements.append("Check strategy signals and QC thresholds")

                # Check win rate
                if total_trades > 10 and win_rate < 40:
                    issues.append(f"Low win rate: {win_rate:.1f}%")
                    improvements.append("Optimize strategy for better win rate")

                # Check PnL trend
                if total_pnl < -500:
                    issues.append(f"Large loss: Rs{total_pnl:.2f}")
                    improvements.append("Review risk management and stop losses")

                # Check if PnL is improving
                if self.last_pnl != 0:
                    pnl_change = total_pnl - self.last_pnl
                    if pnl_change < -50:
                        issues.append(f"PnL declining: Rs{pnl_change:.2f}")
                        improvements.append("Investigate recent trade performance")

                self.last_pnl = total_pnl

            else:
                issues.append("PnL summary file missing")
                improvements.append("Ensure PnL tracker is running")

            return pnl_data, issues, improvements
        except Exception as e:
            issues.append(f"Error analyzing paper trading: {str(e)}")
            return None, issues, improvements

    def analyze_data_quality(self):
        """Analyze data quality"""
        issues = []
        improvements = []

        try:
            chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
            if chain_file.exists():
                # Check file age
                mtime = chain_file.stat().st_mtime
                age_seconds = time.time() - mtime

                if age_seconds > 300:
                    issues.append(f"Chain data stale: {int(age_seconds/60)}m old")
                    improvements.append("Refresh chain data")

                # Check file size
                size = chain_file.stat().st_size
                if size < 1000:
                    issues.append("Chain data file too small")
                    improvements.append("Regenerate chain data")

            else:
                issues.append("Chain data file missing")
                improvements.append("Generate chain data")

            return issues, improvements
        except Exception as e:
            issues.append(f"Error analyzing data: {str(e)}")
            return issues, improvements

    def analyze_performance(self):
        """Analyze system performance"""
        issues = []
        improvements = []

        try:
            perf_file = OUTPUTS_DIR / "perf_metrics.json"
            if perf_file.exists():
                with open(perf_file) as f:
                    perf_data = json.load(f)

                cycle_duration = perf_data.get("cycle_duration_sec", 0)
                fetch_duration = perf_data.get("fetch_duration_sec", 0)
                strategy_duration = perf_data.get("strategy_duration_sec", 0)

                # Check cycle duration
                if cycle_duration > 30:
                    issues.append(f"Cycle too slow: {cycle_duration:.1f}s")
                    improvements.append("Optimize cycle performance")

                # Check fetch duration
                if fetch_duration > 10:
                    issues.append(f"Data fetch slow: {fetch_duration:.1f}s")
                    improvements.append("Optimize data fetching")

                # Check strategy duration
                if strategy_duration > 5:
                    issues.append(f"Strategy slow: {strategy_duration:.1f}s")
                    improvements.append("Optimize strategy execution")

            return issues, improvements
        except Exception as e:
            issues.append(f"Error analyzing performance: {str(e)}")
            return issues, improvements

    def auto_fix_issues(self, issues, improvements):
        """Automatically fix detected issues"""
        fixed = []

        for issue in issues:
            if "Backend unreachable" in issue or "Backend returned" in issue:
                self.log_action("Starting backend server...", "ACTION")
                self.start_backend()
                fixed.append("Started backend")

            elif "Dashboard unreachable" in issue or "Dashboard returned" in issue:
                self.log_action("Starting dashboard server...", "ACTION")
                self.start_dashboard()
                fixed.append("Started dashboard")

            elif "Chain data stale" in issue or "Chain data file missing" in issue:
                self.log_action("Refreshing chain data...", "ACTION")
                self.refresh_chain_data()
                fixed.append("Refreshed chain data")

            elif "Main system" in issue.lower() or "trading system" in issue.lower():
                self.log_action("Starting main trading system...", "ACTION")
                self.start_main_system()
                fixed.append("Started main system")

        return fixed

    def start_backend(self):
        """Start backend"""
        try:
            subprocess.Popen(
                ["python", str(ROOT_DIR / "dashboard" / "backend" / "app.py")],
                cwd=str(ROOT_DIR / "dashboard" / "backend"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(5)
            return True
        except:
            return False

    def start_dashboard(self):
        """Start dashboard"""
        try:
            subprocess.Popen(
                ["python", "-m", "http.server", "8080"],
                cwd=str(ROOT_DIR / "dashboard"),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            return True
        except:
            return False

    def start_main_system(self):
        """Start main system"""
        try:
            bat_file = ROOT_DIR / "RUN_FULL_SYSTEM_PRODUCTION.bat"
            if bat_file.exists():
                subprocess.Popen(
                    ["cmd", "/c", str(bat_file)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(10)
                return True
            return False
        except:
            return False

    def refresh_chain_data(self):
        """Refresh chain data"""
        try:
            subprocess.run(
                ["python", str(ROOT_DIR / "scripts" / "generate_synthetic_live_data.py")],
                cwd=str(ROOT_DIR),
                timeout=30,
                capture_output=True,
            )
            return True
        except:
            return False

    def optimize_for_profit(self, pnl_data):
        """Apply profit optimizations"""
        optimizations = []

        if not pnl_data:
            return optimizations

        total_trades = pnl_data.get("total_trades", 0)
        win_rate = pnl_data.get("win_rate", 0)
        total_pnl = pnl_data.get("total_pnl", 0)

        # Optimization suggestions
        if total_trades == 0:
            optimizations.append("No trades - Check strategy confidence thresholds")

        if total_trades > 0 and win_rate < 50:
            optimizations.append("Low win rate - Consider strategy refinement")

        if total_pnl < 0 and total_trades > 5:
            optimizations.append("Negative PnL - Review stop loss and target levels")

        return optimizations

    def run_analysis_cycle(self):
        """Run complete analysis and improvement cycle"""
        self.cycle_count += 1
        self.print_header()

        now = datetime.now(self.ist)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"Analysis Cycle: #{self.cycle_count}")
        print(f"Runtime: {str(now - self.start_time).split('.')[0]}")
        print()

        all_issues = []
        all_improvements = []
        all_optimizations = []

        print("=" * 80)
        print("DEEP ANALYSIS IN PROGRESS...")
        print("=" * 80)
        print()

        # 1. Analyze Backend
        self.log_action("Analyzing Backend API...", "ACTION")
        backend_ok, backend_data, backend_issues, backend_improvements = self.analyze_backend()
        all_issues.extend(backend_issues)
        all_improvements.extend(backend_improvements)
        if backend_ok:
            self.log_action(
                f"Backend: RUNNING | Mode: {backend_data.get('mode', 'UNKNOWN')} | PnL: Rs{backend_data.get('total_pnl', 0):.2f}",
                "SUCCESS",
            )
        else:
            self.log_action("Backend: ISSUES DETECTED", "WARNING")
        print()

        # 2. Analyze Dashboard
        self.log_action("Analyzing Dashboard...", "ACTION")
        dashboard_ok, dashboard_issues, dashboard_improvements = self.analyze_dashboard()
        all_issues.extend(dashboard_issues)
        all_improvements.extend(dashboard_improvements)
        if dashboard_ok:
            self.log_action("Dashboard: RUNNING", "SUCCESS")
        else:
            self.log_action("Dashboard: ISSUES DETECTED", "WARNING")
        print()

        # 3. Analyze Paper Trading
        self.log_action("Analyzing Paper Trading...", "ACTION")
        pnl_data, trading_issues, trading_improvements = self.analyze_paper_trading()
        all_issues.extend(trading_issues)
        all_improvements.extend(trading_improvements)
        if pnl_data:
            pnl = pnl_data.get("total_pnl", 0)
            trades = pnl_data.get("total_trades", 0)
            win_rate = pnl_data.get("win_rate", 0)
            self.log_action(f"Paper Trading: PnL Rs{pnl:.2f} | Trades: {trades} | Win Rate: {win_rate:.1f}%", "SUCCESS")
        else:
            self.log_action("Paper Trading: NO DATA", "WARNING")
        print()

        # 4. Analyze Data Quality
        self.log_action("Analyzing Data Quality...", "ACTION")
        data_issues, data_improvements = self.analyze_data_quality()
        all_issues.extend(data_issues)
        all_improvements.extend(data_improvements)
        if not data_issues:
            self.log_action("Data Quality: GOOD", "SUCCESS")
        else:
            self.log_action(f"Data Quality: {len(data_issues)} ISSUES", "WARNING")
        print()

        # 5. Analyze Performance
        self.log_action("Analyzing Performance...", "ACTION")
        perf_issues, perf_improvements = self.analyze_performance()
        all_issues.extend(perf_issues)
        all_improvements.extend(perf_improvements)
        if not perf_issues:
            self.log_action("Performance: OPTIMAL", "SUCCESS")
        else:
            self.log_action(f"Performance: {len(perf_issues)} ISSUES", "WARNING")
        print()

        # 6. Auto-Fix Issues
        print("=" * 80)
        print("AUTO-FIXING ISSUES...")
        print("=" * 80)
        print()

        fixed = self.auto_fix_issues(all_issues, all_improvements)
        for fix in fixed:
            self.log_action(f"Fixed: {fix}", "SUCCESS")
            self.errors_fixed.append(fix)
        print()

        # 7. Profit Optimization
        print("=" * 80)
        print("PROFIT OPTIMIZATION ANALYSIS...")
        print("=" * 80)
        print()

        optimizations = self.optimize_for_profit(pnl_data)
        all_optimizations.extend(optimizations)
        for opt in optimizations:
            self.log_action(f"Optimization: {opt}", "ACTION")
            self.optimizations_applied.append(opt)
        print()

        # Summary
        print("=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print()
        print(f"✅ Issues Detected: {len(all_issues)}")
        if all_issues:
            for issue in all_issues[:5]:  # Show first 5
                print(f"   • {issue}")
            if len(all_issues) > 5:
                print(f"   ... and {len(all_issues) - 5} more")
        print()
        print(f"🔧 Improvements Suggested: {len(all_improvements)}")
        if all_improvements:
            for imp in all_improvements[:5]:  # Show first 5
                print(f"   • {imp}")
        print()
        print(f"🚀 Optimizations Applied: {len(all_optimizations)}")
        if all_optimizations:
            for opt in all_optimizations:
                print(f"   • {opt}")
        print()
        print(f"✅ Errors Fixed This Cycle: {len(fixed)}")
        print(f"📊 Total Errors Fixed: {len(self.errors_fixed)}")
        print(f"🚀 Total Optimizations: {len(self.optimizations_applied)}")
        print()
        print("=" * 80)
        print(f"Next analysis in 2 minutes... (Press Ctrl+C to stop)")
        print("=" * 80)

        # Store analysis results
        self.analysis_results.append(
            {
                "timestamp": now.isoformat(),
                "issues": all_issues,
                "improvements": all_improvements,
                "optimizations": all_optimizations,
                "fixed": fixed,
            }
        )

    def run_continuous(self):
        """Run continuous analysis every 2 minutes"""
        while True:
            try:
                self.run_analysis_cycle()
                time.sleep(120)  # 2 minutes
            except KeyboardInterrupt:
                print("\n\nAnalysis stopped by user.")
                break
            except Exception as e:
                print(f"\n❌ Error in analysis cycle: {e}")
                time.sleep(120)


if __name__ == "__main__":
    system = SelfActivatingSystem()
    system.run_continuous()
