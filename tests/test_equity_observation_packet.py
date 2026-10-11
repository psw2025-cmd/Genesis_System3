"""Synthetic failure/identity tests; these do not validate market returns."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import csv
import io
import json
from zipfile import ZipFile

import pytest

from scripts.equity_observation_packet import build_packet, CM_URL
from scripts.equity_instrument_scope import EQUITY_URL, ETF_URL

NOW = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
AS_OF = "2026-10-01T10:01:00Z"
MEMBER = "BhavCopy_NSE_CM_0_0_0_20260930_F_0000.csv"
FIELDS = "TradDt,BizDt,Sgmt,Src,FinInstrmTp,ISIN,TckrSymb,SctySrs,SsnId,OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol".split(",")


def zipped(rows, *, member=MEMBER, extra=False):
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    raw = BytesIO()
    with ZipFile(raw, "w") as archive:
        archive.writestr(member, text.getvalue())
        if extra:
            archive.writestr("extra.csv", text.getvalue())
    return raw.getvalue()


def fixture():
    row = dict(zip(FIELDS, ["2026-09-30", "2026-09-30", "CM", "NSE", "STK",
                          "INECOMPANY", "ABC", "EQ", "F1", "100", "105", "95", "102.25", "1000"]))
    rows = [row, dict(row, TckrSymb="ETF", ISIN="INETRACKER"),
            dict(row, TckrSymb="OTHER", SctySrs="BE", ISIN="INEOTHER")]
    sources = {
        "cash": zipped(rows),
        "company": b"SYMBOL,ISIN NUMBER,SERIES\nABC,INECOMPANY,EQ\n",
        "etf": b"Symbol,ISINNumber\nETF,INETRACKER\n",
        "actions": json.dumps([dict(symbol="ABC", isin="INECOMPANY", exDate="02-Oct-2026", subject="Dividend")]).encode(),
    }
    urls = dict(cash=CM_URL + MEMBER + ".zip", company=EQUITY_URL, etf=ETF_URL,
                actions="https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=30-09-2026&to_date=08-10-2026")
    receipts = {k: dict(url=urls[k], final_url=urls[k], http_status=200,
                       raw_sha256=sha256(v).hexdigest(), bytes=len(v),
                       first_observed_at="2026-10-01T10:00:00Z") for k, v in sources.items()}
    return sources, receipts, rows


def replace_cash(sources, receipts, rows, **kwargs):
    sources["cash"] = zipped(rows, **kwargs)
    receipts["cash"].update(raw_sha256=sha256(sources["cash"]).hexdigest(), bytes=len(sources["cash"]))


def test_packet_keeps_etfs_and_actions_separate_from_forecasts():
    sources, receipts, _ = fixture()
    result = build_packet(sources, receipts, as_of=AS_OF, now=NOW)
    assert result["counts"]["source_rows"] == 3
    assert result["counts"]["ETF_EXCLUDED"] == 1
    assert result["company_eq_observation_count"] == 1
    stock = result["observations"][0]
    assert stock["close"] == "102.25" and stock["volume"] == 1000
    assert stock["action_review"]["action_count"] == 1
    assert stock["action_review"]["adjusted_return_proven"] is False
    assert result["adjusted_prices_proven"] is False
    assert result["exchange_publication_time"] is None
    assert result["qualified_candidates"] == result["forward_predictions"] == result["forward_outcomes"] == 0
    assert result["orders_allowed"] is False


@pytest.mark.parametrize("key", ["cash", "company", "etf", "actions"])
def test_every_source_hash_and_availability_must_bind_before_cutoff(key):
    sources, receipts, _ = fixture()
    wrong = deepcopy(receipts)
    wrong[key]["raw_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="mismatch"):
        build_packet(sources, wrong, as_of=AS_OF, now=NOW)
    receipts[key]["first_observed_at"] = "2026-10-01T11:00:00Z"
    with pytest.raises(ValueError, match="after packet cutoff"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


@pytest.mark.parametrize("field,value", [("TradDt", "2026-09-29"), ("BizDt", "2026-09-29"), ("Sgmt", "FO"), ("Src", "BSE")])
def test_rejects_date_and_source_mismatch_even_for_excluded_rows(field, value):
    sources, receipts, rows = fixture()
    rows[-1][field] = value
    replace_cash(sources, receipts, rows)
    with pytest.raises(ValueError, match="date/source/segment"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


@pytest.mark.parametrize("field,value", [("ClsPric", "NaN"), ("ClsPric", "Infinity"), ("LwPric", "-1"), ("ClsPric", "106"), ("TtlTradgVol", "1.5")])
def test_rejects_invalid_prices_and_fractional_volume(field, value):
    sources, receipts, rows = fixture()
    rows[0][field] = value
    replace_cash(sources, receipts, rows)
    with pytest.raises(ValueError):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


def test_duplicate_identity_cannot_inflate_sample():
    sources, receipts, rows = fixture()
    rows.append(rows[0])
    replace_cash(sources, receipts, rows)
    with pytest.raises(ValueError, match="duplicate cash identity"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


@pytest.mark.parametrize("kwargs", [{"member": "wrong.csv"}, {"extra": True}])
def test_unexpected_zip_members_are_rejected(kwargs):
    sources, receipts, rows = fixture()
    replace_cash(sources, receipts, rows, **kwargs)
    with pytest.raises(ValueError, match="archive member"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


def test_unverified_redirect_and_lookalike_host_rejected():
    sources, receipts, _ = fixture()
    receipts["cash"]["final_url"] += "?changed=true"
    with pytest.raises(ValueError, match="mismatch"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)
    fake = receipts["cash"]["url"].replace("nseindia.com", "nseindia.com.example.org")
    receipts["cash"].update(url=fake, final_url=fake)
    with pytest.raises(ValueError, match="archive URL"):
        build_packet(sources, receipts, as_of=AS_OF, now=NOW)


def test_unknown_or_stale_identity_never_becomes_company_evidence():
    sources, receipts, rows = fixture()
    rows[0]["ISIN"] = "UNKNOWN"
    replace_cash(sources, receipts, rows)
    assert build_packet(sources, receipts, as_of=AS_OF, now=NOW)["company_eq_observation_count"] == 0
    later = "2026-10-02T11:00:00Z"
    result = build_packet(sources, receipts, as_of=later, now=datetime(2026, 10, 3, tzinfo=timezone.utc))
    assert result["company_eq_observation_count"] == 0
    assert result["counts"]["NOT_PROVEN_REFRESH_REQUIRED"] == 2


def test_no_future_packet_or_naive_timestamp():
    sources, receipts, _ = fixture()
    with pytest.raises(ValueError, match="future"):
        build_packet(sources, receipts, as_of="2026-10-01T13:00:00Z", now=NOW)
    with pytest.raises(ValueError, match="timezone"):
        build_packet(sources, receipts, as_of="2026-10-01T10:01:00", now=NOW)
