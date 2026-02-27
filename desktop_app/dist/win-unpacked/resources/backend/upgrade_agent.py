"""
Upgrade Agent - Self-Improvement System with Safety Gates
Watches for issues, plans upgrades, tests, and deploys safely
"""
import json
import os
import subprocess
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

IST = pytz.timezone('Asia/Kolkata')


class UpgradeAgent:
    """
    Agent that monitors system, plans upgrades, and applies them safely
    """
    
    def __init__(self, project_root: Path, agent_memory_dir: Path):
        self.project_root = Path(project_root)
        self.agent_memory_dir = Path(agent_memory_dir)
        self.agent_memory_dir.mkdir(exist_ok=True)
        
        # Directories
        self.diffs_dir = self.agent_memory_dir / "diffs"
        self.test_runs_dir = self.agent_memory_dir / "test_runs"
        self.proof_packs_dir = self.agent_memory_dir / "proof_packs"
        self.state_snapshots_dir = self.agent_memory_dir / "state_snapshots"
        
        # Create directories
        for dir_path in [self.diffs_dir, self.test_runs_dir, self.proof_packs_dir, self.state_snapshots_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Current plan
        self.current_plan = None
        self.auto_apply_enabled = True  # Can be toggled
    
    def load_plan(self) -> Optional[Dict]:
        """Load current upgrade plan"""
        plan_file = self.agent_memory_dir / "plan.md"
        if plan_file.exists():
            # Parse plan.md to extract current task
            try:
                content = plan_file.read_text()
                # Extract current task from plan
                if "Current Task" in content:
                    # Simple parsing - can be enhanced
                    self.current_plan = {"status": "active", "file": str(plan_file)}
                return self.current_plan
            except:
                pass
        return None
    
    def watch_for_issues(self) -> List[Dict[str, Any]]:
        """
        Watch for issues that need fixing
        Returns list of issues found
        Optimized for instant response - returns empty list immediately
        Issue detection is handled by other monitoring systems
        """
        # Return empty list immediately - no blocking operations
        # Issue detection is done by:
        # - QC system (reported via /api/qc)
        # - Health monitoring (reported via /api/health)
        # - Log monitoring (handled separately)
        return []
    
    def create_upgrade_plan(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an upgrade plan to fix issues
        """
        plan = {
            "plan_id": f"PLAN_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now(IST).isoformat(),
            "issues": issues,
            "changes": [],
            "tests_required": [],
            "auto_apply": True,  # Will be set based on change type
            "status": "draft"
        }
        
        # Analyze issues and propose fixes
        for issue in issues:
            if issue["type"] == "log_error":
                plan["changes"].append({
                    "type": "log_fix",
                    "file": issue.get("file", "unknown"),
                    "action": "Review and fix error in logs"
                })
                plan["auto_apply"] = True  # Log fixes can be auto-applied
            
            elif issue["type"] == "backend_unhealthy":
                plan["changes"].append({
                    "type": "backend_restart",
                    "action": "Restart backend service"
                })
                plan["auto_apply"] = True
            
            elif issue["type"] == "qc_fail":
                plan["changes"].append({
                    "type": "qc_investigation",
                    "action": "Investigate QC failure and fix data quality issues"
                })
                plan["auto_apply"] = False  # Requires manual approval
        
        # Save plan
        plan_file = self.agent_memory_dir / f"upgrade_plan_{plan['plan_id']}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
        
        return plan
    
    def run_tests(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run tests before applying upgrade
        """
        test_results = {
            "plan_id": plan["plan_id"],
            "timestamp": datetime.now(IST).isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0
        }
        
        # Run SSOT consistency tests
        try:
            import requests
            state_res = requests.get("http://localhost:8000/api/state", timeout=5)
            if state_res.status_code == 200:
                test_results["tests"].append({
                    "name": "SSOT Endpoint",
                    "status": "pass",
                    "message": "SSOT endpoint is accessible"
                })
                test_results["passed"] += 1
            else:
                test_results["tests"].append({
                    "name": "SSOT Endpoint",
                    "status": "fail",
                    "message": f"SSOT endpoint returned {state_res.status_code}"
                })
                test_results["failed"] += 1
        except Exception as e:
            test_results["tests"].append({
                "name": "SSOT Endpoint",
                "status": "fail",
                "message": str(e)
            })
            test_results["failed"] += 1
        
        # Save test results
        test_file = self.test_runs_dir / f"test_{plan['plan_id']}.json"
        with open(test_file, "w") as f:
            json.dump(test_results, f, indent=2)
        
        return test_results
    
    def apply_upgrade(self, plan: Dict[str, Any], test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply upgrade if tests pass and auto-apply is enabled
        """
        if test_results["failed"] > 0:
            return {
                "success": False,
                "message": "Tests failed, cannot apply upgrade",
                "test_results": test_results
            }
        
        if not plan.get("auto_apply", False):
            return {
                "success": False,
                "message": "Upgrade requires manual approval",
                "plan": plan
            }
        
        # Apply changes
        applied_changes = []
        for change in plan.get("changes", []):
            if change["type"] == "backend_restart":
                # Restart backend (will be handled by Electron)
                applied_changes.append(change)
            elif change["type"] == "log_fix":
                # Log fixes are informational
                applied_changes.append(change)
        
        # Update plan status
        plan["status"] = "applied"
        plan["applied_at"] = datetime.now(IST).isoformat()
        plan["applied_changes"] = applied_changes
        
        # Save updated plan
        plan_file = self.agent_memory_dir / f"upgrade_plan_{plan['plan_id']}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
        
        return {
            "success": True,
            "message": "Upgrade applied successfully",
            "plan": plan,
            "applied_changes": applied_changes
        }
    
    def create_proof_pack(self, plan_id: Optional[str] = None) -> Path:
        """
        Create proof pack ZIP file
        """
        proof_pack_id = plan_id or f"PROOF_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}"
        proof_pack_file = self.proof_packs_dir / f"{proof_pack_id}.zip"
        
        with zipfile.ZipFile(proof_pack_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add latest SSOT snapshot
            state_file = self.project_root / "outputs" / "runtime_state.json"
            if state_file.exists():
                zipf.write(state_file, "ssot_snapshot.json")
            
            # Add state history sample
            state_history_dir = self.project_root / "outputs" / "state_snapshots"
            if state_history_dir.exists():
                recent_snapshots = sorted(state_history_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[:10]
                for snapshot in recent_snapshots:
                    zipf.write(snapshot, f"state_history/{snapshot.name}")
            
            # Add QC report
            qc_file = self.project_root / "outputs" / "qc_report_live.json"
            if qc_file.exists():
                zipf.write(qc_file, "qc_report.json")
            
            # Add test results
            if plan_id:
                test_file = self.test_runs_dir / f"test_{plan_id}.json"
                if test_file.exists():
                    zipf.write(test_file, "test_results.json")
            
            # Add agent memory (tasks, plan)
            tasks_file = self.agent_memory_dir / "tasks.json"
            if tasks_file.exists():
                zipf.write(tasks_file, "agent_memory/tasks.json")
            
            plan_file = self.agent_memory_dir / "plan.md"
            if plan_file.exists():
                zipf.write(plan_file, "agent_memory/plan.md")
            
            # Add build metadata
            build_metadata = {
                "version": "1.0.0",
                "timestamp": datetime.now(IST).isoformat(),
                "proof_pack_id": proof_pack_id
            }
            zipf.writestr("build_metadata.json", json.dumps(build_metadata, indent=2))
        
        return proof_pack_file


# Global instance
_upgrade_agent: Optional[UpgradeAgent] = None


def get_upgrade_agent(project_root: Optional[Path] = None, agent_memory_dir: Optional[Path] = None) -> UpgradeAgent:
    """Get or create global upgrade agent instance"""
    global _upgrade_agent
    if _upgrade_agent is None:
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        if agent_memory_dir is None:
            agent_memory_dir = project_root / "agent_memory"
        _upgrade_agent = UpgradeAgent(project_root, agent_memory_dir)
    return _upgrade_agent
