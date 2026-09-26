"""Synthetic acquisition contracts, never evidence of market performance."""
from datetime import date
from io import BytesIO
import json
from zipfile import ZipFile

import pytest

from scripts import nse_bulk_backfill as bulk


def test_all_404_never_means_complete_and_weekends_are_attempted(tmp_path, monkeypatch):
    attempted = []

    def missing(day, segment, output):
        attempted.append(day)
        return dict(date=day.isoformat(), segment=segment, status="source_404")

    monkeypatch.setattr(bulk, "fetch", missing)
    result = bulk.backfill(date(2026, 9, 25), date(2026, 9, 28), ["FO"], tmp_path)
    assert len(attempted) == 4
    assert date(2026, 9, 26) in attempted and date(2026, 9, 27) in attempted
    assert result["download_attempts_completed"] is True
    assert result["coverage_complete"] is False
    assert result["missing_dates_are_holidays"] is False


def test_download_date_and_hash_bound_cache_retain_original_observation(tmp_path, monkeypatch):
    data = b"TradDt,TckrSymb\n2026-09-25,ABC\n"
    zipped = BytesIO()
    with ZipFile(zipped, "w") as archive:
        archive.writestr("test.csv", data)
    monkeypatch.setattr(bulk, "urlopen", lambda *a, **kw: BytesIO(zipped.getvalue()))
    day = date(2026, 9, 25)
    first = bulk.fetch(day, "FO", tmp_path)
    second = bulk.fetch(day, "FO", tmp_path)
    assert first["status"] == "downloaded" and first["row_count"] == 1
    assert second["status"] == "already_present"
    assert second["first_observed_at"] == first["first_observed_at"]
    assert second["zip_sha256"] == first["zip_sha256"]
    (tmp_path / "20260925_fo_bhavcopy.csv").write_bytes(data.replace(b"ABC", b"DEF"))
    assert bulk.fetch(day, "FO", tmp_path)["status"] == "existing_unverified"


def test_unreceipted_local_file_is_not_authenticated_or_overwritten(tmp_path):
    path = tmp_path / "20260925_fo_bhavcopy.csv"
    raw = b"TradDt,TckrSymb\n2026-09-25,ABC\n"
    path.write_bytes(raw)
    result = bulk.fetch(date(2026, 9, 25), "FO", tmp_path)
    assert result["status"] == "existing_unverified" and path.read_bytes() == raw


@pytest.mark.parametrize("raw", [b"TradDt,TckrSymb\n", b"TradDt,TckrSymb\n2026-09-24,ABC\n"])
def test_empty_or_wrong_date_csv_rejected(raw):
    with pytest.raises(ValueError):
        bulk.validate_csv(raw, date(2026, 9, 25))


def test_manifest_history_is_not_rewritten(tmp_path, monkeypatch):
    monkeypatch.setattr(bulk, "fetch", lambda day, segment, output:
                        dict(date=day.isoformat(), segment=segment, status="downloaded"))
    args = (date(2026, 9, 25), date(2026, 9, 25), ["FO"], tmp_path)
    first, second = bulk.backfill(*args), bulk.backfill(*args)
    assert first["manifest"] != second["manifest"]
    assert len(list(tmp_path.glob("manifest-*.jsonl"))) == 2
    assert json.loads(next(tmp_path.glob("manifest-*.jsonl")).read_text())["date"] == "2026-09-25"
    assert second["coverage_complete"] is True


def test_empty_segment_request_rejected(tmp_path):
    with pytest.raises(ValueError):
        bulk.backfill(date(2026, 9, 25), date(2026, 9, 25), [], tmp_path)
