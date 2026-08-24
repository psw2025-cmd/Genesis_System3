"""Dhan BANKEX option-chain underlying contract."""

from unittest.mock import patch

from core.data.datasource_manager import DataSourceManager


def test_bankex_resolves_to_official_dhan_index_underlying():
    manager = DataSourceManager()

    assert manager._resolve_underlying("BANKEX") == (12, "IDX_I")


def test_bankex_uses_nearest_non_expired_master_expiry_when_api_list_is_empty(tmp_path):
    master = tmp_path / "security_id_list.csv"
    master.write_text(
        "SEM_INSTRUMENT_NAME,SM_SYMBOL_NAME,SEM_TRADING_SYMBOL,SEM_EXPIRY_DATE\n"
        "OPTIDX,BKXOPT,BANKEX-Jan2000-60000-CE,2000-01-27\n"
        "OPTIDX,BKXOPT,BANKEX-Jan2099-60000-CE,2099-01-29\n",
        encoding="utf-8",
    )
    manager = DataSourceManager()

    with patch("core.data.datasource_manager.ROOT", tmp_path):
        assert manager._nearest_master_expiry("BANKEX") == "2099-01-29"
