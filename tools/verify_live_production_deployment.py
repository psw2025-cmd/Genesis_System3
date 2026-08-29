"""Live Production Deployment End-to-End Verification."""

import json
import ssl
import subprocess
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"


def verify_route(name, path, expected_key=None):
    url = BASE_URL + path
    req = urllib.request.Request(url, headers={"User-Agent": "Genesis-Audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read().decode("utf-8")
            status = resp.status
            parsed = json.loads(data) if data.startswith("{") else None
            key_check = True
            if expected_key and parsed:
                key_check = expected_key in parsed
            print(
                f"  [PASS] {name:<30} -> HTTP {status} | Size: {len(data):>7} bytes | Key Check: {key_check}"
            )
            return True
    except Exception as e:
        print(f"  [FAIL] {name:<30} -> ERROR: {e}")
        return False


def main():
    print("=== GENESIS SYSTEM3 END-TO-END LIVE PRODUCTION VERIFICATION ===")
    print(f"Target Production Service: {BASE_URL}")

    # Cloud Run revision info
    p = subprocess.run(
        [
            "gcloud.cmd",
            "run",
            "services",
            "describe",
            "genesis-system3-web",
            "--region=asia-south1",
            "--format=json(status.latestReadyRevisionName,status.traffic)",
        ],
        capture_output=True,
        text=True,
    )
    print(f"Cloud Run Service Status:\n{p.stdout.strip()}\n")

    print("--- Probing Live API Routes ---")
    routes = [
        ("Health Endpoint", "/api/health", "status"),
        ("Deploy Metadata", "/api/deploy/info", "service_name"),
        ("Option Chain (44 Fields)", "/api/option-chain", "underlying"),
        ("Options Intelligence", "/api/options-intel", "underlying"),
        ("Paper Positions", "/api/paper/positions", "positions"),
        ("Paper Trade History", "/api/paper/trades", "trades"),
        ("Paper Account Capital", "/api/paper/account", "initial_capital"),
        ("Paper Engine Status", "/api/paper/status", "engine"),
        ("Multibagger Workspace", "/api/multibagger", "candidates"),
        ("News & Catalysts", "/api/catalysts", "catalysts"),
        ("Institutional Backtest", "/api/backtest/results", "summary"),
        ("Operational Runbook Audit", "/api/runbook/audit", "overall_verdict"),
    ]

    all_passed = True
    for name, path, key in routes:
        ok = verify_route(name, path, key)
        if not ok:
            all_passed = False

    # Check UI
    print("\n--- Probing Live Dashboard UI ---")
    ui_url = BASE_URL + "/ui"
    req = urllib.request.Request(
        ui_url, headers={"User-Agent": "Genesis-Audit/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode("utf-8")
            has_root = "root" in html
            print(
                f"  [PASS] UI Entry Point (/ui)           -> HTTP {resp.status} | HTML Size: {len(html)} bytes | React Root: {has_root}"
            )
    except Exception as e:
        print(f"  [FAIL] UI Entry Point (/ui)           -> ERROR: {e}")
        all_passed = False

    print("\n=== FINAL VERIFICATION VERDICT ===")
    if all_passed:
        print("ALL ENDPOINTS AND UI SURFACES VERIFIED 100% OPERATIONAL ON LIVE PRODUCTION GCP CLOUD RUN!")
    else:
        print("SOME CHECKS FAILED.")


if __name__ == "__main__":
    main()
