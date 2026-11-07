"""Research leakage regression: timezone, unsorted rows and shared timestamp."""
import pytest
from datetime import datetime
from dashboard.backend.lifetime_research_engine import OutcomeRow, walk_forward_windows

def row(ts):
    return OutcomeRow(ts=ts,symbol="NIFTY",side="CE",strategy="S1",return_pct=.01,source="TEST")

def test_unsorted_and_timezone_offset_windows_are_chronological():
    rows=[row("2026-01-01T09:00:00+05:30"),row("2026-01-01T04:00:00Z"),
          row("2026-01-01T09:30:00+05:30"),row("2026-01-01T04:30:00Z"),
          row("2026-01-01T10:00:00+05:30"),row("2026-01-01T05:00:00Z")]
    windows=walk_forward_windows(list(reversed(rows)),2,2)
    assert windows
    for train,test in windows:
        end=max(datetime.fromisoformat(x.ts.replace("Z","+00:00")).timestamp() for x in train)
        start=min(datetime.fromisoformat(x.ts.replace("Z","+00:00")).timestamp() for x in test)
        assert end<start

def test_shared_boundary_timestamp_never_leaks():
    rows=[row("2026-01-01T09:00:00+05:30"),
          row("2026-01-01T09:01:00+05:30"),
          row("2026-01-01T03:31:00Z"),
          row("2026-01-01T09:02:00+05:30")]
    assert walk_forward_windows(rows,2,2)==[]

@pytest.mark.parametrize("bad",["2026-01-01T09:00:00","not-a-time",""])
def test_invalid_timestamp_rejected(bad):
    with pytest.raises(ValueError):
        walk_forward_windows([row(bad),row("2026-01-02T09:00:00+05:30")],1,1)

@pytest.mark.parametrize("train,test",[(0,1),(1,0),(-1,2),(True,1)])
def test_invalid_window_size_rejected(train,test):
    with pytest.raises(ValueError,match="INVALID_WALK_FORWARD_WINDOW_SIZES"):
        walk_forward_windows([row("2026-01-01T09:00:00+05:30")],train,test)
