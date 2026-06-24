"""
Output Schema Validators - Strict schema validation for all outputs
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SchemaValidator:
    """Validates output files against strict schemas."""

    # Required keys for each output type
    SCHEMAS = {
        "health.json": {
            "required": [
                "timestamp",
                "is_running",
                "is_connected",
                "total_cycles",
                "trades_executed",
                "current_positions",
                "total_pnl",
                "daily_pnl",
                "mode",
            ],
            "optional": [
                "last_data_fetch",
                "successful_fetches",
                "failed_fetches",
                "data_success_rate",
                "signal_success_rate",
                "signals_generated",
                "shutdown_time",
                "qc_passed",
            ],
        },
        "qc_report_live.json": {
            "required": ["status", "mode", "timestamp", "qc_passed"],
            "optional": [
                "reason",
                "cycle",
                "cycle_count",
                "total_contracts",
                "trade_signals",
                "no_trade_signals",
                "qc_failures",
                "last_data_fetch",
            ],
        },
        "top_trade_signal.json": {
            "required": ["action", "mode", "timestamp", "confidence"],
            "optional": [
                "underlying",
                "symbol",
                "strategy",
                "reason",
                "reasons",
                "tokens",
                "strikes",
                "entry_mid",
                "stop_loss",
                "target",
            ],
        },
        "chain_raw_live.csv": {
            "required_columns": ["status"],  # At minimum, status column must exist
            "optional_columns": [
                "underlying",
                "strike",
                "option_type",
                "ltp",
                "bid",
                "ask",
                "oi",
                "iv",
                "timestamp",
                "mode",
                "reason",
                "cycle",
            ],
        },
        "underlying_rank_live.csv": {
            "required_columns": ["underlying", "status", "timestamp"],
            "optional_columns": ["exchange", "rank", "score", "mode"],
        },
    }

    @staticmethod
    def validate_json(file_path: Path, schema_name: str) -> tuple[bool, List[str]]:
        """
        Validate JSON file against schema.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        if not file_path.exists():
            return False, [f"File not found: {file_path}"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]

        if schema_name not in SchemaValidator.SCHEMAS:
            return True, []  # Unknown schema, skip validation

        schema = SchemaValidator.SCHEMAS[schema_name]
        required = schema.get("required", [])

        # Check required keys
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")

        # Validate types for critical fields
        if "is_running" in data:
            if not isinstance(data["is_running"], bool):
                errors.append("is_running must be boolean")

        if "is_connected" in data:
            if not isinstance(data["is_connected"], bool):
                errors.append("is_connected must be boolean")

        if "trades_executed" in data:
            if not isinstance(data["trades_executed"], (int, float)):
                errors.append("trades_executed must be numeric")

        if "current_positions" in data:
            if not isinstance(data["current_positions"], (int, float)):
                errors.append("current_positions must be numeric")

        if "qc_passed" in data:
            if not isinstance(data["qc_passed"], bool):
                errors.append("qc_passed must be boolean")

        if "action" in data:
            if data["action"] not in ["TRADE", "NO_TRADE"]:
                errors.append(f"action must be TRADE or NO_TRADE, got: {data['action']}")

        if "mode" in data:
            valid_modes = ["SIMULATION", "LIVE", "MARKET_CLOSED", "NO_DATA"]
            if data["mode"] not in valid_modes:
                errors.append(f"mode must be one of {valid_modes}, got: {data['mode']}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_csv(file_path: Path, schema_name: str) -> tuple[bool, List[str]]:
        """
        Validate CSV file against schema.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        if not file_path.exists():
            return False, [f"File not found: {file_path}"]

        try:
            import pandas as pd

            df = pd.read_csv(file_path)
        except Exception as e:
            return False, [f"Error reading CSV: {e}"]

        if schema_name not in SchemaValidator.SCHEMAS:
            return True, []  # Unknown schema, skip validation

        schema = SchemaValidator.SCHEMAS[schema_name]
        required_cols = schema.get("required_columns", [])

        # Check required columns
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        # Check that file is not empty (must have at least header or one row)
        if len(df) == 0 and len(df.columns) == 0:
            errors.append("CSV file is completely empty")

        return len(errors) == 0, errors

    @staticmethod
    def validate_all_outputs(output_dir: Path, scenario: str = "") -> Dict[str, Any]:
        """
        Validate all output files in a directory.

        Returns:
            Dictionary with validation results
        """
        results = {"valid": True, "errors": [], "files_checked": []}

        # Check each expected file
        files_to_check = [
            ("health.json", "health.json"),
            ("qc_report_live.json", "qc_report_live.json"),
            ("top_trade_signal.json", "top_trade_signal.json"),
            ("chain_raw_live.csv", "chain_raw_live.csv"),
            ("underlying_rank_live.csv", "underlying_rank_live.csv"),
        ]

        for filename, schema_name in files_to_check:
            file_path = output_dir / filename
            results["files_checked"].append(filename)

            if filename.endswith(".json"):
                is_valid, errors = SchemaValidator.validate_json(file_path, schema_name)
            else:
                is_valid, errors = SchemaValidator.validate_csv(file_path, schema_name)

            if not is_valid:
                results["valid"] = False
                results["errors"].extend([f"{filename}: {e}" for e in errors])

        return results
