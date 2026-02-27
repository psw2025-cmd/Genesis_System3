"""
System3 Phase 231 - Threshold Loader & Registry

This phase provides a single, robust place to load BUY/SELL thresholds for each underlying.
It reads from storage/meta/system3_threshold_candidates.json (if available) or falls back
to safe default thresholds. It returns OK when thresholds are loaded successfully, or WARN
when falling back to defaults. It is 100% DRY-RUN safe and does NOT trigger live trading.

Location: core/engine/threshold_loader.py
Function: run_phase231() - Returns PhaseResult dict with status OK/WARN
Helper: load_thresholds() - Returns thresholds dict for use by other modules
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
META_DIR = PROJECT_ROOT / "storage" / "meta"
META_DIR.mkdir(parents=True, exist_ok=True)
THRESHOLD_CANDIDATES_PATH = META_DIR / "system3_threshold_candidates.json"
THRESHOLD_LIVE_PATH = META_DIR / "system3_live_thresholds.json"
LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_threshold_loader.log"
REPORT_PATH = LOG_DIR / "system3_threshold_loader_phase231_report.md"

# Default thresholds (fallback)
DEFAULT_THRESHOLDS = {"buy": 0.12, "sell": -0.10}

# All supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _log_message(message: str, level: str = "INFO") -> None:
    """Log to file only (no logger dependency to avoid import errors)."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass  # Don't fail if logging fails


def load_thresholds(prefer_candidates: bool = True) -> Dict[str, Dict[str, float]]:
    """
    Load thresholds for all underlyings.

    Args:
        prefer_candidates: If True, try to load from threshold_candidates.json first

    Returns:
        dict: {
            "default": {"buy": float, "sell": float},
            "NIFTY": {"buy": float, "sell": float},
            "BANKNIFTY": {...},
            ...
        }
    """
    result = {}

    # Start with defaults for all
    for underlying in SUPPORTED_UNDERLYINGS:
        result[underlying] = DEFAULT_THRESHOLDS.copy()
    result["default"] = DEFAULT_THRESHOLDS.copy()

    if not prefer_candidates:
        _log_message("Using default thresholds (prefer_candidates=False)")
        return result

    # Priority 1: Try to load from live_thresholds.json (new format)
    if THRESHOLD_LIVE_PATH.exists():
        try:
            with THRESHOLD_LIVE_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Check for direct format
            if "global" in data or "default" in data or any(und in data for und in SUPPORTED_UNDERLYINGS):
                # Direct format
                if "global" in data:
                    result["default"] = {
                        "buy": float(data["global"].get("buy", DEFAULT_THRESHOLDS["buy"])),
                        "sell": float(data["global"].get("sell", DEFAULT_THRESHOLDS["sell"])),
                    }
                elif "default" in data:
                    result["default"] = {
                        "buy": float(data["default"].get("buy", DEFAULT_THRESHOLDS["buy"])),
                        "sell": float(data["default"].get("sell", DEFAULT_THRESHOLDS["sell"])),
                    }

                # Load per-underlying thresholds
                per_underlying = data.get("per_underlying", {})
                if not per_underlying:
                    # Try direct keys
                    for underlying in SUPPORTED_UNDERLYINGS:
                        if underlying in data:
                            per_underlying[underlying] = data[underlying]

                for underlying in SUPPORTED_UNDERLYINGS:
                    if underlying in per_underlying:
                        result[underlying] = {
                            "buy": float(per_underlying[underlying].get("buy", result["default"]["buy"])),
                            "sell": float(per_underlying[underlying].get("sell", result["default"]["sell"])),
                        }
                    else:
                        # Use default if not specified
                        result[underlying] = result["default"].copy()

                _log_message("Loaded thresholds from system3_live_thresholds.json")
                return result
        except Exception as e:
            _log_message(f"Failed to load live thresholds: {e}. Trying candidates file.", "WARN")

    # Priority 2: Try to load from candidates file
    if not THRESHOLD_CANDIDATES_PATH.exists():
        _log_message(f"Threshold files not found. Using defaults.", "WARN")
        return result

    try:
        with THRESHOLD_CANDIDATES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Support two formats:
        # Format 1: Direct format with "default" and per-underlying keys
        if "default" in data or any(und in data for und in SUPPORTED_UNDERLYINGS):
            # Direct format
            for underlying in SUPPORTED_UNDERLYINGS:
                if underlying in data:
                    result[underlying] = {
                        "buy": float(data[underlying].get("buy", DEFAULT_THRESHOLDS["buy"])),
                        "sell": float(data[underlying].get("sell", DEFAULT_THRESHOLDS["sell"])),
                    }
            if "default" in data:
                result["default"] = {
                    "buy": float(data["default"].get("buy", DEFAULT_THRESHOLDS["buy"])),
                    "sell": float(data["default"].get("sell", DEFAULT_THRESHOLDS["sell"])),
                }
            _log_message("Loaded thresholds from direct format JSON")
            return result

        # Format 2: Candidates array format (from Phase 223)
        candidates = data.get("candidates", [])
        if not candidates:
            _log_message("No candidates found in JSON. Using defaults.", "WARN")
            return result

        # Find candidate with most signals (or first one if all zero)
        best_candidate = None
        max_signals = -1
        for cand in candidates:
            total_signals = cand.get("buy_count", 0) + cand.get("sell_count", 0)
            if total_signals > max_signals:
                max_signals = total_signals
                best_candidate = cand

        if best_candidate is None:
            best_candidate = candidates[0]

        # Extract thresholds
        buy_thr = float(best_candidate.get("buy_threshold", DEFAULT_THRESHOLDS["buy"]))
        sell_thr = float(best_candidate.get("sell_threshold", DEFAULT_THRESHOLDS["sell"]))

        # Validate thresholds
        if buy_thr <= 0 or sell_thr >= 0:
            _log_message(f"Invalid thresholds (buy={buy_thr}, sell={sell_thr}). Using defaults.", "WARN")
            return result

        # Apply to all underlyings
        for underlying in SUPPORTED_UNDERLYINGS:
            result[underlying] = {"buy": buy_thr, "sell": sell_thr}
        result["default"] = {"buy": buy_thr, "sell": sell_thr}

        _log_message(f"Loaded thresholds from candidates: buy={buy_thr:.3f}, sell={sell_thr:.3f}")

    except json.JSONDecodeError as e:
        _log_message(f"Invalid JSON in threshold candidates file: {e}. Using defaults.", "WARN")
    except (ValueError, TypeError) as e:
        _log_message(f"Invalid threshold values in JSON: {e}. Using defaults.", "WARN")
    except Exception as e:
        _log_message(f"Error loading threshold candidates: {e}. Using defaults.", "WARN")

    return result


def run_phase231() -> Dict[str, Any]:
    """
    Run Phase 231: Threshold Loader & Validator.

    This function implements Phase 231 as a robust loader + validator for BUY/SELL thresholds.
    It reads from storage/meta/system3_threshold_candidates.json (if available) or falls back
    to safe default thresholds. It returns OK when thresholds are loaded successfully, or WARN
    when falling back to defaults. It NEVER returns ERROR - all errors are handled gracefully.

    Returns:
        dict: PhaseResult with keys:
            - phase: 231
            - status: "OK" or "WARN" (never "ERROR")
            - details: Human-readable summary
            - outputs: Dict with thresholds and metadata
            - errors: List of error messages (empty if OK)
    """
    errors = []
    warnings = []
    source = "fallback"

    # Initialize result with defaults
    thresholds = {}
    for underlying in SUPPORTED_UNDERLYINGS:
        thresholds[underlying] = DEFAULT_THRESHOLDS.copy()
    thresholds["default"] = DEFAULT_THRESHOLDS.copy()

    # Try to load from JSON file
    if not THRESHOLD_CANDIDATES_PATH.exists():
        warnings.append(f"File not found: {THRESHOLD_CANDIDATES_PATH}")
        _log_message(f"Threshold candidates file not found. Using fallback defaults.", "WARN")
    else:
        try:
            with THRESHOLD_CANDIDATES_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Try direct format first
            if "default" in data or any(und in data for und in SUPPORTED_UNDERLYINGS):
                source = "direct_format"
                loaded_any = False

                if "default" in data:
                    try:
                        thresholds["default"] = {
                            "buy": float(data["default"].get("buy", DEFAULT_THRESHOLDS["buy"])),
                            "sell": float(data["default"].get("sell", DEFAULT_THRESHOLDS["sell"])),
                        }
                        loaded_any = True
                    except (ValueError, TypeError) as e:
                        warnings.append(f"Invalid default thresholds: {e}")

                for underlying in SUPPORTED_UNDERLYINGS:
                    if underlying in data:
                        try:
                            thresholds[underlying] = {
                                "buy": float(data[underlying].get("buy", thresholds["default"]["buy"])),
                                "sell": float(data[underlying].get("sell", thresholds["default"]["sell"])),
                            }
                            loaded_any = True
                        except (ValueError, TypeError) as e:
                            warnings.append(f"Invalid thresholds for {underlying}: {e}")

                if not loaded_any:
                    warnings.append("Direct format found but no valid thresholds extracted")
                    source = "fallback"

            # Try candidates array format
            elif "candidates" in data:
                source = "candidates_array"
                candidates = data.get("candidates", [])

                if not candidates:
                    warnings.append("Candidates array is empty")
                    source = "fallback"
                else:
                    # Find best candidate
                    best_candidate = None
                    max_signals = -1
                    for cand in candidates:
                        total_signals = cand.get("buy_count", 0) + cand.get("sell_count", 0)
                        if total_signals > max_signals:
                            max_signals = total_signals
                            best_candidate = cand

                    if best_candidate is None:
                        best_candidate = candidates[0]

                    try:
                        buy_thr = float(best_candidate.get("buy_threshold", DEFAULT_THRESHOLDS["buy"]))
                        sell_thr = float(best_candidate.get("sell_threshold", DEFAULT_THRESHOLDS["sell"]))

                        # Validate
                        if buy_thr <= 0 or sell_thr >= 0:
                            warnings.append(f"Invalid thresholds: buy={buy_thr}, sell={sell_thr}")
                            source = "fallback"
                        else:
                            # Apply to all underlyings
                            for underlying in SUPPORTED_UNDERLYINGS:
                                thresholds[underlying] = {"buy": buy_thr, "sell": sell_thr}
                            thresholds["default"] = {"buy": buy_thr, "sell": sell_thr}
                    except (ValueError, TypeError) as e:
                        warnings.append(f"Invalid candidate thresholds: {e}")
                        source = "fallback"
            else:
                warnings.append("JSON file exists but has unsupported format")
                source = "fallback"

        except json.JSONDecodeError as e:
            warnings.append(f"Invalid JSON: {e}")
            _log_message(f"JSON decode error: {e}. Using fallback defaults.", "WARN")
            source = "fallback"
        except Exception as e:
            warnings.append(f"Unexpected error: {e}")
            _log_message(f"Error loading thresholds: {e}. Using fallback defaults.", "WARN")
            source = "fallback"

    # If fallback was used, write fallback JSON
    if source == "fallback" and not THRESHOLD_CANDIDATES_PATH.exists():
        try:
            fallback_data = {
                "metadata": {"generated_at": datetime.now().isoformat(), "source": "phase_231_fallback"},
                "global_thresholds": {"buy": DEFAULT_THRESHOLDS["buy"], "sell": DEFAULT_THRESHOLDS["sell"]},
                "per_underlying": {},
            }
            for underlying in SUPPORTED_UNDERLYINGS:
                fallback_data["per_underlying"][underlying] = DEFAULT_THRESHOLDS.copy()

            with THRESHOLD_CANDIDATES_PATH.open("w", encoding="utf-8") as f:
                json.dump(fallback_data, f, indent=2)
            _log_message(f"Created fallback threshold file: {THRESHOLD_CANDIDATES_PATH}")
        except Exception as e:
            warnings.append(f"Failed to write fallback JSON: {e}")

    # Generate report
    try:
        report_lines = [
            "# System3 Phase 231 - Threshold Loader Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Source**: {source}\n",
            "\n## Loaded Thresholds\n",
            "| Underlying | Buy Threshold | Sell Threshold |\n",
            "|------------|---------------|----------------|\n",
        ]

        report_lines.append(f"| default | {thresholds['default']['buy']:.3f} | {thresholds['default']['sell']:.3f} |\n")
        for underlying in SUPPORTED_UNDERLYINGS:
            report_lines.append(
                f"| {underlying} | {thresholds[underlying]['buy']:.3f} | {thresholds[underlying]['sell']:.3f} |\n"
            )

        if warnings:
            report_lines.append("\n## Warnings\n")
            for warn in warnings:
                report_lines.append(f"- ⚠️ {warn}\n")

        if errors:
            report_lines.append("\n## Errors\n")
            for err in errors:
                report_lines.append(f"- ❌ {err}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
    except Exception as e:
        warnings.append(f"Failed to write report: {e}")

    # Determine status
    status = "OK" if source != "fallback" else "WARN"
    details = (
        f"Loaded thresholds from {source}"
        if source != "fallback"
        else "Using fallback thresholds (file missing or invalid)"
    )

    if warnings:
        details += f" ({len(warnings)} warning(s))"

    return {
        "phase": 231,
        "status": status,
        "details": details,
        "outputs": {
            "thresholds": thresholds,
            "source": source,
            "file_path": str(THRESHOLD_CANDIDATES_PATH),
            "file_exists": THRESHOLD_CANDIDATES_PATH.exists(),
            "report_file": str(REPORT_PATH),
        },
        "errors": errors,
        "warnings": warnings,
    }


if __name__ == "__main__":
    # Test Phase 231
    result = run_phase231()
    print(f"Phase {result['phase']}: {result['status']}")
    print(f"Details: {result['details']}")
    print("\nLoaded thresholds:")
    thresholds = result["outputs"]["thresholds"]
    for key in ["default", "NIFTY", "BANKNIFTY"]:
        if key in thresholds:
            print(f"  {key}: buy={thresholds[key]['buy']:.3f}, sell={thresholds[key]['sell']:.3f}")
