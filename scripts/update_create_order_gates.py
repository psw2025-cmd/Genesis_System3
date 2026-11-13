from pathlib import Path

path = Path("dashboard/backend/app.py")
content = path.read_text(encoding="utf-8")

old_block = """@app.post("/api/orders/create")
@limiter.limit("10/second")
async def create_order(request: Request, order_data: Dict[str, Any]):
    try:
        req = OrderRequest(
            symbol=str(order_data.get("symbol") or "NIFTY"),
            quantity=int(order_data.get("quantity") or 1),
            order_type=str(order_data.get("order_type") or "MARKET"),
            side=str(order_data.get("side") or "BUY"),
            price=float(order_data.get("price")) if order_data.get("price") is not None else None,
            product=str(order_data.get("product") or "MIS"),
            variety=str(order_data.get("variety") or "REGULAR"),
            api_key=request.headers.get("X-API-KEY") or order_data.get("api_key")
        )
    except Exception as val_err:
        raise HTTPException(status_code=400, detail=f"Invalid order payload: {val_err}")
    res = await route_order(req)
    return {"status": "ok" if res.success else "error", "order": res.model_dump()}

async def _legacy_create_order_internal(order_data: Dict[str, Any]):
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
            }

        try:
            live_cfg = json.loads((ROOT_DIR / "config" / "live_trade_config.json").read_text())
        except Exception:
            live_cfg = {}
        risk_limits = {
            "max_positions": live_cfg.get("MAX_OPEN_POSITIONS", 5),
            "max_exposure": live_cfg.get("MAX_EXPOSURE", 100000),
            "max_loss": -abs(live_cfg.get("MAX_DAILY_LOSS", 5000)),
            "max_concentration_pct": live_cfg.get("MAX_CONCENTRATION_PCT", 50),
        }
        positions_data = await get_positions()
        risk_check = get_risk_management().check_risk_limits(positions_data.get("positions", []), risk_limits)
        if risk_check.get("status") == "FAIL":
            return {"status": "ERROR", "message": "Order rejected: risk limits breached", "risk_check": risk_check}

        order_mgmt = get_order_management()
        order = order_mgmt.create_order(
            symbol=order_data.get("symbol"),
            order_type=order_data.get("order_type", "MARKET"),
            quantity=order_data.get("quantity", 0),
            price=order_data.get("price"),
            stop_loss=order_data.get("stop_loss"),
            target=order_data.get("target"),
            trailing_stop_pct=order_data.get("trailing_stop_pct"),
        )

        return {"status": "ok", "order": order}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}"""

new_block = """@app.post("/api/orders/create")
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
            }

        try:
            live_cfg = json.loads((ROOT_DIR / "config" / "live_trade_config.json").read_text())
        except Exception:
            live_cfg = {}
        risk_limits = {
            "max_positions": live_cfg.get("MAX_OPEN_POSITIONS", 5),
            "max_exposure": live_cfg.get("MAX_EXPOSURE", 100000),
            "max_loss": -abs(live_cfg.get("MAX_DAILY_LOSS", 5000)),
            "max_concentration_pct": live_cfg.get("MAX_CONCENTRATION_PCT", 50),
        }
        positions_data = await get_positions()
        risk_check = get_risk_management().check_risk_limits(positions_data.get("positions", []), risk_limits)
        if risk_check.get("status") == "FAIL":
            return {"status": "ERROR", "message": "Order rejected: risk limits breached", "risk_check": risk_check}

        order_mgmt = get_order_management()
        order = order_mgmt.create_order(
            symbol=order_data.get("symbol"),
            order_type=order_data.get("order_type", "MARKET"),
            quantity=order_data.get("quantity", 0),
            price=order_data.get("price"),
            stop_loss=order_data.get("stop_loss"),
            target=order_data.get("target"),
            trailing_stop_pct=order_data.get("trailing_stop_pct"),
        )

        return {"status": "ok", "order": order}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}"""

assert old_block in content, "old_block not found in dashboard/backend/app.py"
content = content.replace(old_block, new_block, 1)
path.write_text(content, encoding="utf-8")
print("SUCCESSFULLY_UPDATED_CREATE_ORDER")
