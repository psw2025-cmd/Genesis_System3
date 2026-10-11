from datetime import date
from pathlib import Path
from hashlib import sha256
import json
import pytest
from scripts.cepe_chronological_evaluation import (
    distribution,pair_session_calendar,session_calendar,source_scope,split_pairs,
)


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


def test_official_sessions_join_weekend_without_joining_missing_session():
    files = [Path(x+"_fo_bhavcopy.csv") for x in ("20260401","20260402","20260406")]
    sessions = [date(2026,4,1),date(2026,4,2),date(2026,4,6)]
    pairs,gaps = split_pairs(files,date(2026,4,1),date(2026,4,6),sessions)
    assert [(a,c) for a,b,c,d in pairs] == [
        (date(2026,4,1),date(2026,4,2)),
        (date(2026,4,2),date(2026,4,6)),
    ]
    assert gaps == []
    with pytest.raises(ValueError,match="official session calendar"):
        split_pairs(files[:-1],date(2026,4,1),date(2026,4,6),sessions)


def test_session_calendar_is_exact_hash_and_digest_bound(tmp_path):
    expected = ["2025-01-01","2025-01-02","2025-01-03"]
    evidence = {
        "schema_version":1,"segment":"FO",
        "scope":{"start":"2025-01-01","end":"2025-01-05"},
        "first_observed_at":"2026-09-27T00:00:00Z",
        "official_sources":[{
            "circular":"NSE/FAOP/65588",
            "url":"https://nsearchives.nseindia.com/content/circulars/FAOP65588.pdf",
            "calendar_year":2025,"override_dates":[],"raw_pdf_sha256":"a"*64,
        }],
        "holidays":[],"special_live_sessions":[],
        "session_dates_sha256":sha256("\n".join(expected).encode()).hexdigest(),
    }
    path = tmp_path / "calendar.json"
    path.write_text(json.dumps(evidence))
    sessions,receipt = session_calendar(path,date(2025,1,1),date(2025,1,5))
    assert [day.isoformat() for day in sessions] == expected
    assert receipt["raw_pdf_hashes_complete"] is True
    evidence["session_dates_sha256"] = "0"*64
    path.write_text(json.dumps(evidence))
    with pytest.raises(ValueError,match="digest mismatch"):
        session_calendar(path,date(2025,1,1),date(2025,1,5))


def test_pair_calendar_binds_weekend_to_official_sources():
    sessions = [date(2025,1,3),date(2025,1,6)]
    receipt = {"first_observed_at":"2026-09-27T00:00:00Z","official_sources":[{
        "circular":"NSE/FAOP/65588",
        "url":"https://nsearchives.nseindia.com/content/circulars/FAOP65588.pdf",
        "raw_pdf_sha256":"a"*64,"calendar_year":2025,"override_dates":[],
    }]}
    calendar = json.loads(pair_session_calendar(
        date(2025,1,3),date(2025,1,6),sessions,receipt))
    assert calendar["schema"] == "nse-session-calendar-v2"
    assert calendar["days"]["2025-01-04"] is None
    assert calendar["days"]["2025-01-05"] is None
    assert calendar["sources"][0]["sha256"] == "a"*64


def test_manifest_must_account_for_every_requested_date(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([dict(date="2025-01-01",segment="FO",status="source_404")]))
    with pytest.raises(ValueError,match="every requested date"):
        source_scope(tmp_path,date(2025,1,1),date(2025,1,2),manifest)


def test_multiple_manifests_and_official_sessions_prove_scope(tmp_path):
    manifests = []
    for index,day in enumerate(("2025-01-01","2025-01-02")):
        raw = f"source binding fixture {day}".encode()
        compact = day.replace("-","")
        path = tmp_path / f"{compact}_fo_bhavcopy.csv"
        path.write_bytes(raw)
        receipt = dict(csv_sha256=sha256(raw).hexdigest(),segment="FO",date=day,
            source=f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{compact}_F_0000.csv.zip",
            first_observed_at="2026-09-27T00:00:00Z",zip_sha256="a"*64,status="downloaded")
        path.with_suffix(".receipt.json").write_text(json.dumps(receipt))
        manifest = tmp_path / f"manifest-{index}.jsonl"
        manifest.write_text(json.dumps(receipt)+"\n")
        manifests.append(manifest)
    result = source_scope(tmp_path,date(2025,1,1),date(2025,1,2),manifests,
        official_sessions=[date(2025,1,1),date(2025,1,2)],calendar_receipt={"status":"fixture"})
    assert result["market_calendar_complete"] is True
    assert len(result["manifest_receipts"]) == 2
