"""
Dashboard Content Analysis - Full Testing and Analysis
Accesses dashboard, tests all tabs, and analyzes all content
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pytz

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
IST = pytz.timezone("Asia/Kolkata")


class DashboardAnalyzer:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(IST).isoformat(),
            "backend_status": None,
            "frontend_status": None,
            "tabs": {},
            "api_data": {},
            "content_analysis": {},
            "issues": [],
            "recommendations": [],
        }

    def check_services(self):
        """Check if backend and frontend are running"""
        print("=" * 80)
        print("🔍 CHECKING SERVICES")
        print("=" * 80)

        # Check backend
        try:
            response = requests.get(f"{API_BASE}/api/status", timeout=5)
            if response.status_code == 200:
                self.results["backend_status"] = "running"
                print("✅ Backend: RUNNING")
            else:
                self.results["backend_status"] = f"error_{response.status_code}"
                print(f"⚠️  Backend: ERROR (Status {response.status_code})")
        except Exception as e:
            self.results["backend_status"] = "not_running"
            print(f"❌ Backend: NOT RUNNING - {e}")
            return False

        # Check frontend
        try:
            response = requests.get(FRONTEND_BASE, timeout=5)
            if response.status_code == 200:
                self.results["frontend_status"] = "running"
                print("✅ Frontend: RUNNING")
            else:
                self.results["frontend_status"] = f"error_{response.status_code}"
                print(f"⚠️  Frontend: ERROR (Status {response.status_code})")
        except Exception as e:
            self.results["frontend_status"] = "not_running"
            print(f"❌ Frontend: NOT RUNNING - {e}")
            return False

        return True

    def analyze_tab(self, tab_path, tab_name):
        """Analyze a dashboard tab"""
        print(f"\n📄 Analyzing: {tab_name} ({tab_path})")

        try:
            url = f"{FRONTEND_BASE}{tab_path}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                self.results["tabs"][tab_name] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": "Failed to load",
                }
                return

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract key information
            title = soup.find("title")
            title_text = title.text if title else "No title"

            # Check for React app
            react_root = soup.find(id="root") or soup.find(class_=lambda x: x and "root" in x.lower())
            has_react = react_root is not None

            # Check for common dashboard elements
            has_nav = soup.find("nav") is not None
            has_main = soup.find("main") is not None

            # Extract text content
            text_content = soup.get_text()
            word_count = len(text_content.split())

            # Check for errors in console (look for error patterns in HTML)
            has_errors = "error" in text_content.lower() and "boundary" not in text_content.lower()

            # Check for loading states
            has_loading = "loading" in text_content.lower() or "Loading" in text_content

            tab_analysis = {
                "status": "ok",
                "status_code": 200,
                "title": title_text,
                "has_react": has_react,
                "has_nav": has_nav,
                "has_main": has_main,
                "word_count": word_count,
                "has_errors": has_errors,
                "has_loading": has_loading,
                "url": url,
            }

            self.results["tabs"][tab_name] = tab_analysis

            status_icon = "✅" if has_react and not has_errors else "⚠️"
            print(f"  {status_icon} Status: OK | React: {has_react} | Words: {word_count} | Errors: {has_errors}")

        except Exception as e:
            self.results["tabs"][tab_name] = {"status": "error", "error": str(e)}
            print(f"  ❌ Error: {e}")

    def analyze_api_data(self):
        """Analyze data from all API endpoints"""
        print("\n" + "=" * 80)
        print("📊 ANALYZING API DATA")
        print("=" * 80)

        endpoints = {
            "health": "/api/health",
            "chain_nifty": "/api/chain/NIFTY",
            "signals": "/api/signal/top",
            "positions": "/api/positions",
            "pnl": "/api/pnl",
            "qc": "/api/qc",
            "perf": "/api/perf",
            "alerts": "/api/alerts/recent",
            "risk": "/api/risk/portfolio",
        }

        for name, endpoint in endpoints.items():
            try:
                print(f"\n  📡 {name.upper()}: {endpoint}")
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # Analyze data structure
                    analysis = {
                        "status": "ok",
                        "status_code": 200,
                        "has_data": data is not None,
                        "data_type": type(data).__name__,
                        "keys": list(data.keys()) if isinstance(data, dict) else "N/A",
                        "data_source": data.get("data_source", "unknown") if isinstance(data, dict) else "unknown",
                        "response_size": len(json.dumps(data)),
                    }

                    # Specific analysis based on endpoint
                    if name == "health":
                        analysis["market_status"] = data.get("market_status", "unknown")
                        analysis["broker_status"] = data.get("broker_status", "unknown")
                        analysis["total_pnl"] = data.get("total_pnl", 0)
                        analysis["open_positions"] = data.get("open_positions", 0)
                        print(f"    ✅ Market: {analysis['market_status']} | Broker: {analysis['broker_status']}")
                        print(f"    💰 PnL: ₹{analysis['total_pnl']:.2f} | Positions: {analysis['open_positions']}")

                    elif name == "chain_nifty":
                        analysis["contracts_count"] = len(data.get("contracts", []))
                        analysis["spot_price"] = data.get("spot", 0)
                        analysis["pcr"] = data.get("pcr", 0)
                        print(
                            f"    ✅ Contracts: {analysis['contracts_count']} | Spot: ₹{analysis['spot_price']:.2f} | PCR: {analysis['pcr']:.2f}"
                        )

                    elif name == "signals":
                        analysis["has_signal"] = data.get("action") == "TRADE"
                        analysis["confidence"] = data.get("confidence", 0)
                        print(f"    ✅ Signal: {analysis['has_signal']} | Confidence: {analysis['confidence']:.2f}")

                    elif name == "positions":
                        positions = data.get("positions", [])
                        analysis["positions_count"] = len(positions) if isinstance(positions, list) else 0
                        print(f"    ✅ Positions: {analysis['positions_count']}")

                    elif name == "pnl":
                        analysis["total_pnl"] = data.get("total_pnl", 0)
                        analysis["daily_pnl"] = data.get("daily_pnl", 0)
                        print(f"    ✅ Total PnL: ₹{analysis['total_pnl']:.2f} | Daily: ₹{analysis['daily_pnl']:.2f}")

                    self.results["api_data"][name] = analysis

                else:
                    self.results["api_data"][name] = {"status": "error", "status_code": response.status_code}
                    print(f"    ❌ Error: HTTP {response.status_code}")

            except Exception as e:
                self.results["api_data"][name] = {"status": "error", "error": str(e)}
                print(f"    ❌ Error: {e}")

    def analyze_content_consistency(self):
        """Analyze content consistency across tabs and APIs"""
        print("\n" + "=" * 80)
        print("🔍 ANALYZING CONTENT CONSISTENCY")
        print("=" * 80)

        consistency_checks = []

        # Check PnL consistency
        health_pnl = self.results["api_data"].get("health", {}).get("total_pnl", None)
        pnl_total = self.results["api_data"].get("pnl", {}).get("total_pnl", None)

        if health_pnl is not None and pnl_total is not None:
            diff = abs(health_pnl - pnl_total)
            if diff < 100:  # Allow small differences
                consistency_checks.append(
                    {
                        "check": "PnL Consistency",
                        "status": "✅ PASS",
                        "health_pnl": health_pnl,
                        "pnl_total": pnl_total,
                        "difference": diff,
                    }
                )
                print(f"  ✅ PnL Consistency: Health={health_pnl:.2f}, PnL={pnl_total:.2f}, Diff={diff:.2f}")
            else:
                consistency_checks.append(
                    {
                        "check": "PnL Consistency",
                        "status": "⚠️ WARNING",
                        "health_pnl": health_pnl,
                        "pnl_total": pnl_total,
                        "difference": diff,
                    }
                )
                print(f"  ⚠️  PnL Inconsistency: Health={health_pnl:.2f}, PnL={pnl_total:.2f}, Diff={diff:.2f}")

        # Check data source consistency
        data_sources = []
        for api_name, api_data in self.results["api_data"].items():
            if isinstance(api_data, dict) and "data_source" in api_data:
                data_sources.append(api_data["data_source"])

        unique_sources = set(data_sources)
        if len(unique_sources) <= 2:  # real, synthetic, or unknown
            consistency_checks.append(
                {"check": "Data Source Consistency", "status": "✅ PASS", "sources": list(unique_sources)}
            )
            print(f"  ✅ Data Sources: {', '.join(unique_sources)}")
        else:
            consistency_checks.append(
                {"check": "Data Source Consistency", "status": "⚠️ WARNING", "sources": list(unique_sources)}
            )
            print(f"  ⚠️  Multiple Data Sources: {', '.join(unique_sources)}")

        self.results["content_analysis"]["consistency"] = consistency_checks

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("📊 GENERATING ANALYSIS REPORT")
        print("=" * 80)

        # Count issues
        tab_errors = sum(1 for t in self.results["tabs"].values() if t.get("status") == "error")
        api_errors = sum(1 for a in self.results["api_data"].values() if a.get("status") == "error")

        # Generate summary
        summary = {
            "backend": self.results["backend_status"],
            "frontend": self.results["frontend_status"],
            "tabs_tested": len(self.results["tabs"]),
            "tabs_ok": len(self.results["tabs"]) - tab_errors,
            "tabs_errors": tab_errors,
            "apis_tested": len(self.results["api_data"]),
            "apis_ok": len(self.results["api_data"]) - api_errors,
            "apis_errors": api_errors,
            "overall_status": "✅ OK" if tab_errors == 0 and api_errors == 0 else "⚠️ ISSUES FOUND",
        }

        print(f"\n📊 SUMMARY:")
        print(f"  Backend: {summary['backend']}")
        print(f"  Frontend: {summary['frontend']}")
        print(f"  Tabs: {summary['tabs_ok']}/{summary['tabs_tested']} OK")
        print(f"  APIs: {summary['apis_ok']}/{summary['apis_tested']} OK")
        print(f"  Overall: {summary['overall_status']}")

        # Save results
        results_file = "outputs/dashboard_content_analysis.json"
        os.makedirs("outputs", exist_ok=True)

        self.results["summary"] = summary

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Full analysis saved to: {results_file}")

        return summary

    def run_full_analysis(self):
        """Run complete dashboard analysis"""
        print("=" * 80)
        print("🚀 DASHBOARD CONTENT ANALYSIS")
        print("=" * 80)
        print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}\n")

        # 1. Check services
        if not self.check_services():
            print("\n❌ Services not running. Please start backend and frontend.")
            return

        # 2. Analyze all tabs
        print("\n" + "=" * 80)
        print("🖥️  ANALYZING DASHBOARD TABS")
        print("=" * 80)

        tabs = [
            ("/", "Overview"),
            ("/chain", "Chain Analytics"),
            ("/signals", "Signals"),
            ("/trading", "Paper Trading"),
            ("/alerts", "Alerts"),
            ("/risk", "Risk Dashboard"),
            ("/charts", "Advanced Charts"),
            ("/ml", "ML Performance"),
            ("/model", "Model Behavior"),
            ("/control", "Control Plane"),
        ]

        for path, name in tabs:
            self.analyze_tab(path, name)

        # 3. Analyze API data
        self.analyze_api_data()

        # 4. Analyze content consistency
        self.analyze_content_consistency()

        # 5. Generate report
        summary = self.generate_report()

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)

        return summary if summary else {"overall_status": "❌ ERROR"}


if __name__ == "__main__":
    try:
        analyzer = DashboardAnalyzer()
        summary = analyzer.run_full_analysis()

        if summary["overall_status"] == "✅ OK":
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
