import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.validation.qc_validator import QCValidator
from tools.qc_runtime_anomaly_audit import is_market_closed_zero_expected


def test_empty_dataframe_fails_cleanly_without_crash():
    passed, reasons = QCValidator().validate_snapshot(pd.DataFrame(), "NIFTY")

    assert passed is False
    assert reasons == ["No contracts to validate"]


def test_bid_ask_complete_pair_priority_does_not_mix_partial_legacy_with_full_dhan_pair():
    df = pd.DataFrame(
        {
            "bidPrice": [999.0],
            "top_bid_price": [100.0],
            "top_ask_price": [101.0],
        }
    )

    assert QCValidator._bid_ask_columns(df) == ("top_bid_price", "top_ask_price")


def test_runtime_qc_route_exists_in_fastapi_app():
    spec = importlib.util.spec_from_file_location(
        "dashboard_backend_app_runtime_qc_test", ROOT_DIR / "dashboard" / "backend" / "app.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    routes = {getattr(route, "path", None) for route in mod.app.routes}
    assert "/api/qc/runtime" in routes


def test_market_closed_zero_contracts_are_expected_skip_not_critical():
    result = {
        "status": "MARKET_CLOSED_EXPECTED",
        "market_open": False,
        "skipped": True,
        "total_contracts": 0,
    }

    assert is_market_closed_zero_expected(result) is True
