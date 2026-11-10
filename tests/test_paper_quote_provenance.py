"""Option quote provenance must be explicit before a PAPER entry."""
import json

import pytest

from dashboard.backend.paper_pipeline_v8 import BLOCK_NO_LIVE_QUOTE, _load_chain_quote


@pytest.mark.parametrize("status,source,allowed", [
    ("MARKET_OPEN", "dhan", True),
    ("MARKET_OPEN", "unknown", False),
    ("MARKET_OPEN", "manual", False),
    ("MARKET_OPEN", "csv", False),
    ("MARKET_CLOSED", "dhan", False),
    ("NOT_VERIFIED", "dhan", False),
    ("ERROR", "dhan", False),
])
def test_option_chain_requires_explicit_contract_dhan_provenance(tmp_path, status, source, allowed):
    folder = tmp_path / "src" / "outputs"
    folder.mkdir(parents=True)
    (folder / "chain_NIFTY.json").write_text(json.dumps({
        "data_source": "dhan",
        "source_priority": "dhan_p0_live",
        "status": status,
        "stale": False,
        "contracts": [{"option_type": "CE", "strike": 25000,
                       "ltp": 101.5, "source": source}],
    }))
    quote, reason = _load_chain_quote(tmp_path, "NIFTY", "CE", 25000)
    if allowed:
        assert reason == "OK" and quote is not None
    else:
        assert quote is None and reason == BLOCK_NO_LIVE_QUOTE
