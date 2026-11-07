"""400 corruption scenarios protecting the real paper position book."""
import json
import pytest
from dashboard.backend.paper_pipeline_v8 import _pipeline_paths, _update_positions_and_pnl

def _order():
    return {"position_id":"PV8-test","paper_order_id":"test","underlying":"NIFTY","contract_symbol":"NIFTY-CE","qty":25,"entry_price":100.0,"created_utc":"2026-11-07T05:00:00+00:00"}

@pytest.mark.parametrize("suffix",range(400))
def test_corrupt_position_book_never_resets_or_appends(tmp_path,suffix):
    paths=_pipeline_paths(tmp_path)
    path=paths["positions"]
    path.parent.mkdir(parents=True,exist_ok=True)
    # Every payload has a distinct invalid JSON suffix; existing evidence must remain byte-identical.
    original='{"positions":[{"position_id":"historical"}],"open_count":1}' + ('!' * (suffix+1))
    path.write_text(original,encoding="utf-8")
    with pytest.raises(ValueError,match="PAPER_POSITIONS_CORRUPT"):
        _update_positions_and_pnl(tmp_path,_order())
    assert path.read_text(encoding="utf-8")==original
    assert not paths["pnl_summary"].exists()

@pytest.mark.parametrize("payload",['[]','null','{}','{"positions":{}}','{"positions":[null]}','{"positions":[{}]}'])
def test_invalid_position_schema_blocks_writes(tmp_path,payload):
    path=_pipeline_paths(tmp_path)["positions"]
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(payload)
    with pytest.raises(ValueError,match="PAPER_POSITIONS_INVALID"):
        _update_positions_and_pnl(tmp_path,_order())
    assert path.read_text()==payload

def test_new_position_book_still_works(tmp_path):
    _update_positions_and_pnl(tmp_path,_order())
    book=json.loads(_pipeline_paths(tmp_path)["positions"].read_text())
    assert book["open_count"]==1
