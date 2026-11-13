import re

path = 'c:/Genesis_System3_clean/core/engine/dhan_full_market_scanner.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """            slippage = 0.15
            fill_price = round(price + slippage if transaction_type == "BUY" else price - slippage, 2)
            brokerage = 20.0
            stt = round(fill_price * qty * 0.00125, 2)
            total_turnover = round(fill_price * qty, 2)

            return {
                "status": "SUCCESS",
                "execution_mode": "PAPER",
                "order_id": f"ORD-DHAN-PAPER-{int(datetime.now().timestamp())}",
                "symbol": und,
                "contract": f"{und} {int(strike)} {opt}",
                "security_id": sec_id,
                "transaction_type": transaction_type.upper(),
                "order_type": order_type.upper(),
                "requested_price": price,
                "fill_price": fill_price,
                "slippage": slippage,
                "quantity": qty,
                "lot_size": lot,
                "brokerage_inr": brokerage,
                "stt_inr": stt,
                "turnover_inr": total_turnover,
                "dhan_payload": dhan_payload,
                "message": "Paper order validated against Dhan schema and filled in simulated ledger."
            }"""

replacement = """            slippage = 0.15
            fill_price = round(price + slippage if transaction_type == "BUY" else price - slippage, 2)
            brokerage = 20.0
            stt = round(fill_price * qty * 0.00125, 2)
            total_turnover = round(fill_price * qty, 2)
            order_id = f"ORD-DHAN-PAPER-{int(datetime.now().timestamp())}"

            # Auto-dispatch paper execution fill receipt to Telegram downstream (@System3PSWBot)
            try:
                from core.engine.telegram_notifier import default_telegram_notifier
                receipt_msg = default_telegram_notifier.format_paper_fill_receipt(
                    order_id=order_id,
                    symbol=f"{und} {int(strike)} {opt}",
                    side=transaction_type.upper(),
                    qty=qty,
                    fill_price=fill_price,
                    slippage_pts=slippage,
                    brokerage_inr=brokerage,
                    stt_inr=stt
                )
                default_telegram_notifier.dispatch(text=receipt_msg, category="PAPER_EXECUTION")
            except Exception:
                pass

            return {
                "status": "SUCCESS",
                "execution_mode": "PAPER",
                "order_id": order_id,
                "symbol": und,
                "contract": f"{und} {int(strike)} {opt}",
                "security_id": sec_id,
                "transaction_type": transaction_type.upper(),
                "order_type": order_type.upper(),
                "requested_price": price,
                "fill_price": fill_price,
                "slippage": slippage,
                "quantity": qty,
                "lot_size": lot,
                "brokerage_inr": brokerage,
                "stt_inr": stt,
                "turnover_inr": total_turnover,
                "dhan_payload": dhan_payload,
                "message": "Paper order validated against Dhan schema and filled in simulated ledger."
            }"""

code_norm = code.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

if target_norm in code_norm:
    new_code = code_norm.replace(target_norm, replacement_norm)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_code)
    print("SUCCESS: Patched dhan_full_market_scanner.py with Telegram dispatch.")
else:
    print("FAILED: Target not matched in dhan_full_market_scanner.py.")
