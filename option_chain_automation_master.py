"""
Option Chain Automation Master — DISABLED (Dhan / DhanHQ path).

System3 is Dhan-only. The full implementation (2254 lines) used DhanBroker
for live option-chain data fetching and is not operational in this configuration.

The original file has been preserved in:
    archive/legacy_dhan/ (via git history)

Any attempt to instantiate OptionChainAutomationMaster raises RuntimeError.
"""

_DISABLED_REASON = (
    "OptionChainAutomationMaster is disabled. System3 is Dhan-only. "
    "The Dhan / DhanHQ option-chain automation path is not active."
)


def _raise_disabled(*_args, **_kwargs):
    raise RuntimeError(_DISABLED_REASON)


class OptionChainAutomationMaster:
    """Disabled Dhan automation master — kept for backward-compatible imports."""

    def __init__(self, *_args, **_kwargs):
        _raise_disabled()


# Legacy top-level entry points fail closed.
run = start = main = _raise_disabled
