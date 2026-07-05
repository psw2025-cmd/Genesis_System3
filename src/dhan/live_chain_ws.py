"""
Dhan DhanHQ WebSocket — DISABLED.

System3 is Dhan-only. The DhanHQ WebSocket data path is not operational.
Kept as a compatibility shim so that callers which guard their import with
try/except do not crash at import time.

Any attempt to instantiate LiveChainWebSocket raises RuntimeError.
"""

DISABLED_REASON = (
    "Dhan DhanHQ WebSocket path is disabled. "
    "System3 is configured for Dhan-only analyzer/paper operation. "
    "Use the Dhan data feed in core/brokers/dhan/ instead."
)

# Sentinel — SmartApi is not installed and must not be imported
SmartWebSocketV2 = None


def _raise_disabled(*_args, **_kwargs):
    raise RuntimeError(DISABLED_REASON)


class LiveChainWebSocket:
    """
    Disabled Dhan WebSocket shim.

    Preserved for backward-compatible imports only.
    Raises RuntimeError on any instantiation attempt.
    """

    EXCHANGE_MAP = {}
    MODE_SNAP_QUOTE = 3

    def __init__(self, *_args, **_kwargs):
        _raise_disabled()

    connect = _raise_disabled
    subscribe = _raise_disabled
    disconnect = _raise_disabled
    reconnect = _raise_disabled

    def is_alive(self, *_args, **_kwargs) -> bool:  # noqa: D401
        return False
