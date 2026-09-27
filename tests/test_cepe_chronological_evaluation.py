from datetime import date
from pathlib import Path
from hashlib import sha256
import json
import pytest
from scripts.cepe_chronological_evaluation import distribution,split_pairs,source_scope


def test_split_excludes_future_outcome_and_unproven_weekend():
    files = [Path(x+"_fo_bhavcopy.csv") for x in ("20260330","20260331","20260401","20260402","20260406")]
    pairs,gaps = split_pairs(files,date(2026,4,1),date(2026,6,30))
    assert [(a,c) for a,b,c,d in pairs] == [(date(2026,4,1),date(2026,4,2))]
    assert len(gaps) == 1
    validation,_ = split_pairs(files,date(2026,1,1),date(2026,3,31))
    assert len(validation) == 1 and validation[0][2] == date(2026,3,31)


def test_distribution_keeps_losses_and_extreme_multiples_uncapped():
    result = distribution([0.1,1,3,10,20,30,58])
    assert result["quantiles"]["0"] == 0.1
    assert result["quantiles"]["1"] == 58
    assert result["thresholds"] == {"3":5,"10":4,"20":3,"30":2}
    assert result["full_uncapped_distribution_sha256"] == distribution([58,30,20,10,3,1,0.1])["full_uncapped_distribution_sha256"]


def test_partial_directory_cannot_claim_archived_full_phase(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([dict(date="2025-01-01",segment="FO",status="downloaded")]))
    with pytest.raises(ValueError,match="Directory differs"):
        source_scope(tmp_path,date(2025,1,1),date(2025,1,1),manifest)
    assert source_scope(tmp_path,date(2025,1,1),date(2025,1,1))["acquisition_manifest_verified"] is False


def test_manifest_must_account_for_missing_calendar_dates(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([dict(date="2025-01-01",segment="FO",status="source_404")]))
    with pytest.raises(ValueError,match="every requested date"):
        source_scope(tmp_path,date(2025,1,1),date(2025,1,2),manifest)


def test_bound_source_and_404_do_not_prove_holiday_or_market_completeness(tmp_path):
    raw = b"source binding fixture, not actual market evidence"
    p = tmp_path / "20250101_fo_bhavcopy.csv"
    p.write_bytes(raw)
    receipt = dict(csv_sha256=sha256(raw).hexdigest(),segment="FO",date="2025-01-01",
        source="https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20250101_F_0000.csv.zip",
        first_observed_at="2026-09-27T00:00:00Z",zip_sha256="a"*64,status="downloaded")
    p.with_suffix(".receipt.json").write_text(json.dumps(receipt))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([receipt,dict(date="2025-01-02",segment="FO",status="source_404")]))
    result = source_scope(tmp_path,date(2025,1,1),date(2025,1,2),manifest)
    assert result["acquisition_manifest_verified"] is True
    assert result["source_files"] == 1 and result["source_404_dates"] == 1
    assert result["market_calendar_complete"] is False and result["missing_dates_are_holidays"] is False
    p.write_bytes(b"altered fixture")
    with pytest.raises(ValueError,match="Unverified source"):
        source_scope(tmp_path,date(2025,1,1),date(2025,1,2),manifest)
