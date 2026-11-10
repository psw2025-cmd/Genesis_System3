"""Read-only PAPER order/trade book truth projection. Never invent simulated fills."""
from pathlib import Path
from typing import Any, Dict, List
from dashboard.backend.paper_pipeline_v8 import _pipeline_paths, _read_jsonl


def read_paper_books(root: Path | str) -> Dict[str, Any]:
    paths = _pipeline_paths(Path(root))
    orders: List[Dict[str, Any]] = _read_jsonl(paths["orders"])
    seen = set()
    for row in orders:
        order_id = row.get("paper_order_id")
        if not order_id or order_id in seen:
            raise ValueError("PAPER_ORDER_BOOK_INVALID_ID")
        seen.add(order_id)
        if row.get("order_mode") != "ANALYZER_PAPER_ONLY_NO_BROKER_ORDER":
            raise ValueError("PAPER_ORDER_BOOK_UNVERIFIED_MODE")
        if not row.get("created_utc"):
            raise ValueError("PAPER_ORDER_BOOK_MISSING_TIMESTAMP")
    # An opening position or order is NOT independent proof of a trade fill.
    return {
        "source": "core_pipeline_v8",
        "paper_only": True,
        "broker_orders": False,
        "order_book": orders,
        "order_count": len(orders),
        "trade_book": [],
        "trade_count": 0,
        "trade_verification_status": "NOT_VERIFIED",
        "trade_verification_reason": "No independently reconciled simulated fill ledger",
        "generated_from": "paper_order_ledger.jsonl",
    }
