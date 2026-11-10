"""
BLK-007 FIX: Automated Blocker Finder Pipeline
Discovers, reports, and tracks open blockers automatically.

Issue: Same blockers were rediscovered manually every few weeks,
creating confusion about current status and priorities.

Fix:
1. Scan repo for known blocker patterns (comments, TODOs, errors)
2. Query runtime API for operational issues (alerts, failures)
3. Compare against master blocker register
4. Auto-generate daily report with delta/new findings
5. Integrate with CI/CD to run on each deploy
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import pytz
import re

IST = pytz.timezone("Asia/Kolkata")


class SystemBlockerFinder:
    """Scans repo and runtime for known/unknown blockers."""
    
    # Known blocker patterns in code/docs
    BLOCKER_PATTERNS = [
        (r"BLOCKER|BLK-\d+", "explicit_blocker_reference"),
        (r"TODO.*CRITICAL", "critical_todo"),
        (r"FIXME.*urgent", "urgent_fixme"),
        (r"XXX.*bug|BUG.*XXX", "critical_bug_marker"),
        (r"causing false.*alert|false.*disconnect", "false_alert_issue"),
        (r"hard.?coded.*proof|proof.*gate.*hard", "hardcoded_proof"),
        (r"not.*proven|proof.*missing|lack.*of.*proof", "missing_proof"),
        (r"eligibility.*not.*check|F&O.*filter.*missing", "missing_filter"),
    ]
    
    def __init__(self, repo_root: Path, outputs_dir: Path):
        """
        Initialize blocker finder.
        
        Args:
            repo_root: Root of Genesis_System3 repo
            outputs_dir: Output directory for reports
        """
        self.repo_root = Path(repo_root)
        self.outputs_dir = Path(outputs_dir)
        self.blockers_found = []
        self.runtime_issues = []
        self.known_blockers = self._load_known_blockers()
        
    def _load_known_blockers(self) -> Dict[str, Dict]:
        """Load SYSTEM3_BLOCKER_REGISTER.md into structured dict."""
        register_file = self.repo_root / "SYSTEM3_BLOCKER_REGISTER.md"
        
        if not register_file.exists():
            return {}
        
        known = {}
        try:
            content = register_file.read_text(encoding="utf-8", errors="replace")
            # Parse markdown table rows
            for line in content.split("\n"):
                if line.startswith("|") and "SYS3-BLK-" in line:
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 2:
                        blk_id = parts[0]
                        known[blk_id] = {
                            "id": blk_id,
                            "severity": parts[1] if len(parts) > 1 else "UNKNOWN",
                            "area": parts[2] if len(parts) > 2 else "",
                            "blocker": parts[3] if len(parts) > 3 else "",
                        }
        except Exception as e:
            print(f"Warning: Could not load known blockers: {e}")
        
        return known
    
    def scan_repo_for_blockers(self) -> List[Dict]:
        """
        Scan tracked source/docs for blocker patterns.

        Prefer `git ls-files` so historical `reports/` / `storage/` trees cannot
        hang the post-market pipeline on Windows.
        """
        findings = []
        skip_parts = {
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
            "dist",
            "build",
            "reports",
            "storage",
            "logs",
            "state",
            "outputs",
            ".cursor",
            ".idea",
            ".vscode",
            "agent-transcripts",
            "coverage",
            "htmlcov",
        }
        compiled = [
            (re.compile(pattern, re.IGNORECASE), pattern_type)
            for pattern, pattern_type in self.BLOCKER_PATTERNS
        ]
        try:
            for path in self._candidate_scan_files(skip_parts):
                try:
                    if path.stat().st_size > 1_000_000:
                        continue
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            if line_no > 5000:
                                break
                            for regex, pattern_type in compiled:
                                if regex.search(line):
                                    findings.append({
                                        "file": str(path.relative_to(self.repo_root)),
                                        "line": line_no,
                                        "pattern": pattern_type,
                                        "snippet": line.strip()[:100],
                                    })
                                    break
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: Repo scan failed: {e}")
        return findings

    def _candidate_scan_files(self, skip_parts: Set[str]) -> List[Path]:
        """Tracked source files first; fall back to a bounded walk."""
        suffixes = {".py", ".md", ".json"}
        tracked: List[Path] = []
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_root),
                    "ls-files",
                    "-z",
                    "*.py",
                    "*.md",
                    "*.json",
                ],
                capture_output=True,
                timeout=60,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                for raw in result.stdout.split(b"\0"):
                    if not raw:
                        continue
                    rel = raw.decode("utf-8", errors="replace").replace("\\", "/")
                    parts = Path(rel).parts
                    if any(part in skip_parts for part in parts):
                        continue
                    path = self.repo_root / rel
                    if path.is_file() and path.suffix.lower() in suffixes:
                        tracked.append(path)
                if tracked:
                    return tracked
        except Exception:
            pass

        files: List[Path] = []
        try:
            for root, dirs, names in os.walk(self.repo_root):
                dirs[:] = [d for d in dirs if d not in skip_parts]
                for name in names:
                    if Path(name).suffix.lower() not in suffixes:
                        continue
                    path = Path(root) / name
                    try:
                        if path.stat().st_size > 1_000_000:
                            continue
                        files.append(path)
                        if len(files) >= 4000:
                            return files
                    except Exception:
                        pass
        except Exception:
            pass
        return files
    
    def check_runtime_state(self, api_url: Optional[str] = None) -> List[Dict]:
        """
        Query runtime API for operational issues.
        
        Returns: List of {issue_type, severity, description, timestamp, ...}
        """
        issues = []
        
        # In production, would hit /api/state and check:
        # - broker.connected vs. alert state contradictions
        # - data_source freshness
        # - qc_status failures
        # - model accuracy gaps
        # - positions without corresponding paper trades
        
        # For now, return template for integration
        if api_url:
            try:
                import requests
                resp = requests.get(f"{api_url}/api/state", timeout=10)
                state = resp.json()
                
                # Check for contradictions
                broker_connected = state.get("broker", {}).get("connected", False)
                has_disconnect_alert = any(
                    a.get("type") == "BROKER_DISCONNECTED" 
                    for a in state.get("alerts", [])
                )
                
                if broker_connected and has_disconnect_alert:
                    issues.append({
                        "type": "CONTRADICTION",
                        "severity": "HIGH",
                        "description": "Broker shows connected but alert says disconnected",
                        "timestamp": datetime.now(IST).isoformat(),
                        "relates_to": "SYS3-BLK-001",
                    })
                
                # Check data freshness
                data_age = state.get("data_age_seconds", 0)
                if data_age > 300:
                    issues.append({
                        "type": "STALE_DATA",
                        "severity": "MEDIUM",
                        "description": f"Data source {data_age}s old",
                        "timestamp": datetime.now(IST).isoformat(),
                        "relates_to": "SYS3-BLK-009",
                    })
            
            except Exception as e:
                print(f"Warning: Runtime check failed: {e}")
        
        return issues
    
    def generate_report(self, output_file: Optional[Path] = None, api_url: Optional[str] = None) -> Dict:
        """
        Generate blocker report combining repo scan + runtime checks.
        
        Returns: {summary, new_blockers, known_blockers, recommendations}
        """
        now = datetime.now(IST)
        
        # Run scans
        repo_findings = self.scan_repo_for_blockers()
        runtime_issues = self.check_runtime_state(api_url)
        
        # Categorize findings
        new_blockers = []
        existing_blockers = self.known_blockers.copy()
        
        for finding in repo_findings:
            # Check if already tracked
            is_known = False
            for blk_id, blk_info in self.known_blockers.items():
                if finding["pattern"] in blk_info.get("blocker", ""):
                    is_known = True
                    break
            
            if not is_known:
                new_blockers.append(finding)
        
        report = {
            "generated_at": now.isoformat(),
            "scan_type": "AUTOMATED_BLOCKER_DISCOVERY",
            "summary": {
                "total_findings": len(repo_findings) + len(runtime_issues),
                "repo_findings": len(repo_findings),
                "runtime_issues": len(runtime_issues),
                "known_blockers": len(existing_blockers),
                "new_potential_blockers": len(new_blockers),
            },
            "new_blockers": new_blockers[:10],  # Top 10
            "known_blockers": list(existing_blockers.values()),
            "runtime_issues": runtime_issues,
            "recommendations": self._generate_recommendations(new_blockers, runtime_issues),
        }
        
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _generate_recommendations(self, new_blockers: List[Dict], 
                                 runtime_issues: List[Dict]) -> List[str]:
        """Generate prioritized recommendations."""
        recs = []
        
        if any("false_alert" in f.get("pattern", "") for f in new_blockers):
            recs.append("FIX_PRIORITY: Investigate false alert patterns (BLK-001)")
        
        if any("missing_proof" in f.get("pattern", "") for f in new_blockers):
            recs.append("FIX_PRIORITY: Add proof gates for untested operations (BLK-003, BLK-005)")
        
        if any("CONTRADICTION" in i.get("type", "") for i in runtime_issues):
            recs.append("FIX_PRIORITY: Resolve runtime state contradictions (BLK-001)")
        
        if any("eligibility" in f.get("pattern", "").lower() for f in new_blockers):
            recs.append("FIX_PRIORITY: Implement F&O eligibility filter (BLK-004)")
        
        return recs


def _configure_stdio() -> None:
    """Windows consoles are often cp1252; never crash the post-market pipeline on print."""
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def parse_blocker_finder_args(argv: Optional[List[str]] = None):
    """Parse CLI. --api-base is accepted for pipeline compatibility; never treat flags as paths."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Automated System3 blocker scan")
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root (default: checkout containing this script)",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Report output directory (default: <repo>/reports/blockers)",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Optional runtime API base URL (reserved for runtime checks)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.output_dir is None:
        args.output_dir = str(Path(args.repo_root) / "reports" / "blockers")
    return args


def run_automated_scan(
    repo_root: str,
    output_dir: str = "/tmp/genesis_blockers",
    api_base: Optional[str] = None,
):
    """
    CLI entry point for automated blocker scan.
    
    Designed to run from CI/CD pipeline or cron job.
    """
    print(f"[SCAN] Starting automated blocker scan at {datetime.now(IST)}...")
    
    finder = SystemBlockerFinder(Path(repo_root), Path(output_dir))
    report = finder.generate_report(Path(output_dir) / "blocker_report.json", api_url=api_base)
    
    print("\n" + "="*60)
    print("BLOCKER SCAN SUMMARY")
    print("="*60)
    print(f"Total findings: {report['summary']['total_findings']}")
    print(f"Repo patterns:  {report['summary']['repo_findings']}")
    print(f"Runtime issues: {report['summary']['runtime_issues']}")
    print(f"Known blockers: {report['summary']['known_blockers']}")
    print(f"NEW blockers:   {report['summary']['new_potential_blockers']}")
    
    if report["recommendations"]:
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    print("\n[OK] Report saved to " + str(Path(output_dir) / "blocker_report.json"))
    return report


if __name__ == "__main__":
    import sys

    _configure_stdio()
    args = parse_blocker_finder_args()
    report = run_automated_scan(args.repo_root, args.output_dir, api_base=args.api_base)
    # Scan completion is success for the post-market pipeline. New findings are reported,
    # not a hard process failure — otherwise Windows/local daily runs fail on emoji/noise.
    new_count = int(report["summary"].get("new_potential_blockers") or 0)
    print(f"\n[DONE] Exit code 0 (scan complete; new_potential_blockers={new_count})")
    raise SystemExit(0)
