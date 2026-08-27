"""Generic three-state circuit breaker (CLOSED / OPEN / HALF_OPEN).

CLOSED: calls flow normally; failures are counted in a rolling window.
OPEN: calls are rejected immediately until `reset_timeout_s` has elapsed.
HALF_OPEN: one trial call is allowed through; success closes the breaker,
failure re-opens it.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(RuntimeError):
    """Raised by `guard()` when the circuit is OPEN and not yet eligible to trial."""


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    reset_timeout_s: float = 30.0
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _consecutive_failures: int = field(default=0, init=False)
    _opened_at: float | None = field(default=None, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state is CircuitState.OPEN and self._opened_at is not None:
            if time.monotonic() - self._opened_at >= self.reset_timeout_s:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def guard(self) -> None:
        """Raise CircuitOpenError if a call should not proceed right now."""
        if self.state is CircuitState.OPEN:
            raise CircuitOpenError(
                f"circuit open; retry after {self.reset_timeout_s:.1f}s reset window"
            )

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self.state is CircuitState.HALF_OPEN or self._consecutive_failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
