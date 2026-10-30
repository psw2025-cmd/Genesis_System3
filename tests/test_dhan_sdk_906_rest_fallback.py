"""DH-906 SDK response may permit one read-only REST attempt; auth errors do not."""
from unittest.mock import patch
import pytest
from core.brokers.dhan import dhan_readonly as d

@pytest.mark.parametrize("method,sdk_method", [
    ("get_funds", "get_fund_limits"),
    ("get_holdings", "get_holdings"),
    ("get_positions", "get_positions"),
])
def test_sdk_906_reconciles_once_via_readonly_rest(method, sdk_method):
    class Fake:
        pass
    client = Fake()
    setattr(client, sdk_method, lambda: {"status": "failure", "remarks": {"error_code": "DH-906", "error_message": "Incorrect Request"}})
    with patch.object(d, "get_dhan_credentials", return_value={"client_id": "test", "access_token": "dummy"}), \
         patch.object(d, "create_dhan_client", return_value=client), \
         patch.object(d, "_rest_get", return_value={"status": "success", "data": []}) as req:
        result = getattr(d, method)()
        assert result["success"] is True
        assert result["source"] == "rest"
        assert req.call_count == 1

@pytest.mark.parametrize("method,sdk_method", [
    ("get_funds", "get_fund_limits"),
    ("get_holdings", "get_holdings"),
    ("get_positions", "get_positions"),
])
def test_sdk_auth_error_does_not_retry(method, sdk_method):
    class Fake:
        pass
    client = Fake()
    setattr(client, sdk_method, lambda: {"status": "failure", "remarks": {"error_code": "DH-808", "error_message": "Invalid Access Token"}})
    with patch.object(d, "get_dhan_credentials", return_value={"client_id": "test", "access_token": "dummy"}), \
         patch.object(d, "create_dhan_client", return_value=client), \
         patch.object(d, "_rest_get") as req:
        result = getattr(d, method)()
        assert result["success"] is False
        req.assert_not_called()
