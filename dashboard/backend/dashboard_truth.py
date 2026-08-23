"""Shared dashboard data-truth helpers. No synthetic prices or LIVE enablement."""

from __future__ import annotations


def classify_overview_data_source(*, market_open: bool, broker_connected: bool) -> str:
    """Return an honest source label. Never use a bare `live` tag when the market is closed."""
    if broker_connected and market_open:
        return "broker_connected_market_open"
    if broker_connected:
        return "broker_connected_market_closed"
    if market_open:
        return "broker_disconnected_market_open"
    return "broker_disconnected_market_closed"
