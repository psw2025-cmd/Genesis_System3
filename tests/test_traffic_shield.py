import asyncio
import time

from fastapi import Request
from fastapi.responses import JSONResponse

from dashboard.backend import traffic_shield as shield


def _request(method="GET", path="/api/batch/positions-holdings", query=b""):
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "scheme": "https",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query,
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 443),
        }
    )


def _reset():
    shield._cache.clear()
    shield._locks.clear()
    shield._stats.clear()


def test_identical_expensive_gets_are_single_flight():
    _reset()

    async def scenario():
        calls = 0

        async def producer(_request):
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.05)
            return JSONResponse({"status": "ok", "calls": calls})

        responses = await asyncio.gather(
            *[
                shield.traffic_shield_middleware(
                    _request(query=f"_ts={index}".encode()),
                    producer,
                )
                for index in range(12)
            ]
        )
        assert calls == 1
        assert all(response.status_code == 200 for response in responses)
        assert shield.traffic_shield_status()["stats"]["coalesced_waiters"] >= 1

    asyncio.run(scenario())


def test_transient_failure_serves_recent_successful_stale_snapshot():
    _reset()

    async def scenario():
        async def good(_request):
            return JSONResponse({"status": "ok", "value": 7})

        first = await shield.traffic_shield_middleware(_request(), good)
        assert first.status_code == 200
        key = "/api/batch/positions-holdings"
        shield._cache[key].stored_at = time.monotonic() - (shield._FRESH_TTL + 0.5)

        async def failing(_request):
            return JSONResponse({"status": "error"}, status_code=503)

        second = await shield.traffic_shield_middleware(_request(), failing)
        assert second.status_code == 200
        assert second.headers["x-system3-traffic-shield"].startswith("stale-upstream")
        assert shield.traffic_shield_status()["stats"]["stale_transient_served"] == 1

    asyncio.run(scenario())


def test_mutation_requests_are_never_cached_coalesced_or_retried():
    _reset()

    async def scenario():
        calls = 0

        async def mutation(_request):
            nonlocal calls
            calls += 1
            return JSONResponse({"status": "blocked"}, status_code=403)

        for _ in range(3):
            response = await shield.traffic_shield_middleware(
                _request(method="POST", path="/api/broker/orders"),
                mutation,
            )
            assert response.status_code == 403
        assert calls == 3
        assert shield.traffic_shield_status()["stats"] == {}

    asyncio.run(scenario())


def test_cache_buster_does_not_create_new_singleflight_lane():
    assert shield._key(_request(query=b"_ts=1&symbol=NIFTY")) == shield._key(
        _request(query=b"symbol=NIFTY&_ts=999999")
    )
