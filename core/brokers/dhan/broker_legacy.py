"""Legacy Dhan broker module disabled.

System3 is Dhan-only. This compatibility shim prevents import-time crashes from
missing DhanHQ/pyotp packages while making any attempted Dhan broker use fail
closed with a clear error.
"""

DISABLED_REASON = (
    "Dhan / DhanHQ broker path is disabled. System3 is configured for "
    "Dhan-only analyzer/paper operation. Use core.brokers.dhan modules instead."
)


def _raise_disabled(*_args, **_kwargs):
    raise RuntimeError(DISABLED_REASON)


class DhanBroker:
    """Disabled legacy broker class kept only for backward-compatible imports."""

    def __init__(self, *_args, **_kwargs):
        _raise_disabled()


# Common legacy aliases/functions fail closed if imported by old code.
SmartConnect = None
connect = _raise_disabled
login = _raise_disabled
get_profile = _raise_disabled
get_ltp = _raise_disabled
get_quote = _raise_disabled
place_order = _raise_disabled
modify_order = _raise_disabled
cancel_order = _raise_disabled
