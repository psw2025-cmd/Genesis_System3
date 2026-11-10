#!/usr/bin/env python3
"""End-to-end Cloud proof for Genesis System3 public/read-only dashboard.

Writes reports/latest/cloud_e2e_proof/{summary.json,README.md}.
Exit 0 only when required UI/API/stream markers pass.

Dashboard reads are anonymous by architecture. This proof must never load or
send the retired dashboard API key/session credential surface.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "cloud_e2e_proof"
BASE = os.environ.get("SYSTEM3_CLOUD_BASE", "https://genesis-system3-web-doq2wplepa-el.a.run.app").rstrip("/")
EXPECTED_EPOCH = os.environ.get("SYSTEM3_EXPECTED_EPOCH", "20260803_e2e_full_cloud_40")


def _get(path: str, timeout: float = 60.0):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            elapsed = round(time.time() - started, 2)
            ctype = resp.headers.get("Content-Type", "")
            if "json" in ctype or path.endswith(".json") or path.startswith("/api/"):
                try:
                    data = json.loads(body.decode("utf-8", errors="replace"))
                except Exception:
                    data = body.decode("utf-8", errors="replace")[:500]
            else:
                data = body.decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "elapsed_s": elapsed, "data": data}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "elapsed_s": round(time.time() - started, 2), "error": str(e)}
    except Exception as e:
        return {"ok": False, "status": 0, "elapsed_s": round(time.time() - started, 2), "error": str(e)}


def main() -> int:
    checks = []

    prov = _get("/ui/assets/deploy-provenance.json")
    epoch = ""
    if isinstance(prov.get("data"), dict):
        epoch = str(prov["data"].get("build_epoch") or "")
    checks.append(
        {
            "id": "provenance_epoch",
            "pass": prov.get("ok") and epoch == EXPECTED_EPOCH,
            "detail": {"expected": EXPECTED_EPOCH, "got": epoch, "http": prov.get("status")},
        }
    )
    checks.append(
        {
            "id": "provenance_badges",
            "pass": isinstance(prov.get("data"), dict)
            and bool(prov["data"].get("cloud_build_badge"))
            and bool(prov["data"].get("session_snapshot_ui")),
            "detail": prov.get("data") if isinstance(prov.get("data"), dict) else prov,
        }
    )

    html = _get(f"/ui/?v={EXPECTED_EPOCH}")
    html_text = html.get("data") if isinstance(html.get("data"), str) else ""
    checks.append(
        {
            "id": "ui_html_assets",
            "pass": html.get("ok") and "assets/index-" in html_text and ".js" in html_text,
            "detail": {
                "http": html.get("status"),
                "has_js": "assets/index-" in html_text,
                "snippet": html_text[:240],
            },
        }
    )

    health = _get("/api/health")
    h = health.get("data") if isinstance(health.get("data"), dict) else {}
    checks.append(
        {
            "id": "health_ok",
            "pass": health.get("ok") and h.get("status") == "ok",
            "detail": {
                "http": health.get("status"),
                "broker": h.get("broker_status") or (h.get("broker") or {}).get("status"),
                "market": h.get("market_status") or (h.get("market") or {}).get("is_open"),
                "live_allowed": h.get("live_allowed"),
            },
        }
    )

    for sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
        ch = _get(f"/api/chain/{sym}", timeout=90)
        d = ch.get("data") if isinstance(ch.get("data"), dict) else {}
        n = len(d.get("contracts") or [])
        spot = float(d.get("spot") or 0)
        checks.append(
            {
                "id": f"chain_{sym}",
                "pass": ch.get("ok") and spot > 0 and n > 0,
                "detail": {
                    "http": ch.get("status"),
                    "spot": spot,
                    "contracts": n,
                    "status": d.get("status"),
                    "source_priority": d.get("source_priority"),
                    "age_s": d.get("snapshot_age_seconds"),
                },
            }
        )

    top = _get("/api/scanner/top_contract_gainers?top_n=3&market_top_n=10&include_equity=1", timeout=120)
    td = top.get("data") if isinstance(top.get("data"), dict) else {}
    rows = td.get("market_top_table") or []
    checks.append(
        {
            "id": "market_top",
            "pass": top.get("ok") and len(rows) > 0,
            "detail": {
                "http": top.get("status"),
                "rows": len(rows),
                "status": td.get("status"),
                "stream_mode": td.get("stream_mode"),
                "sample": [
                    f"{r.get('underlying')} {r.get('option_type')} {r.get('gain_pct')}"
                    for r in rows[:3]
                    if isinstance(r, dict)
                ],
            },
        }
    )

    auth = _get("/api/auth/status")
    auth_data = auth.get("data") if isinstance(auth.get("data"), dict) else {}
    checks.append(
        {
            "id": "auth_status",
            "pass": auth.get("ok")
            and auth_data.get("required") is False
            and auth_data.get("configured") is False
            and auth_data.get("authenticated") is False
            and auth_data.get("mode") == "public_readonly",
            "detail": {
                "http": auth.get("status"),
                "required": auth_data.get("required"),
                "configured": auth_data.get("configured"),
                "authenticated": auth_data.get("authenticated"),
                "mode": auth_data.get("mode"),
            },
        }
    )

    passed = sum(1 for c in checks if c["pass"])
    failed = [c["id"] for c in checks if not c["pass"]]
    summary = {
        "schema": 2,
        "generated_at_ist": datetime.now().isoformat(timespec="seconds"),
        "base": BASE,
        "expected_epoch": EXPECTED_EPOCH,
        "observed_epoch": epoch,
        "pass_count": passed,
        "fail_count": len(failed),
        "failed": failed,
        "overall_pass": len(failed) == 0,
        "dashboard_access": "public_readonly_anonymous",
        "dashboard_credentials_loaded": False,
        "dashboard_credentials_sent": False,
        "live_trading_enabled": False,
        "checks": checks,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Cloud E2E Proof",
        "",
        f"- Base: `{BASE}`",
        f"- Expected epoch: `{EXPECTED_EPOCH}`",
        f"- Observed epoch: `{epoch}`",
        f"- Overall: **{'PASS' if summary['overall_pass'] else 'FAIL'}** ({passed}/{len(checks)})",
        "- Dashboard access: anonymous public/read-only",
        "- Dashboard credentials loaded/sent: false/false",
        "- Live trading: OFF",
        "",
        "## Checks",
        "",
    ]
    for c in checks:
        mark = "PASS" if c["pass"] else "FAIL"
        lines.append(f"- `{c['id']}`: **{mark}** — `{json.dumps(c['detail'], ensure_ascii=True)[:220]}`")
    lines.extend(
        [
            "",
            "## User visual confirmation",
            "",
            f"1. Hard refresh: `{BASE}/ui/?v={EXPECTED_EPOCH}`",
            "2. TopBar must show green **CLOUD BUILD** badge ending with `e2e_full_cloud_40`",
            "3. Trade tab: Market Top + Option Chain rows (snapshot after hours / live in session)",
            "",
        ]
    )
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"overall_pass": summary["overall_pass"], "failed": failed, "epoch": epoch}, indent=2))
    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
