"""Historical research must use dated exchange contract terms and stay fail closed."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_archive_session_does_not_scrape_nse_website(monkeypatch):
    downloader = _module("bhavcopy_downloader_history_test", "bhavcopy_downloader.py")
    monkeypatch.setattr(downloader.requests.Session, "get", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("website request")))
    session = downloader._get_session()
    assert session.headers["Accept"] == "application/zip"
    assert "Referer" not in session.headers


def test_udiff_lot_size_and_close_price_research_never_certify_execution(tmp_path, monkeypatch):
    costed = _module("costed_history_test", "costed_walkforward_proof.py")
    pf = _module("pf_history_test", "pf_gated_backtest.py")
    data = tmp_path / "bhavcopy"
    reports = tmp_path / "reports"
    data.mkdir()
    reports.mkdir()
    header = "TckrSymb,OptnTp,StrkPric,ClsPric,OpnIntrst,ChngInOpnIntrst,XpryDt,UndrlygPric,NewBrdLotQty\n"
    for day, price in (("20261111", 20), ("20261112", 25)):
        (data / f"{day}_fo_bhavcopy.csv").write_text(
            header + f"NIFTY,CE,25300,{price},1000,100,2026-11-17,25299.35,65\n",
            encoding="utf-8",
        )
    rows = costed.load_bhavcopy(data / "20261111_fo_bhavcopy.csv")
    assert rows[0]["lot_size"] == 65
    assert pf.load_bhavcopy(data / "20261111_fo_bhavcopy.csv")[0]["lot_size"] == 65
    monkeypatch.setattr(pf, "BHAVCOPY_DIR", data)
    monkeypatch.setattr(pf, "OUT", reports)
    result = pf.run()
    assert result["trades"][0]["lot_size"] == 65
    assert result["trades"][0]["gross_pnl"] == 325
    assert result["estimated_profitability_screen_pass"] is False
    assert result["profit_factor"] is None
    assert result["backtest_pass"] is False
    assert result["pass"] is False
