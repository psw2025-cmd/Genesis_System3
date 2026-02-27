"""
Add Upgrade Agent endpoints to app.py
This script adds the upgrade agent API endpoints
"""

import re
from pathlib import Path

app_file = Path("dashboard/backend/app.py")

# Read the file
content = app_file.read_text(encoding="utf-8")

# Check if upgrade agent endpoints already exist
if "/api/agent/memory" in content:
    print("Upgrade agent endpoints already exist")
else:
    # Find the shutdown event
    shutdown_pattern = r'@app\.on_event\("shutdown"\)'

    # Insert upgrade agent endpoints before shutdown
    upgrade_agent_code = '''
# Upgrade Agent Endpoints
try:
    from dashboard.backend.upgrade_agent import get_upgrade_agent
    UPGRADE_AGENT_AVAILABLE = True
except ImportError:
    try:
        from upgrade_agent import get_upgrade_agent
        UPGRADE_AGENT_AVAILABLE = True
    except ImportError:
        UPGRADE_AGENT_AVAILABLE = False
        print("Warning: Upgrade agent not available")

if UPGRADE_AGENT_AVAILABLE:
    upgrade_agent = get_upgrade_agent(ROOT_DIR, ROOT_DIR / "agent_memory")

@app.get("/api/agent/memory")
async def get_agent_memory():
    """Get agent memory (tasks, plan)"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}
        
        memory_file = ROOT_DIR / "agent_memory" / "tasks.json"
        if memory_file.exists():
            return json.loads(memory_file.read_text())
        return {"status": "ok", "tasks": [], "run_id": "NONE"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/agent/issues")
async def get_agent_issues():
    """Get detected issues"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available", "issues": []}
        
        issues = upgrade_agent.watch_for_issues()
        return {"status": "ok", "issues": issues}
    except Exception as e:
        return {"status": "error", "message": str(e), "issues": []}

@app.get("/api/agent/upgrade-plan")
async def get_upgrade_plan():
    """Get current upgrade plan"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "none", "message": "Upgrade agent not available"}
        
        plan_files = sorted(
            (ROOT_DIR / "agent_memory").glob("upgrade_plan_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if plan_files:
            plan = json.loads(plan_files[0].read_text())
            if plan.get("status") in ["draft", "ready"]:
                return {"status": "ok", **plan}
        
        return {"status": "none", "message": "No pending upgrade plan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/agent/create-plan")
async def create_upgrade_plan():
    """Create new upgrade plan from detected issues"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}
        
        issues = upgrade_agent.watch_for_issues()
        if not issues:
            return {"status": "ok", "message": "No issues detected", "plan": None}
        
        plan = upgrade_agent.create_upgrade_plan(issues)
        test_results = upgrade_agent.run_tests(plan)
        
        if test_results["failed"] == 0:
            plan["status"] = "ready"
        else:
            plan["status"] = "needs_fix"
        
        plan_file = ROOT_DIR / "agent_memory" / f"upgrade_plan_{plan['plan_id']}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
        
        return {"status": "ok", "plan": plan, "test_results": test_results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/agent/apply-upgrade")
async def apply_upgrade(plan_data: Dict[str, Any]):
    """Apply upgrade plan"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}
        
        plan_id = plan_data.get("plan_id")
        if not plan_id:
            return {"status": "error", "message": "plan_id required"}
        
        plan_file = ROOT_DIR / "agent_memory" / f"upgrade_plan_{plan_id}.json"
        if not plan_file.exists():
            return {"status": "error", "message": "Plan not found"}
        
        plan = json.loads(plan_file.read_text())
        test_results = upgrade_agent.run_tests(plan)
        result = upgrade_agent.apply_upgrade(plan, test_results)
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/agent/rollback")
async def rollback_upgrade():
    """Rollback last upgrade"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}
        
        plan_files = sorted(
            (ROOT_DIR / "agent_memory").glob("upgrade_plan_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for plan_file in plan_files:
            plan = json.loads(plan_file.read_text())
            if plan.get("status") == "applied":
                plan["status"] = "rolled_back"
                plan["rolled_back_at"] = datetime.now(IST).isoformat()
                with open(plan_file, "w") as f:
                    json.dump(plan, f, indent=2)
                
                return {"status": "ok", "success": True, "message": "Rollback initiated"}
        
        return {"status": "error", "success": False, "message": "No applied upgrade found"}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e)}

@app.get("/api/agent/test-results/{plan_id}")
async def get_test_results(plan_id: str):
    """Get test results for a plan"""
    try:
        test_file = ROOT_DIR / "agent_memory" / "test_runs" / f"test_{plan_id}.json"
        if test_file.exists():
            return json.loads(test_file.read_text())
        return {"status": "error", "message": "Test results not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/agent/pause")
async def pause_agent():
    """Pause/resume upgrade agent"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}
        
        upgrade_agent.auto_apply_enabled = not upgrade_agent.auto_apply_enabled
        return {"status": "ok", "paused": not upgrade_agent.auto_apply_enabled}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/proof-pack")
async def get_proof_pack():
    """Download proof pack ZIP"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Upgrade agent not available")
        
        proof_pack_file = upgrade_agent.create_proof_pack()
        
        return FileResponse(
            proof_pack_file,
            media_type="application/zip",
            filename=f"proof_pack_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}.zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''

    # Insert before shutdown event
    if re.search(shutdown_pattern, content):
        content = re.sub(shutdown_pattern, upgrade_agent_code + "\n" + r'@app.on_event("shutdown")', content)
        app_file.write_text(content, encoding="utf-8")
        print("[OK] Upgrade agent endpoints added to app.py")
    else:
        # Append at the end
        content += upgrade_agent_code
        app_file.write_text(content, encoding="utf-8")
        print("[OK] Upgrade agent endpoints appended to app.py")
