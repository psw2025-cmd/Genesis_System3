import pytest
import requests

BASE = "http://127.0.0.1:8000"

CONTRACTS = [
    ("GET",  "/",                          200),
    ("GET",  "/api/health",                200),
    ("GET",  "/api/state",                 200),
    ("GET",  "/api/broker/status",         200),
    ("GET",  "/openapi.json",              200),
    ("GET",  "/docs",                      200),
    ("GET",  "/ui",                        200),
    ("GET",  "/risk",                      200),
    ("GET",  "/tradebook",                 200),
    ("GET",  "/holdings",                  200),
    ("GET",  "/dhan-health",               200),
    ("POST", "/emergency-exit",            403),
    ("GET",  "/auto-research",             200),
    ("GET",  "/verify-strategy",           200),
    ("GET",  "/learn-from-loss",           200),
    ("GET",  "/adapt-market",              200),
    ("GET",  "/option-intelligence/NIFTY", 200),
    ("GET",  "/autonomous-brain",          200),
    ("GET",  "/hidden-secrets-lab",        200),
    ("GET",  "/never-die-monitor",         200),
    ("GET",  "/hunger-meter",              200),
    ("GET",  "/data-truth-score",          200),
    ("GET",  "/world-comparison",          200),
    ("GET",  "/roadmap",                   200),
    ("GET",  "/cost-roi",                  200),
]

@pytest.mark.parametrize("method,path,expected", CONTRACTS)
def test_contract(method: str, path: str, expected: int) -> None:
    url = BASE + path
    if method == "POST":
        r = requests.post(url, json={"dry_run": True}, timeout=10)
    else:
        r = requests.get(url, timeout=10)
    assert r.status_code == expected, f"Expected {expected}, got {r.status_code} for {method} {path}"

def test_emergency_exit_guard() -> None:
    r = requests.post(BASE + "/emergency-exit", json={"dry_run": True}, timeout=10)
    assert r.status_code == 403
    assert r.json().get("code") == "PUBLIC_DASHBOARD_READ_ONLY"
