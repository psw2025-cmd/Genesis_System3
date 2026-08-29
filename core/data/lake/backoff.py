"""Exponential backoff with full jitter, plus Retry-After awareness.

Reference: AWS Architecture Blog, "Exponential Backoff And Jitter" (full jitter
variant) - sleep = random(0, min(cap, base * 2**attempt)).
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BackoffPolicy:
    base_seconds: float = 0.5
    cap_seconds: float = 30.0
    max_attempts: int | None = 8  # None = unlimited

    def delay_seconds(self, attempt: int, retry_after: float | None = None) -> float:
        """Delay before the given attempt (0-indexed). Honors a server Retry-After
        hint by using it as a floor, since the server's stated wait always wins."""
        if attempt < 0:
            raise ValueError("attempt must be >= 0")
        exp_delay = min(self.cap_seconds, self.base_seconds * (2**attempt))
        jittered = random.uniform(0, exp_delay)
        if retry_after is not None and retry_after > 0:
            return max(jittered, float(retry_after))
        return jittered

    def exhausted(self, attempt: int) -> bool:
        return self.max_attempts is not None and attempt >= self.max_attempts
