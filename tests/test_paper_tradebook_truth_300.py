"""Paper trade book must not fabricate fills from order records."""
import json
import pytest
from dashboard.backend.paper_book_truth import read_paper_books
from dashboard.backend.paper_pipeline_v8 import _pipeline_paths

@pytest.mark.parametrize("index",range(300))
def test_order_is_never_misrepresented_as_trade_fill(tmp_path,index):
    path=_pipeline_paths(tmp_path)["orders"]
    path.parent.mkdir(parents=True,exist_ok=True)
    row={"paper_order_id":f"order-{index}","order_mode":"ANALYZER_PAPER_ONLY_NO_BROKER_ORDER","created_utc":"2026-11-07T05:00:00+00:00","qty":index+1,"status":"PAPER_OPEN"}
    path.write_text(json.dumps(row)+"\\n")
    books=read_paper_books(tmp_path)
    assert books["order_count"]==1
    assert books["trade_count"]==0
    assert books["trade_book"]==[]
    assert books["trade_verification_status"]=="NOT_VERIFIED"

def test_duplicate_order_id_blocks_truth(tmp_path):
    path=_pipeline_paths(tmp_path)["orders"]
    path.parent.mkdir(parents=True,exist_ok=True)
    row={"paper_order_id":"dup","order_mode":"ANALYZER_PAPER_ONLY_NO_BROKER_ORDER","created_utc":"2026-11-07T05:00:00+00:00"}
    path.write_text(json.dumps(row)+"\\n"+json.dumps(row)+"\\n")
    with pytest.raises(ValueError,match="INVALID_ID"):
        read_paper_books(tmp_path)

def test_empty_books_are_not_verified(tmp_path):
    books=read_paper_books(tmp_path)
    assert books["order_count"]==0 and books["trade_count"]==0
    assert books["trade_verification_status"]=="NOT_VERIFIED"
