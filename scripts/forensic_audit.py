"""
Forensic Audit Utilities - Environment snapshots, config snapshots, secrets redaction, file hashes
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).parent.parent


def get_env_snapshot() -> Dict[str, Any]:
    """Capture environment snapshot."""
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": sys.platform,
        "os_name": os.name,
        "cwd": str(Path.cwd()),
        "root_dir": str(ROOT_DIR),
    }

    # Get installed packages
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            snapshot["installed_packages"] = result.stdout.strip().split("\n")
        else:
            snapshot["installed_packages"] = []
    except Exception as e:
        snapshot["installed_packages"] = [f"Error: {e}"]

    # Get git commit hash if available
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, cwd=ROOT_DIR)
        if result.returncode == 0:
            snapshot["git_commit_hash"] = result.stdout.strip()
        else:
            snapshot["git_commit_hash"] = None
    except Exception:
        snapshot["git_commit_hash"] = None

    # Environment variables (redacted)
    env_vars = {}
    sensitive_patterns = ["PASSWORD", "SECRET", "KEY", "TOKEN", "API", "AUTH"]
    for key, value in os.environ.items():
        if any(pattern in key.upper() for pattern in sensitive_patterns):
            env_vars[key] = "[REDACTED]"
        else:
            env_vars[key] = value
    snapshot["environment_variables"] = env_vars

    return snapshot


def get_config_snapshot(args_dict: Dict[str, Any], config_dict: Dict[str, Any] = None) -> Dict[str, Any]:
    """Capture configuration snapshot."""
    snapshot = {"timestamp": datetime.now().isoformat(), "runtime_args": args_dict, "config_values": config_dict or {}}
    return snapshot


def scan_for_secrets(file_path: Path) -> List[Dict[str, Any]]:
    """Scan file for potential secrets (API keys, tokens, etc.)."""
    findings = []

    if not file_path.exists():
        return findings

    # Patterns to detect secrets
    patterns = {
        "api_key": r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
        "token": r'(?i)(token|access_token|bearer)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
        "password": r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']{8,})["\']?',
        "secret": r'(?i)(secret|secret_key)\s*[:=]\s*["\']?([a-zA-Z0-9]{16,})["\']?',
    }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for pattern_name, pattern in patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    findings.append(
                        {
                            "pattern": pattern_name,
                            "line": content[: match.start()].count("\n") + 1,
                            "match_preview": (
                                match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0)
                            ),
                        }
                    )
    except Exception as e:
        findings.append({"error": f"Failed to scan file: {e}"})

    return findings


def generate_file_hash(file_path: Path) -> Optional[str]:
    """Generate SHA256 hash of file."""
    if not file_path.exists():
        return None

    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None


def create_secrets_redaction_report(output_dir: Path) -> Dict[str, Any]:
    """Create secrets redaction report for all output files."""
    report = {"timestamp": datetime.now().isoformat(), "files_scanned": [], "findings": [], "status": "PASS"}

    files_to_scan = [
        "health.json",
        "qc_report_live.json",
        "top_trade_signal.json",
        "chain_raw_live.csv",
        "underlying_rank_live.csv",
    ]

    for filename in files_to_scan:
        file_path = output_dir / filename
        if file_path.exists():
            report["files_scanned"].append(filename)
            findings = scan_for_secrets(file_path)
            if findings:
                report["findings"].extend([{**f, "file": filename} for f in findings])
                report["status"] = "WARN"

    if not report["findings"]:
        report["status"] = "PASS"

    return report


def create_file_hashes(output_dir: Path) -> Dict[str, Any]:
    """Create file hashes for all artifacts."""
    hashes = {"timestamp": datetime.now().isoformat(), "files": {}}

    files_to_hash = [
        "health.json",
        "qc_report_live.json",
        "top_trade_signal.json",
        "chain_raw_live.csv",
        "underlying_rank_live.csv",
        "validation_results.json",
        "perf_metrics.json",
        "exceptions.json",
        "run_metadata.json",
    ]

    for filename in files_to_hash:
        file_path = output_dir / filename
        if file_path.exists():
            file_hash = generate_file_hash(file_path)
            if file_hash:
                hashes["files"][filename] = {"sha256": file_hash, "size_bytes": file_path.stat().st_size}

    return hashes


if __name__ == "__main__":
    # Test
    output_dir = ROOT_DIR / "outputs"
    print(json.dumps(get_env_snapshot(), indent=2))
    print(json.dumps(create_secrets_redaction_report(output_dir), indent=2))
    print(json.dumps(create_file_hashes(output_dir), indent=2))
