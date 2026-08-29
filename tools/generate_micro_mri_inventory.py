"""Fast Exhaustive Micro-MRI Inventory Scanner."""

from __future__ import annotations

import csv
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = ROOT / "SYSTEM3_MICRO_MRI_INVENTORY.csv"

VALID_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".json",
    ".yml",
    ".yaml",
    ".sh",
    ".ps1",
    ".csv",
    ".md",
    "Dockerfile",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".worktrees",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
}


def get_latest_commit_sha() -> str:
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        return (p.stdout or "").strip() or "head"
    except Exception:
        return "head"


def classify_domain(path_str: str) -> tuple[str, str, str, str]:
    """Return (Domain_Category, Component_Type, Is_Active, Associated_API_Route_Or_Job)."""
    p = path_str.lower().replace("\\", "/")

    if "chain" in p or "option" in p:
        if p.endswith(".tsx") or p.endswith(".ts"):
            return (
                "Option Chain",
                "Frontend Workspace UI",
                "Active",
                "/api/option-chain",
            )
        return (
            "Option Chain",
            "Core Backend Service",
            "Active",
            "/api/option-chain, /api/options-intel",
        )

    if "multibagger" in p:
        if p.endswith(".tsx") or p.endswith(".ts"):
            return (
                "Multibagger Intelligence",
                "Frontend Research Workspace",
                "Active",
                "/api/multibagger",
            )
        return (
            "Multibagger Intelligence",
            "Core Fundamental Engine",
            "Active",
            "/api/multibagger",
        )

    if "ml" in p or "model" in p or "tournament" in p or "feature" in p:
        return (
            "ML & Tournament",
            "Prediction Intelligence",
            "Active",
            "/api/ml/features, /api/ml/tournament",
        )

    if "paper" in p or "order" in p or "position" in p:
        return (
            "Paper Execution",
            "Simulated Order Engine",
            "Active",
            "/api/paper/positions, /api/paper/orders",
        )

    if "backtest" in p or "simulation" in p:
        return (
            "Backtesting Engine",
            "Institutional Simulation",
            "Active",
            "/api/backtest/results",
        )

    if "catalyst" in p or "news" in p:
        return (
            "Macro & News Intelligence",
            "Event Timeline Service",
            "Active",
            "/api/catalysts, /api/news",
        )

    if "dhan" in p or "broker" in p or "feed" in p:
        return (
            "Broker Gateway & Ingestion",
            "Dhan Connector / Rotator",
            "Active",
            "/api/broker/status, genesis-system3-dhan-token-rotate",
        )

    if "scheduler" in p or "runner" in p or "cron" in p:
        return (
            "Cloud Orchestration",
            "Job Scheduler / Runner",
            "Active",
            "genesis-system3-dhan-token-rotate-daily",
        )

    if "cloud_storage" in p or "firestore" in p or "storage" in p:
        return (
            "Cloud Storage & State SSOT",
            "Firestore & GCS Layer",
            "Active",
            "gs://system3-openalgo-safe-artifacts",
        )

    if "app.py" in p or "secure_app.py" in p or "route" in p or "router" in p:
        return (
            "API Gateway & Router",
            "FastAPI Unified Router",
            "Active",
            "/api/*, /ui",
        )

    if "dashboard/frontend" in p:
        return (
            "Frontend Dashboard",
            "React / Vite UI Component",
            "Active",
            "/ui",
        )

    if ".github" in p or "deploy" in p:
        return (
            "CI/CD & Cloud Run DevOps",
            "GitHub Actions / GCP WIF",
            "Active",
            "genesis-system3-web",
        )

    if "rule" in p or "policy" in p or "agent" in p or "docs" in p:
        return (
            "Governance & Contract Policy",
            "Agent Operating Laws",
            "Active",
            "docs/control_plane/*",
        )

    return (
        "General Core & Utilities",
        "Utility Script / Module",
        "Active",
        "N/A",
    )


def scan_workspace():
    print("=== FAST EXHAUSTIVE MICRO-MRI REPOSITORY SCAN ===")
    head_sha = get_latest_commit_sha()
    records = []

    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [
            d
            for d in dirs
            if d not in IGNORED_DIRS and not d.startswith(".worktrees")
        ]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in VALID_EXTENSIONS or file == "Dockerfile":
                full_path = Path(root) / file
                try:
                    rel_path = full_path.relative_to(ROOT).as_posix()
                except ValueError:
                    continue

                domain, comp_type, is_active, assoc_route = classify_domain(
                    rel_path
                )
                file_size = full_path.stat().st_size
                notes = f"Size: {file_size} bytes | Head SHA: {head_sha}"

                records.append({
                    "File_Path": rel_path,
                    "Domain_Category": domain,
                    "Component_Type": comp_type,
                    "Is_Active": is_active,
                    "Associated_API_Route_Or_Job": assoc_route,
                    "SHA_Provenance": head_sha,
                    "Notes_And_Diagnostics": notes,
                })

    records.sort(key=lambda r: (r["Domain_Category"], r["File_Path"]))

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "File_Path",
            "Domain_Category",
            "Component_Type",
            "Is_Active",
            "Associated_API_Route_Or_Job",
            "SHA_Provenance",
            "Notes_And_Diagnostics",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"Total Files Cataloged: {len(records)}")
    print(f"Successfully generated: {OUTPUT_CSV}")
    return records


if __name__ == "__main__":
    scan_workspace()
