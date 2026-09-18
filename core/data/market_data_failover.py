from __future__ import annotations

"""Read-only market-data failover primitives for Genesis System3.

This module contains no order endpoints and no broker credentials. It provides a
small, testable routing layer that can be fed by existing read-only providers
(Dhan websocket, Dhan REST market quote, Dhan option-chain, Dhan historical,
secondary broker adapters, exchange validation feeds, or last-known-good cache).

Production invariants:
- broker-backed data is required by default;
- synthetic/demo providers are never accepted in production;
- stale cache is explicit, never silently reported as live;
- every result carries provider/fallback/freshness truth;
- circuit breakers stop repeatedly hammering a failing provider.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import os
import time
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence


class ProviderTier(str, Enum):
    PRIMARY_BROKER = "primary_broker"
    SECONDARY_BROKER = "secondary_broker"
    EXCHANGE_VALIDATION = "exchange_validation"
    LAST_KNOWN_GOOD = "last_known_good"
    TEST_ONLY = "test_only"


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    tier: ProviderTier
    fetch: Callable[[Mapping[str, Any]], Any]
    broker_backed: bool
    priority: int = 100
    supports: frozenset[str] = field(default_factory=frozenset)
    timeout_s: float = 3.0


@dataclass
class ProviderHealth:
    consecutive_failures: int = 0
    circuit_open_until: float = 0.0
    last_error: str = ""
    last_success_at: float = 0.0

    def available(self, now: Optional[float] = None) -> bool:
        now = time.monotonic() if now is None else now
        return now >= self.circuit_open_until


@dataclass(frozen=True)
class MarketDataResult:
    ok: bool
    data: Any
    provider: str
    tier: ProviderTier
    broker_backed: bool
    authoritative: bool
    degraded: bool
    stale: bool
    observed_at: str
    latency_ms: float
    fallback_index: int
    reason: str = ""
    attempts: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "provider": self.provider,
            "tier": self.tier.value,
            "broker_backed": self.broker_backed,
            "authoritative": self.authoritative,
            "degraded": self.degraded,
            "stale": self.stale,
            "observed_at": self.observed_at,
            "latency_ms": self.latency_ms,
            "fallback_index": self.fallback_index,
            "reason": self.reason,
            "attempts": list(self.attempts),
        }


class MarketDataUnavailable(RuntimeError):
    pass


class MarketDataFailoverRouter:
    """Sequential, truth-preserving read-only provider failover.

    Providers are ordered by ``priority``. A provider failure increments a
    circuit-breaker counter; after ``failure_threshold`` failures the provider is
    skipped for ``circuit_open_s`` seconds.

    ``require_broker=True`` is the production default. Exchange-only sources may
    still be registered for cross-validation but will not be selected to drive
    the UI unless the caller explicitly opts into non-broker degraded data.
    """

    def __init__(
        self,
        providers: Iterable[ProviderSpec],
        *,
        failure_threshold: int = 2,
        circuit_open_s: float = 15.0,
        production: Optional[bool] = None,
    ) -> None:
        self.providers: List[ProviderSpec] = sorted(providers, key=lambda p: (p.priority, p.name))
        self.failure_threshold = max(1, int(failure_threshold))
        self.circuit_open_s = max(0.1, float(circuit_open_s))
        if production is None:
            production = bool(
                os.getenv("K_SERVICE")
                or os.getenv("CLOUD_MODE")
                or os.getenv("SYSTEM3_DEPLOY_TARGET") == "gcp-cloud-run"
            )
        self.production = bool(production)
        self.health: Dict[str, ProviderHealth] = {p.name: ProviderHealth() for p in self.providers}

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    @staticmethod
    def _usable_payload(payload: Any) -> bool:
        if payload is None:
            return False
        if isinstance(payload, Mapping):
            if payload.get("ok") is False or payload.get("success") is False:
                return False
            if "data" in payload and payload.get("data") in (None, {}, []):
                return False
            return bool(payload)
        if isinstance(payload, (list, tuple, set, str, bytes)):
            return len(payload) > 0
        return True

    @staticmethod
    def _payload_stale(payload: Any) -> bool:
        if isinstance(payload, Mapping):
            return bool(payload.get("stale") or payload.get("is_stale"))
        return False

    @staticmethod
    def _payload_reason(payload: Any) -> str:
        if isinstance(payload, Mapping):
            return str(payload.get("reason") or payload.get("error") or payload.get("stale_reason") or "")[:240]
        return ""

    def provider_health(self) -> Dict[str, Dict[str, Any]]:
        now = time.monotonic()
        return {
            name: {
                "consecutive_failures": h.consecutive_failures,
                "circuit_open": not h.available(now),
                "last_error": h.last_error,
                "last_success_at_monotonic": h.last_success_at,
            }
            for name, h in self.health.items()
        }

    def fetch(
        self,
        kind: str,
        request: Mapping[str, Any],
        *,
        require_broker: bool = True,
        allow_stale: bool = True,
    ) -> MarketDataResult:
        attempts: List[dict[str, Any]] = []
        eligible = [p for p in self.providers if not p.supports or kind in p.supports]
        if not eligible:
            raise MarketDataUnavailable(f"no providers registered for kind={kind}")

        for fallback_index, provider in enumerate(eligible):
            health = self.health[provider.name]

            if self.production and provider.tier is ProviderTier.TEST_ONLY:
                attempts.append({"provider": provider.name, "status": "blocked_test_only"})
                continue
            if require_broker and not provider.broker_backed:
                attempts.append({"provider": provider.name, "status": "validation_only_non_broker"})
                continue
            if not health.available():
                attempts.append({"provider": provider.name, "status": "circuit_open"})
                continue

            started = time.perf_counter()
            try:
                payload = provider.fetch(request)
                latency_ms = (time.perf_counter() - started) * 1000.0
                if not self._usable_payload(payload):
                    raise MarketDataUnavailable(self._payload_reason(payload) or "empty_or_unsuccessful_payload")

                stale = self._payload_stale(payload) or provider.tier is ProviderTier.LAST_KNOWN_GOOD
                if stale and not allow_stale:
                    raise MarketDataUnavailable("stale_payload_rejected")

                health.consecutive_failures = 0
                health.circuit_open_until = 0.0
                health.last_error = ""
                health.last_success_at = time.monotonic()
                attempts.append({
                    "provider": provider.name,
                    "status": "success",
                    "latency_ms": round(latency_ms, 3),
                    "stale": stale,
                })
                authoritative = provider.tier is ProviderTier.PRIMARY_BROKER and not stale
                degraded = fallback_index > 0 or not authoritative or stale
                return MarketDataResult(
                    ok=True,
                    data=payload,
                    provider=provider.name,
                    tier=provider.tier,
                    broker_backed=provider.broker_backed,
                    authoritative=authoritative,
                    degraded=degraded,
                    stale=stale,
                    observed_at=self._now_iso(),
                    latency_ms=round(latency_ms, 3),
                    fallback_index=fallback_index,
                    reason=self._payload_reason(payload),
                    attempts=tuple(attempts),
                )
            except Exception as exc:
                latency_ms = (time.perf_counter() - started) * 1000.0
                health.consecutive_failures += 1
                health.last_error = f"{type(exc).__name__}: {exc}"[:240]
                if health.consecutive_failures >= self.failure_threshold:
                    health.circuit_open_until = time.monotonic() + self.circuit_open_s
                attempts.append({
                    "provider": provider.name,
                    "status": "failed",
                    "latency_ms": round(latency_ms, 3),
                    "error": health.last_error,
                })

        raise MarketDataUnavailable(
            f"all eligible providers failed for kind={kind}; attempts={attempts}"
        )


def recommended_provider_order() -> Sequence[dict[str, Any]]:
    """Document the production routing contract without importing broker SDKs.

    Adapters are registered elsewhere so credentials remain in Secret Manager and
    this module stays safe to unit-test.
    """
    return (
        {
            "name": "dhan_ws",
            "tier": ProviderTier.PRIMARY_BROKER.value,
            "use": "live ticks/quotes; primary during market session",
        },
        {
            "name": "dhan_rest_quote",
            "tier": ProviderTier.PRIMARY_BROKER.value,
            "use": "snapshot failover/resync for websocket gaps",
        },
        {
            "name": "dhan_option_chain",
            "tier": ProviderTier.PRIMARY_BROKER.value,
            "use": "full option-chain/expiries/greeks/OI/bid-ask",
        },
        {
            "name": "dhan_historical",
            "tier": ProviderTier.PRIMARY_BROKER.value,
            "use": "chart candle backfill and continuity repair",
        },
        {
            "name": "secondary_broker_optional",
            "tier": ProviderTier.SECONDARY_BROKER.value,
            "use": "optional read-only continuity only when separately credentialed/licensed",
        },
        {
            "name": "dhan_last_known_good",
            "tier": ProviderTier.LAST_KNOWN_GOOD.value,
            "use": "explicit stale/degraded continuity; never labelled live",
        },
        {
            "name": "nse_bse_validation",
            "tier": ProviderTier.EXCHANGE_VALIDATION.value,
            "use": "cross-validation/coverage truth; not selected when require_broker=True",
        },
    )
