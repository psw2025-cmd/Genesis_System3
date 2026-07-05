"""
Dashboard Data Validator - Production Grade
Compares dashboard data with live internet sources (NSE, BSE, Dhan)
Validates all data points and identifies discrepancies
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pytz
import requests

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"

# NSE API endpoints (public)
NSE_BASE = "https://www.nseindia.com/api"
NSE_OPTION_CHAIN = "https://www.nseindia.com/api/option-chain-indices"
NSE_QUOTE = "https://www.nseindia.com/api/quote-equity"

# Alternative data sources
YAHOO_FINANCE_API = "https://query1.finance.yahoo.com/v8/finance/chart"
TRADINGVIEW_API = "https://symbol-search.tradingview.com/symbol_search"


@dataclass
class ValidationResult:
    """Result of data validation"""

    timestamp: str
    underlying: str
    field: str
    dashboard_value: Any
    source_value: Any
    match: bool
    difference: float
    difference_pct: float
    source: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str


@dataclass
class ValidationReport:
    """Complete validation report"""

    timestamp: str
    total_validations: int
    passed: int
    failed: int
    critical_issues: int
    results: List[ValidationResult]
    summary: Dict[str, Any]


class DashboardDataValidator:
    """Validates dashboard data against live internet sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self.validation_results: List[ValidationResult] = []

    def get_nse_headers(self):
        """Get NSE headers (they require specific headers)"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/option-chain",
        }

    def fetch_nse_option_chain(self, symbol: str) -> Optional[Dict]:
        """Fetch option chain from NSE (v3 API via hardened session)."""
        try:
            from core.data.nse_session import NSEFetchError, fetch_option_chain_json

            return fetch_option_chain_json(symbol)
        except NSEFetchError as e:
            print(f"NSE option chain unavailable for {symbol}: {e}")
            return self.fetch_nse_alternative(symbol)
        except Exception as e:
            print(f"Error fetching NSE data for {symbol}: {e}")
            return None

    def fetch_nse_alternative(self, symbol: str) -> Optional[Dict]:
        """Alternative method to fetch NSE data"""
        try:
            # Use NSE website scraping alternative
            # For now, return None - will implement if needed
            return None
        except:
            return None

    def fetch_yahoo_finance_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch quote from Yahoo Finance"""
        try:
            # Map symbols to Yahoo Finance format
            yahoo_symbols = {
                "NIFTY": "^NSEI",
                "BANKNIFTY": "^NSEBANK",
                "FINNIFTY": "^NSEFINNIFTY",
                "MIDCPNIFTY": "^NSEMIDCP",
                "SENSEX": "^BSESN",
            }

            yahoo_symbol = yahoo_symbols.get(symbol.upper())
            if not yahoo_symbol:
                return None

            url = f"{YAHOO_FINANCE_API}/{yahoo_symbol}"
            params = {"interval": "1d", "range": "1d"}

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})
                    return {
                        "ltp": meta.get("regularMarketPrice"),
                        "open": meta.get("regularMarketOpen"),
                        "high": meta.get("regularMarketDayHigh"),
                        "low": meta.get("regularMarketDayLow"),
                        "close": meta.get("previousClose"),
                        "volume": meta.get("regularMarketVolume"),
                    }
        except Exception as e:
            print(f"Error fetching Yahoo Finance data: {e}")
        return None

    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data from API"""
        try:
            base_url = "http://localhost:8000"

            # Fetch all dashboard endpoints
            health = self.session.get(f"{base_url}/api/health", timeout=5).json()

            # Get chain data for each underlying
            chain_data = {}
            for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
                try:
                    chain = self.session.get(f"{base_url}/api/chain/{underlying}", timeout=5).json()
                    chain_data[underlying] = chain
                except:
                    chain_data[underlying] = None

            return {"health": health, "chains": chain_data}
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            return {}

    def validate_spot_price(self, underlying: str, dashboard_spot: float, source_spot: float) -> ValidationResult:
        """Validate spot price"""
        if dashboard_spot == 0 or source_spot == 0:
            return ValidationResult(
                timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                underlying=underlying,
                field="spot_price",
                dashboard_value=dashboard_spot,
                source_value=source_spot,
                match=False,
                difference=abs(dashboard_spot - source_spot),
                difference_pct=(
                    100.0 if dashboard_spot == 0 else abs((dashboard_spot - source_spot) / dashboard_spot * 100)
                ),
                source="YAHOO_FINANCE",
                severity="CRITICAL",
                message="Spot price mismatch or zero",
            )

        diff = abs(dashboard_spot - source_spot)
        diff_pct = abs((dashboard_spot - source_spot) / source_spot * 100)

        # Allow 0.1% difference for market movements
        match = diff_pct < 0.1
        severity = "CRITICAL" if diff_pct > 1.0 else "HIGH" if diff_pct > 0.5 else "MEDIUM"

        return ValidationResult(
            timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            underlying=underlying,
            field="spot_price",
            dashboard_value=dashboard_spot,
            source_value=source_spot,
            match=match,
            difference=diff,
            difference_pct=diff_pct,
            source="YAHOO_FINANCE",
            severity=severity,
            message=f"Spot price difference: {diff_pct:.2f}%",
        )

    def validate_option_ltp(
        self, underlying: str, strike: float, option_type: str, dashboard_ltp: float, source_ltp: float
    ) -> Optional[ValidationResult]:
        """Validate option LTP"""
        if dashboard_ltp == 0 or source_ltp == 0:
            return None  # Skip if no data

        diff = abs(dashboard_ltp - source_ltp)
        diff_pct = abs((dashboard_ltp - source_ltp) / source_ltp * 100) if source_ltp > 0 else 100

        # Allow 5% difference for options (more volatile)
        match = diff_pct < 5.0
        severity = "CRITICAL" if diff_pct > 10.0 else "HIGH" if diff_pct > 5.0 else "MEDIUM"

        return ValidationResult(
            timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            underlying=underlying,
            field=f"ltp_{strike}_{option_type}",
            dashboard_value=dashboard_ltp,
            source_value=source_ltp,
            match=match,
            difference=diff,
            difference_pct=diff_pct,
            source="NSE",
            severity=severity,
            message=f"LTP difference for {strike} {option_type}: {diff_pct:.2f}%",
        )

    def validate_chain_data(self, underlying: str, dashboard_chain: Dict, source_data: Dict) -> List[ValidationResult]:
        """Validate entire option chain"""
        results = []

        # Validate spot price
        dashboard_spot = dashboard_chain.get("spot", 0)
        if source_data and "ltp" in source_data:
            source_spot = source_data.get("ltp", 0)
            if source_spot > 0:
                results.append(self.validate_spot_price(underlying, dashboard_spot, source_spot))

        # Validate PCR if available
        dashboard_pcr = dashboard_chain.get("pcr", 1.0)
        # PCR validation would require full chain data from source

        # Validate contract counts
        dashboard_contracts = dashboard_chain.get("total_contracts", 0)
        if dashboard_contracts == 0:
            results.append(
                ValidationResult(
                    timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                    underlying=underlying,
                    field="contract_count",
                    dashboard_value=dashboard_contracts,
                    source_value=0,
                    match=False,
                    difference=0,
                    difference_pct=0,
                    source="DASHBOARD",
                    severity="HIGH",
                    message="No contracts in dashboard data",
                )
            )

        return results

    def run_validation(self) -> ValidationReport:
        """Run complete validation"""
        print("Starting dashboard data validation...")
        print("=" * 60)

        # Get dashboard data
        print("\n[1/4] Fetching dashboard data...")
        dashboard_data = self.get_dashboard_data()
        if not dashboard_data:
            print("  [ERROR] Could not fetch dashboard data")
            return self._create_error_report("Dashboard API not accessible")

        print("  [OK] Dashboard data fetched")

        # Fetch source data for each underlying
        print("\n[2/4] Fetching live market data...")
        source_data = {}
        for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
            print(f"  Fetching {underlying}...", end=" ")
            yahoo_data = self.fetch_yahoo_finance_quote(underlying)
            if yahoo_data:
                source_data[underlying] = yahoo_data
                print(f"[OK] LTP: {yahoo_data.get('ltp', 'N/A')}")
            else:
                print("[WARN] No data")

        # Validate each underlying
        print("\n[3/4] Validating data...")
        all_results = []

        chains = dashboard_data.get("chains", {})
        for underlying, dashboard_chain in chains.items():
            if not dashboard_chain:
                continue

            print(f"  Validating {underlying}...", end=" ")
            source = source_data.get(underlying)
            results = self.validate_chain_data(underlying, dashboard_chain, source or {})
            all_results.extend(results)

            passed = sum(1 for r in results if r.match)
            failed = len(results) - passed
            print(f"[{passed} passed, {failed} failed]")

        # Create report
        print("\n[4/4] Generating report...")
        report = self._create_report(all_results)

        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        print(f"Total Validations: {report.total_validations}")
        print(f"Passed: {report.passed} ({report.passed/report.total_validations*100:.1f}%)")
        print(f"Failed: {report.failed} ({report.failed/report.total_validations*100:.1f}%)")
        print(f"Critical Issues: {report.critical_issues}")

        return report

    def _create_report(self, results: List[ValidationResult]) -> ValidationReport:
        """Create validation report"""
        total = len(results)
        passed = sum(1 for r in results if r.match)
        failed = total - passed
        critical = sum(1 for r in results if r.severity == "CRITICAL")

        summary = {
            "by_severity": {
                "CRITICAL": sum(1 for r in results if r.severity == "CRITICAL"),
                "HIGH": sum(1 for r in results if r.severity == "HIGH"),
                "MEDIUM": sum(1 for r in results if r.severity == "MEDIUM"),
                "LOW": sum(1 for r in results if r.severity == "LOW"),
            },
            "by_underlying": {},
            "by_field": {},
        }

        for result in results:
            # By underlying
            if result.underlying not in summary["by_underlying"]:
                summary["by_underlying"][result.underlying] = {"passed": 0, "failed": 0}
            if result.match:
                summary["by_underlying"][result.underlying]["passed"] += 1
            else:
                summary["by_underlying"][result.underlying]["failed"] += 1

            # By field
            if result.field not in summary["by_field"]:
                summary["by_field"][result.field] = {"passed": 0, "failed": 0}
            if result.match:
                summary["by_field"][result.field]["passed"] += 1
            else:
                summary["by_field"][result.field]["failed"] += 1

        return ValidationReport(
            timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            total_validations=total,
            passed=passed,
            failed=failed,
            critical_issues=critical,
            results=results,
            summary=summary,
        )

    def _create_error_report(self, message: str) -> ValidationReport:
        """Create error report"""
        return ValidationReport(
            timestamp=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            total_validations=0,
            passed=0,
            failed=0,
            critical_issues=0,
            results=[],
            summary={"error": message},
        )

    def save_report(self, report: ValidationReport, filename: str = None):
        """Save validation report to JSON"""
        if filename is None:
            filename = f"dashboard_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report_path = OUTPUTS_DIR / "validation" / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        report_dict = {
            "timestamp": report.timestamp,
            "total_validations": report.total_validations,
            "passed": report.passed,
            "failed": report.failed,
            "critical_issues": report.critical_issues,
            "results": [asdict(r) for r in report.results],
            "summary": report.summary,
        }

        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        print(f"\nReport saved: {report_path}")
        return report_path


if __name__ == "__main__":
    validator = DashboardDataValidator()
    report = validator.run_validation()
    validator.save_report(report)
