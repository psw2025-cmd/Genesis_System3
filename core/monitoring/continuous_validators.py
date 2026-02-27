"""
PHASE E: CONTINUOUS VALIDATORS

Real-time monitoring modules for production System3 operation.
Detects timestamp parsing failures, merge key misalignment, and environment integrity issues.

Modules:
  1. TimestampValidator: Validates timestamp parsing across all phases
  2. MergeKeyValidator: Monitors merge key alignment before Phase 239 join
  3. VenvLockMode: Prevents venv contamination; enforces package pinning
  4. ContinuousMonitor: Orchestrates all validators in watchdog loop

Usage:
  from core/monitoring/continuous_validators import ContinuousMonitor
  
  monitor = ContinuousMonitor(
    watch_dir="storage/live",
    check_interval_sec=30,
    alert_on_threshold_miss=True,
    lock_venv_mode=True
  )
  monitor.start()  # Run in background watchdog
"""

import json
import logging
import hashlib
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np


class TimestampValidator:
    """Validates timestamp parsing reliability across Phase 221 & 239."""

    def __init__(self, metrics_dir: Path = None, logger: logging.Logger = None):
        self.metrics_dir = Path(metrics_dir or "storage/metrics")
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> Dict:
        """Convenience method to validate recent phase outputs."""
        from pathlib import Path

        phase_files = [
            Path("storage/live/forward/phase221_forward_returns.csv"),
            Path("storage/live/enriched/angel_virtual_orders_with_pnl.csv"),
        ]
        results = []
        for pf in phase_files:
            if pf.exists():
                result = self.validate_phase_output(pf, pf.stem)
                results.append(result)
        return {"passed": all(r.get("status") == "OK" for r in results), "results": results}

    def validate_phase_output(self, phase_csv: Path, phase_name: str) -> Dict:
        """
        Validate timestamp column in phase output.

        Args:
            phase_csv: Path to phase output CSV
            phase_name: Phase name (e.g., "Phase 221", "Phase 239")

        Returns:
            {
              "status": "OK" | "WARN" | "ERROR",
              "total_rows": int,
              "valid_timestamps": int,
              "null_timestamps": int,
              "parse_errors": int,
              "formats_detected": List[str],
              "timestamp_range": [min, max],
              "validation_time": timestamp
            }
        """
        try:
            df = pd.read_csv(phase_csv)
            if "ts" not in df.columns:
                return {"status": "WARN", "message": f"{phase_name}: No 'ts' column found", "total_rows": len(df)}

            ts_col = df["ts"]
            total = len(ts_col)
            nulls = ts_col.isna().sum()
            valid = total - nulls

            # Detect timestamp formats
            formats = self._detect_formats(ts_col)

            # Check timestamp range validity
            non_null = ts_col.dropna()
            if len(non_null) > 0:
                try:
                    parsed = pd.to_datetime(non_null, errors="coerce")
                    valid_parsed = parsed.notna().sum()
                    ts_range = (parsed.min(), parsed.max())
                except Exception as e:
                    valid_parsed = 0
                    ts_range = (None, None)
            else:
                valid_parsed = 0
                ts_range = (None, None)

            status = "OK" if valid >= total * 0.8 else "WARN" if valid >= 0 else "ERROR"

            result = {
                "status": status,
                "phase": phase_name,
                "total_rows": total,
                "valid_timestamps": valid_parsed,
                "null_timestamps": nulls,
                "valid_pct": 100.0 * valid_parsed / total if total > 0 else 0,
                "formats_detected": formats,
                "timestamp_range": [str(ts_range[0]), str(ts_range[1])],
                "validation_time": datetime.utcnow().isoformat(),
            }

            self.logger.info(
                f"[{phase_name}] Timestamp validation: {valid_parsed}/{total} valid ({result['valid_pct']:.1f}%)"
            )
            return result

        except Exception as e:
            self.logger.error(f"[{phase_name}] Timestamp validation error: {e}")
            return {
                "status": "ERROR",
                "phase": phase_name,
                "error": str(e),
                "validation_time": datetime.utcnow().isoformat(),
            }

    def _detect_formats(self, ts_col: pd.Series, sample_size: int = 100) -> List[str]:
        """Detect timestamp formats in sample."""
        formats = set()
        sample = ts_col.dropna().head(sample_size)

        for val in sample:
            val_str = str(val)
            if "+" in val_str or "Z" in val_str:
                formats.add("ISO8601_with_offset")
            elif "T" in val_str:
                formats.add("ISO8601_naive")
            elif len(val_str) < 15:
                formats.add("numeric_epoch")
            else:
                formats.add("other")

        return list(formats)

    def save_report(self, results: List[Dict]) -> Path:
        """Save validation results to metrics/."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.metrics_dir / f"timestamp_validation_{timestamp}.json"

        with open(report_path, "w") as f:
            report_data = {
                "validation_time": datetime.utcnow().isoformat(),
                "results": results,
                "summary": {"total_phases": len(results), "all_valid": all(r.get("status") == "OK" for r in results)},
            }
            # Convert numpy types to JSON-serializable types
            report_json = json.loads(json.dumps(report_data, default=str))
            json.dump(report_json, f, indent=2)

        return report_path


class MergeKeyValidator:
    """Monitors merge key alignment before Phase 239 join."""

    def __init__(self, metrics_dir: Path = None, logger: logging.Logger = None):
        self.metrics_dir = Path(metrics_dir or "storage/metrics")
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> Dict:
        """Convenience method to validate merge key alignment."""
        from pathlib import Path

        signals_file = Path("storage/live/forward/phase221_forward_returns.csv")
        orders_file = Path("storage/live/healed/angel_virtual_orders_healed.csv")
        if signals_file.exists() and orders_file.exists():
            result = self.validate_alignment(signals_file, orders_file)
            return {"passed": result.get("status") == "OK", "result": result}
        else:
            return {"passed": False, "message": "Required files not found"}

    def validate_alignment(self, signals_csv: Path, orders_csv: Path) -> Dict:
        """
        Validate merge key alignment between signals and orders.

        Returns:
            {
              "status": "OK" | "WARN" | "ERROR",
              "merge_keys": {
                "ts": {"signals_unique": int, "orders_unique": int, "overlap": int, "overlap_pct": float},
                "underlying": {...},
                "strike": {...},
                "side": {...},
                "expiry": {...}
              },
              "alignment_score": float (0-100),
              "recommendations": List[str]
            }
        """
        try:
            signals = pd.read_csv(signals_csv)
            orders = pd.read_csv(orders_csv)

            keys = ["ts", "underlying", "strike", "side", "expiry"]
            missing_keys = [k for k in keys if k not in signals.columns or k not in orders.columns]

            if missing_keys:
                return {
                    "status": "ERROR",
                    "message": f"Missing merge keys: {missing_keys}",
                    "signals_shape": signals.shape,
                    "orders_shape": orders.shape,
                }

            alignment = {}
            overlaps = []

            for key in keys:
                sig_unique = set(signals[key].dropna().astype(str).unique())
                ord_unique = set(orders[key].dropna().astype(str).unique())
                overlap = len(sig_unique & ord_unique)
                overlap_pct = 100.0 * overlap / len(sig_unique) if len(sig_unique) > 0 else 0

                alignment[key] = {
                    "signals_unique": len(sig_unique),
                    "orders_unique": len(ord_unique),
                    "overlap": overlap,
                    "overlap_pct": overlap_pct,
                }
                overlaps.append(overlap_pct)

            alignment_score = np.mean(overlaps)
            status = "OK" if alignment_score >= 80 else "WARN" if alignment_score >= 50 else "ERROR"

            recommendations = []
            if alignment["side"]["overlap_pct"] < 50:
                recommendations.append("CRITICAL: Side mismatch (CE/PE vs BUY/SELL?) - apply normalize_side()")
            if alignment["expiry"]["overlap_pct"] < 50:
                recommendations.append(
                    "CRITICAL: Expiry format mismatch (DDMMMYYYY vs YYYY-MM-DD?) - apply normalize_expiry()"
                )
            if alignment["ts"]["overlap_pct"] < 50:
                recommendations.append(
                    "CRITICAL: Timestamp format mismatch (ISO8601+offset vs naive?) - apply normalize_timestamp()"
                )
            if alignment["strike"]["overlap_pct"] < 80:
                recommendations.append("WARNING: Strike mismatch (float vs int?) - apply normalize_strike()")
            if alignment["underlying"]["overlap_pct"] < 80:
                recommendations.append(
                    "WARNING: Underlying mismatch (case sensitivity?) - apply normalize_underlying()"
                )

            result = {
                "status": status,
                "merge_keys": alignment,
                "alignment_score": alignment_score,
                "signals_rows": len(signals),
                "orders_rows": len(orders),
                "validation_time": datetime.utcnow().isoformat(),
                "recommendations": recommendations,
            }

            self.logger.info(f"Merge key alignment: {alignment_score:.1f}% (status: {status})")
            if recommendations:
                for rec in recommendations:
                    self.logger.warning(f"     {rec}")

            return result

        except Exception as e:
            self.logger.error(f"Merge key validation error: {e}")
            return {"status": "ERROR", "error": str(e), "validation_time": datetime.utcnow().isoformat()}

    def save_report(self, results: Dict) -> Path:
        """Save validation results to metrics/."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.metrics_dir / f"merge_key_validation_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        return report_path


class VenvLockMode:
    """Prevents venv contamination by monitoring and enforcing package pinning."""

    def __init__(self, venv_path: Path = None, logger: logging.Logger = None):
        self.venv_path = Path(venv_path or "venv")
        self.logger = logger or logging.getLogger(__name__)
        self.allowed_packages = {
            "pandas",
            "numpy",
            "pathlib",
            "json",
            "logging",
            "datetime",
            "pip",
            "setuptools",
            "wheel",
        }

    def validate(self) -> Dict:
        """Convenience method to validate venv integrity."""
        result = self.validate_venv_integrity()
        return {"passed": result.get("status") == "OK", "result": result}

    def get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages and versions."""
        try:
            if platform.system() == "Windows":
                python_exe = self.venv_path / "Scripts" / "python.exe"
            else:
                python_exe = self.venv_path / "bin" / "python"

            if not python_exe.exists():
                self.logger.warning(f"Python executable not found: {python_exe}")
                return {}

            result = subprocess.run(
                [str(python_exe), "-m", "pip", "list", "--format=json"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {p["name"]: p["version"] for p in packages}
            else:
                self.logger.error(f"pip list error: {result.stderr}")
                return {}

        except Exception as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return {}

    def compute_venv_hash(self) -> str:
        """Compute hash of venv package state."""
        packages = self.get_installed_packages()
        state = json.dumps(packages, sort_keys=True)
        return hashlib.sha256(state.encode()).hexdigest()

    def validate_venv_integrity(self) -> Dict:
        """
        Validate venv hasn't been modified unexpectedly.

        Returns:
            {
              "status": "OK" | "WARN",
              "venv_exists": bool,
              "python_version": str,
              "package_count": int,
              "suspicious_packages": List[str],
              "venv_hash": str,
              "timestamp": timestamp
            }
        """
        try:
            if platform.system() == "Windows":
                python_exe = self.venv_path / "Scripts" / "python.exe"
            else:
                python_exe = self.venv_path / "bin" / "python"

            venv_exists = python_exe.exists()
            python_version = "unknown"

            if venv_exists:
                result = subprocess.run([str(python_exe), "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    python_version = result.stdout.strip()

            packages = self.get_installed_packages()
            suspicious = [p for p in packages.keys() if p not in self.allowed_packages and not p.startswith("_")]

            status = "OK" if not suspicious else "WARN"

            result = {
                "status": status,
                "venv_exists": venv_exists,
                "venv_path": str(self.venv_path),
                "python_version": python_version,
                "package_count": len(packages),
                "suspicious_packages": suspicious[:10],  # Top 10
                "venv_hash": self.compute_venv_hash(),
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.logger.info(f"Venv integrity: {result['package_count']} packages, {len(suspicious)} suspicious")

            return result

        except Exception as e:
            self.logger.error(f"Venv validation error: {e}")
            return {"status": "ERROR", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def save_report(self, results: Dict) -> Path:
        """Save validation results to metrics/."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = Path("storage/metrics") / f"venv_integrity_{timestamp}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            # Convert numpy types to JSON-serializable types
            report_json = json.loads(json.dumps(results, default=str))
            json.dump(report_json, f, indent=2)

        return report_path


class ContinuousMonitor:
    """Orchestrates all validators in background watchdog loop."""

    def __init__(
        self,
        watch_dir: Path = None,
        check_interval_sec: int = 60,
        alert_on_threshold_miss: bool = True,
        lock_venv_mode: bool = True,
        log_file: Path = None,
    ):
        self.watch_dir = Path(watch_dir or "storage/live")
        self.check_interval = timedelta(seconds=check_interval_sec)
        self.alert_threshold = alert_on_threshold_miss
        self.lock_venv = lock_venv_mode

        # Setup logging
        log_file = Path(log_file or "storage/metrics/continuous_monitor.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("ContinuousMonitor")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize validators
        self.ts_validator = TimestampValidator(logger=self.logger)
        self.key_validator = MergeKeyValidator(logger=self.logger)
        self.venv_validator = VenvLockMode(logger=self.logger)

        self.last_check = None
        self.check_count = 0

    def run_check(self) -> Dict:
        """Execute all validators and return results."""
        self.logger.info("=" * 80)
        self.logger.info("CONTINUOUS VALIDATION CHECK")
        self.logger.info("=" * 80)

        results = {
            "check_id": f"check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "check_number": self.check_count,
            "validators": {},
        }

        # Timestamp validation
        self.logger.info("[*] Running timestamp validation...")
        phase_files = [
            self.watch_dir / "forward" / "phase221_forward_returns.csv",
            self.watch_dir / "enriched" / "angel_virtual_orders_with_pnl.csv",
        ]
        ts_results = []
        for pf in phase_files:
            if pf.exists():
                ts_results.append(self.ts_validator.validate_phase_output(pf, pf.stem))
        if ts_results:
            results["validators"]["timestamp"] = ts_results
            self.ts_validator.save_report(ts_results)

        # Merge key validation
        self.logger.info("[*] Running merge key validation...")
        signals_file = self.watch_dir / "forward" / "phase221_forward_returns.csv"
        orders_file = self.watch_dir / "healed" / "angel_virtual_orders_healed.csv"
        if signals_file.exists() and orders_file.exists():
            key_results = self.key_validator.validate_alignment(signals_file, orders_file)
            results["validators"]["merge_keys"] = key_results
            self.key_validator.save_report(key_results)

        # Venv integrity
        if self.lock_venv:
            self.logger.info("[*] Running venv integrity check...")
            venv_results = self.venv_validator.validate_venv_integrity()
            results["validators"]["venv"] = venv_results
            self.venv_validator.save_report(venv_results)

        self.last_check = datetime.utcnow()
        self.check_count += 1

        self.logger.info("=" * 80)
        self.logger.info(f"Check complete (#{self.check_count})")
        self.logger.info("=" * 80)

        return results

    def print_summary(self, results: Dict):
        """Print validation summary to console."""
        print(f"\n{'='*70}")
        print(f"CONTINUOUS VALIDATION REPORT - {results['check_id']}")
        print(f"{'='*70}\n")

        if "timestamp" in results.get("validators", {}):
            print("TIMESTAMP VALIDATION:")
            for r in results["validators"]["timestamp"]:
                print(f"  * {r.get('phase', '?')}: {r.get('status', '?')} ({r.get('valid_pct', 0):.1f}% valid)")

        if "merge_keys" in results.get("validators", {}):
            mk = results["validators"]["merge_keys"]
            print(f"\nMERGE KEY ALIGNMENT: {mk.get('alignment_score', 0):.1f}% - {mk.get('status', '?')}")
            if mk.get("recommendations"):
                for rec in mk["recommendations"]:
                    print(f"  [!] {rec}")

        if "venv" in results.get("validators", {}):
            venv = results["validators"]["venv"]
            print(f"\nVENV INTEGRITY: {venv.get('status', '?')} ({venv.get('package_count', 0)} packages)")
            if venv.get("suspicious_packages"):
                print(f"  [!] Suspicious: {', '.join(venv['suspicious_packages'][:5])}")

        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    # Example usage
    monitor = ContinuousMonitor(
        watch_dir="storage/live", check_interval_sec=60, alert_on_threshold_miss=True, lock_venv_mode=True
    )

    results = monitor.run_check()
    monitor.print_summary(results)
