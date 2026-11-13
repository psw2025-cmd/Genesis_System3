from pathlib import Path

path = Path("dashboard/backend/app.py")
content = path.read_text(encoding="utf-8")

old_code = """@app.post("/api/orders/create")
async def create_order(order_data: Dict[str, Any], request: Request = None):
    \"\"\"Create a new order. Gated on: kill switch (inside
    OrderManagement.create_order itself), human approval, and portfolio
    risk limits - previously all three existed but only the dashboard's
    read-only status endpoints ever consulted them; nothing in the
    order-creation path did.\"\"\"
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        try:
            from dashboard.backend.human_approval_service import build_approval_status
        except ImportError:
            from human_approval_service import build_approval_status
        approval = build_approval_status()
        if not approval.get("human_approval"):
            return {
                "status": "ERROR",
                "message": "Order rejected: human approval gate not signed off",
                "approval": approval,
            }"""

new_code = """@app.post("/api/orders/create")
async def create_order(order_data: Dict[str, Any], request: Request = None):
    \"\"\"Create a new order. Gated on: kill switch (inside
    OrderManagement.create_order itself), human approval, and portfolio
    risk limits - previously all three existed but only the dashboard's
    read-only status endpoints ever consulted them; nothing in the
    order-creation path did.\"\"\"
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        # 1. Kill switch check - emergency halt takes precedence over all other logic
        try:
            from core.engine.system3_phase113_kill_switch_monitor import run_phase113
            kill_result = run_phase113()
            if kill_result and kill_result.get("status") == "KILL":
                return {
                    "status": "ERROR",
                    "message": f"Order rejected: kill switch active ({kill_result.get('details')})",
                    "kill_switch": kill_result,
                }
        except Exception:
            pass

        # 2. Human approval gate
        try:
            from dashboard.backend.human_approval_service import build_approval_status
        except ImportError:
            from human_approval_service import build_approval_status
        approval = build_approval_status()
        if not approval.get("human_approval"):
            return {
                "status": "ERROR",
                "message": "Order rejected: human approval gate not signed off",
                "approval": approval,
            }"""

assert old_code in content, "old_code not found in dashboard/backend/app.py"
content = content.replace(old_code, new_code, 1)
path.write_text(content, encoding="utf-8")
print("SUCCESSFULLY_UPDATED_APP_ORDER_KILL_SWITCH_FIRST")
