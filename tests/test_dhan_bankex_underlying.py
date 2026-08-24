"""Dhan BANKEX option-chain underlying contract."""

from core.data.datasource_manager import DataSourceManager


def test_bankex_resolves_to_official_dhan_index_underlying():
    manager = DataSourceManager()

    assert manager._resolve_underlying("BANKEX") == (12, "IDX_I")
