"""
Option Chain Automation Master — DISABLED (Angel One / SmartAPI path).

System3 is Dhan-only. The full implementation (2254 lines) used AngelOneBroker
for live option-chain data fetching and is not operational in this configuration.

The original file has been preserved in:
    archive/legacy_angel_one/ (via git history)

Any attempt to instantiate OptionChainAutomationMaster raises RuntimeError.
"""

_DISABLED_REASON = (
    "OptionChainAutomationMaster is disabled. System3 is Dhan-only. "
    "The Angel One / SmartAPI option-chain automation path is not active."
)


def _raise_disabled(*_args, **_kwargs):
    raise RuntimeError(_DISABLED_REASON)


class OptionChainAutomationMaster:
    """Disabled Angel One automation master — kept for backward-compatible imports."""

    def __init__(self, *_args, **_kwargs):
        _raise_disabled()


# Legacy top-level entry points fail closed.
run = start = main = _raise_disabled
