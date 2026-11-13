import re
from pathlib import Path

for app_path in [Path(r"C:\content\app\app.py"), Path(r"C:\Genesis_System3_clean\content\app\app.py")]:
    if not app_path.is_file():
        continue
    text = app_path.read_text(encoding="utf-8")
    
    old_block = """    data = SCANNER.bind_order_execution(
        underlying=symbol,
        strike=float(strike),
        option_type=option_type,
        transaction_type=side,
        order_type=order_type,
        price=float(price),
        quantity=int(qty)
    )
    return make_envelope(data, utcnow())"""

    new_block = """    if request.method == "GET":
        data = {
            "status": "READY_FOR_EXECUTION",
            "execution_mode": "PAPER",
            "symbol": symbol.upper(),
            "strike": float(strike),
            "option_type": option_type.upper(),
            "contract": f"{symbol.upper()} {int(strike)} {option_type.upper()}",
            "transaction_type": side.upper(),
            "order_type": order_type.upper(),
            "price": float(price),
            "quantity": int(qty),
            "safety_locks": {"paper_mode": 1, "live_orders_allowed": 0}
        }
        return make_envelope(data, utcnow())

    data = SCANNER.bind_order_execution(
        underlying=symbol,
        strike=float(strike),
        option_type=option_type,
        transaction_type=side,
        order_type=order_type,
        price=float(price),
        quantity=int(qty)
    )
    return make_envelope(data, utcnow())"""

    if old_block in text:
        text = text.replace(old_block, new_block)
        app_path.write_text(text, encoding="utf-8")
        print(f"Patched dhan_orders_dynamic_bind in {app_path}")
    else:
        print(f"old_block not found in {app_path}")
