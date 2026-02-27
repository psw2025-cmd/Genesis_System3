"""
Production-Grade Option Chain Data Validation and Auto-Correction

Validates option chain CSV files and automatically re-fetches missing data
to ensure completeness before downstream processing.
"""

import os
import sys
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


class OptionChainValidator:
    """Validates and auto-corrects option chain data."""

    # Mandatory columns for validation
    CRITICAL_COLUMNS = ["ltp", "oi", "bidPrice", "offerPrice", "delta"]

    # Minimum rows expected for NIFTY chain
    MIN_ROWS_NIFTY = 100

    # Maximum NaN rate threshold (10%)
    MAX_NAN_RATE = 0.10

    def __init__(self, broker: Optional[AngelOneBroker] = None):
        """
        Initialize validator.

        Args:
            broker: Optional AngelOneBroker instance (creates new if None)
        """
        self.broker = broker
        self.log_file = ROOT_DIR / "storage" / "logs" / "api_pull_validation.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str, level: str = "INFO"):
        """Log message to file and logger."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")

        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def validate(self, csv_path: str, underlying: str = "NIFTY") -> Dict:
        """
        Validate option chain CSV file.

        Args:
            csv_path: Path to CSV file
            underlying: Underlying name (default: NIFTY)

        Returns:
            dict with validation results:
            {
                "status": "COMPLETE" or "INCOMPLETE",
                "failed_checks": [],
                "nan_rates": {},
                "row_count": 0,
                "details": {}
            }
        """
        self._log(f"Starting validation for {csv_path}")

        if not os.path.exists(csv_path):
            self._log(f"CSV file not found: {csv_path}", "ERROR")
            return {
                "status": "INCOMPLETE",
                "failed_checks": ["FILE_NOT_FOUND"],
                "nan_rates": {},
                "row_count": 0,
                "details": {"error": f"File not found: {csv_path}"},
            }

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self._log(f"Failed to read CSV: {e}", "ERROR")
            return {
                "status": "INCOMPLETE",
                "failed_checks": ["CSV_READ_ERROR"],
                "nan_rates": {},
                "row_count": 0,
                "details": {"error": str(e)},
            }

        row_count = len(df)
        failed_checks = []
        nan_rates = {}
        details = {}

        # Check 1: Row count
        if underlying.upper() == "NIFTY" and row_count < self.MIN_ROWS_NIFTY:
            failed_checks.append(f"ROW_COUNT_LOW: {row_count} < {self.MIN_ROWS_NIFTY}")
            details["row_count"] = row_count

        # Check 2: NaN rates for critical columns
        for col in self.CRITICAL_COLUMNS:
            if col not in df.columns:
                nan_rate = 1.0  # 100% missing if column doesn't exist
                failed_checks.append(f"COLUMN_MISSING: {col}")
            else:
                nan_count = df[col].isna().sum()
                nan_rate = nan_count / row_count if row_count > 0 else 1.0
                nan_rates[col] = nan_rate

                if nan_rate > self.MAX_NAN_RATE:
                    failed_checks.append(f"NAN_RATE_HIGH: {col}={nan_rate:.1%} > {self.MAX_NAN_RATE:.1%}")

        # Check 3: All rows have identical/empty pTime (stale data)
        if "pTime" in df.columns:
            ptime_values = df["pTime"].dropna().unique()
            if len(ptime_values) <= 1:
                failed_checks.append("PTIME_STALE: All rows have identical/empty pTime")
                details["ptime_unique_count"] = len(ptime_values)

        # Check 4: spot_price consistency (check if all rows have same spot)
        if "spot_price" in df.columns:
            spot_values = df["spot_price"].dropna().unique()
            if len(spot_values) > 1:
                failed_checks.append("SPOT_PRICE_INCONSISTENT: Multiple spot prices found")
                details["spot_unique_count"] = len(spot_values)
            elif len(spot_values) == 0:
                failed_checks.append("SPOT_PRICE_MISSING: No spot price data")

        # Determine status
        status = "COMPLETE" if len(failed_checks) == 0 else "INCOMPLETE"

        result = {
            "status": status,
            "failed_checks": failed_checks,
            "nan_rates": nan_rates,
            "row_count": row_count,
            "details": details,
        }

        self._log(f"Validation complete: {status}. Failed checks: {len(failed_checks)}")
        return result

    def correct_missing_data(
        self, csv_path: str, underlying: str = "NIFTY", exchange: str = "NFO", max_retries: int = 3
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Auto-correct missing data by re-fetching from API.

        Args:
            csv_path: Path to CSV file
            underlying: Underlying name
            exchange: Exchange code
            max_retries: Maximum retry attempts

        Returns:
            tuple: (corrected_df, correction_stats)
        """
        self._log(f"Starting data correction for {csv_path}")

        # Initialize broker if not provided
        if self.broker is None:
            try:
                self.broker = AngelOneBroker(allow_data_only=True)
            except Exception as e:
                self._log(f"Failed to initialize broker: {e}", "ERROR")
                return None, {"error": str(e)}

        # Load original data
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            self._log(f"Failed to read CSV: {e}", "ERROR")
            return None, {"error": str(e)}

        correction_stats = {"ltp_fixed": 0, "oi_fixed": 0, "quote_fixed": 0, "greeks_fixed": 0, "attempts": 0}

        # Identify rows with missing critical data
        missing_ltp = df[df["ltp"].isna()].copy()
        missing_oi = df[df["oi"].isna()].copy()
        missing_greeks = df[df["delta"].isna()].copy()

        self._log(f"Found {len(missing_ltp)} rows with missing LTP")
        self._log(f"Found {len(missing_oi)} rows with missing OI")
        self._log(f"Found {len(missing_greeks)} rows with missing Greeks")

        # Retry loop
        for attempt in range(1, max_retries + 1):
            self._log(f"Correction attempt {attempt}/{max_retries}")
            correction_stats["attempts"] = attempt

            # Fix missing LTP and quote data
            if len(missing_ltp) > 0:
                fixed_ltp = self._fix_ltp_and_quote(df, missing_ltp, exchange)
                correction_stats["ltp_fixed"] += fixed_ltp["ltp"]
                correction_stats["quote_fixed"] += fixed_ltp["quote"]
                correction_stats["oi_fixed"] += fixed_ltp["oi"]

            # Fix missing Greeks
            if len(missing_greeks) > 0:
                fixed_greeks = self._fix_greeks(df, missing_greeks, exchange)
                correction_stats["greeks_fixed"] += fixed_greeks

            # Re-check if we need more attempts
            remaining_ltp = df[df["ltp"].isna()].shape[0]
            remaining_greeks = df[df["delta"].isna()].shape[0]

            if remaining_ltp == 0 and remaining_greeks == 0:
                self._log("All missing data corrected")
                break

            if attempt < max_retries:
                self._log(f"Sleeping 5 seconds before retry...")
                time.sleep(5)

        return df, correction_stats

    def _fix_ltp_and_quote(self, df: pd.DataFrame, missing_rows: pd.DataFrame, exchange: str) -> Dict:
        """Fix missing LTP and quote data."""
        fixed = {"ltp": 0, "quote": 0, "oi": 0}

        for idx, row in missing_rows.iterrows():
            try:
                symbol = str(row["symbol"])
                token = str(row["token"])

                # Fetch quote data (includes LTP, OHLC, volume, OI, bid/ask)
                quote_data = self.broker.get_quote(exchange, symbol, token)

                if quote_data and quote_data.get("status"):
                    try:
                        quote = quote_data.get("data", {})

                        # Update LTP
                        if quote.get("ltp") is not None:
                            df.at[idx, "ltp"] = float(quote.get("ltp"))
                            fixed["ltp"] += 1

                        # Update OHLC
                        if quote.get("open") is not None:
                            df.at[idx, "open"] = float(quote.get("open"))
                        if quote.get("high") is not None:
                            df.at[idx, "high"] = float(quote.get("high"))
                        if quote.get("low") is not None:
                            df.at[idx, "low"] = float(quote.get("low"))
                        if quote.get("close") is not None:
                            df.at[idx, "close"] = float(quote.get("close"))

                        # Update volume and OI
                        if quote.get("volume") is not None:
                            df.at[idx, "volume"] = int(quote.get("volume"))
                            fixed["quote"] += 1
                        if quote.get("oi") is not None:
                            df.at[idx, "oi"] = int(quote.get("oi"))
                            fixed["oi"] += 1

                        # Update bid/ask
                        if quote.get("bidPrice") is not None:
                            df.at[idx, "bidPrice"] = float(quote.get("bidPrice"))
                            df.at[idx, "bidQty"] = int(quote.get("bidQty", 0))
                        if quote.get("offerPrice") is not None:
                            df.at[idx, "offerPrice"] = float(quote.get("offerPrice"))
                            df.at[idx, "offerQty"] = int(quote.get("offerQty", 0))

                        # Update change
                        if quote.get("change") is not None:
                            df.at[idx, "change"] = float(quote.get("change"))
                        if quote.get("pChange") is not None:
                            df.at[idx, "pChange"] = float(quote.get("pChange"))

                    except (KeyError, ValueError, TypeError) as e:
                        self._log(f"Error parsing quote for {symbol}: {e}", "WARNING")
                        continue

                # Small delay to avoid rate limiting
                time.sleep(0.1)

            except Exception as e:
                self._log(f"Error fetching quote for row {idx}: {e}", "WARNING")
                continue

        return fixed

    def _fix_greeks(self, df: pd.DataFrame, missing_rows: pd.DataFrame, exchange: str) -> int:
        """Fix missing Greeks data."""
        fixed = 0

        for idx, row in missing_rows.iterrows():
            try:
                symbol = str(row["symbol"])
                token = str(row["token"])
                strike = float(row["strike"])
                expiry = str(row.get("expiry", "")).replace("-", "").upper()
                option_type = str(row.get("option_type", row.get("optionType", "")))

                if not expiry or not option_type:
                    continue

                # Fetch Greeks
                greeks_data = self.broker.get_option_greeks(exchange, symbol, token, strike, expiry, option_type)

                if greeks_data and greeks_data.get("status"):
                    try:
                        greeks = greeks_data.get("data", {})

                        # Update Greeks
                        if greeks.get("delta") is not None:
                            df.at[idx, "delta"] = float(greeks.get("delta"))
                            fixed += 1
                        if greeks.get("gamma") is not None:
                            df.at[idx, "gamma"] = float(greeks.get("gamma"))
                        if greeks.get("theta") is not None:
                            df.at[idx, "theta"] = float(greeks.get("theta"))
                        if greeks.get("vega") is not None:
                            df.at[idx, "vega"] = float(greeks.get("vega"))
                        if greeks.get("rho") is not None:
                            df.at[idx, "rho"] = float(greeks.get("rho"))
                        if greeks.get("iv") is not None:
                            df.at[idx, "iv"] = float(greeks.get("iv"))
                            df.at[idx, "impliedVolatility"] = df.at[idx, "iv"]

                        # Update premium fields
                        if greeks.get("pTime") is not None:
                            df.at[idx, "pTime"] = greeks.get("pTime")
                        if greeks.get("pChange") is not None:
                            df.at[idx, "pChange"] = float(greeks.get("pChange"))
                        if greeks.get("pOI") is not None:
                            df.at[idx, "pOI"] = int(greeks.get("pOI"))
                        if greeks.get("pVolume") is not None:
                            df.at[idx, "pVolume"] = int(greeks.get("pVolume"))

                    except (KeyError, ValueError, TypeError) as e:
                        self._log(f"Error parsing Greeks for {symbol}: {e}", "WARNING")
                        continue

                # Small delay to avoid rate limiting
                time.sleep(0.1)

            except Exception as e:
                self._log(f"Error fetching Greeks for row {idx}: {e}", "WARNING")
                continue

        return fixed

    def validate_and_correct(
        self, csv_path: str, underlying: str = "NIFTY", exchange: str = "NFO", output_path: Optional[str] = None
    ) -> Dict:
        """
        Complete validation and correction pipeline.

        Args:
            csv_path: Input CSV path
            underlying: Underlying name
            exchange: Exchange code
            output_path: Output CSV path (auto-generated if None)

        Returns:
            dict with complete results
        """
        # Step 1: Validate
        validation_result = self.validate(csv_path, underlying)

        if validation_result["status"] == "COMPLETE":
            self._log("Data validation PASSED - no correction needed")
            return {
                "validation": validation_result,
                "correction": None,
                "output_file": csv_path,
                "final_status": "COMPLETE",
            }

        # Step 2: Correct
        self._log(f"Data validation FAILED - starting correction")
        self._log(f"Failed checks: {validation_result['failed_checks']}")

        corrected_df, correction_stats = self.correct_missing_data(csv_path, underlying, exchange)

        if corrected_df is None:
            return {
                "validation": validation_result,
                "correction": {"error": "Correction failed"},
                "output_file": None,
                "final_status": "INCOMPLETE",
            }

        # Step 3: Re-validate
        # Save to temp file for re-validation
        temp_path = csv_path.replace(".csv", "_corrected_temp.csv")
        corrected_df.to_csv(temp_path, index=False)

        final_validation = self.validate(temp_path, underlying)

        # Step 4: Save final file
        if output_path is None:
            base_name = Path(csv_path).stem
            output_path = str(ROOT_DIR / "storage" / "live" / f"{base_name}_v2.csv")

        corrected_df.to_csv(output_path, index=False)

        # Calculate final NaN rates
        final_nan_rates = {}
        for col in self.CRITICAL_COLUMNS:
            if col in corrected_df.columns:
                nan_count = corrected_df[col].isna().sum()
                final_nan_rates[col] = nan_count / len(corrected_df)

        result = {
            "validation": validation_result,
            "correction": correction_stats,
            "final_validation": final_validation,
            "output_file": output_path,
            "final_status": final_validation["status"],
            "final_nan_rates": final_nan_rates,
            "rows_after_fix": len(corrected_df),
        }

        # Generate summary output
        self._print_summary(result)

        return result

    def _print_summary(self, result: Dict):
        """Print validation summary in required format."""
        print("\n" + "=" * 80)
        print("OPTION CHAIN VALIDATION SUMMARY")
        print("=" * 80)
        print(f"VALIDATION: {result['final_status']}")
        print(f"Failed checks: {result['validation']['failed_checks']}")
        print(f"Rows after fix: {result['rows_after_fix']}")

        print("\nNaN rates fixed:")
        for col, rate in result["final_nan_rates"].items():
            print(f"  {col}={rate:.1%}")

        if result.get("correction"):
            print(f"\nCorrection stats:")
            print(f"  LTP fixed: {result['correction'].get('ltp_fixed', 0)}")
            print(f"  OI fixed: {result['correction'].get('oi_fixed', 0)}")
            print(f"  Greeks fixed: {result['correction'].get('greeks_fixed', 0)}")
            print(f"  Attempts: {result['correction'].get('attempts', 0)}")

        print(f"\nFile ready: {result['output_file']}")
        print("=" * 80 + "\n")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate and correct option chain data")
    parser.add_argument("csv_path", help="Path to option chain CSV file")
    parser.add_argument("--underlying", default="NIFTY", help="Underlying name")
    parser.add_argument("--exchange", default="NFO", help="Exchange code")
    parser.add_argument("--output", help="Output CSV path (auto-generated if not provided)")

    args = parser.parse_args()

    validator = OptionChainValidator()
    result = validator.validate_and_correct(args.csv_path, args.underlying, args.exchange, args.output)

    return 0 if result["final_status"] == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
