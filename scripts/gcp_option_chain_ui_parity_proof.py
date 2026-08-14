#!/usr/bin/env python3
"""Strict production-UI proof for broker option-chain parity.

UI is the final truth gate. This script uses the same real deployed Cloud Run
browser transport as the canonical tab proof and refuses to pass on API-only
truth. Read-only only; it never calls order or mutation endpoints.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from scripts.gcp_ui_tab_visual_proof import ChromeDriverSession, _service_url

EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path("reports/latest/public_dashboard_proof/option_chain_parity")
CORE = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}


def _wait_until(browser: ChromeDriverSession, script: str, args: list[Any], timeout_s: int = 25) -> Any:
    deadline = time.monotonic() + timeout_s
    last: Any = None
    while time.monotonic() < deadline:
        last = browser._request(
            "POST",
            f"/session/{browser.session_id}/execute/sync",
            {"script": script, "args": args},
            timeout=15,
        )
        if isinstance(last, dict) and last.get("ready"):
            return last
        time.sleep(0.5)
    return last


def _snapshot(browser: ChromeDriverSession) -> dict[str, Any]:
    script = r"""
const text = (document.body?.innerText || '');
const upper = text.toUpperCase();
const input = document.querySelector('input[aria-label="Search option underlying"]');
const expiry = document.querySelector('select[aria-label="Option expiry"]');
const strikes = document.querySelector('select[aria-label="Strike visibility"]');
const datalist = document.querySelector('#option-underlying-universe');
const values = datalist ? Array.from(datalist.querySelectorAll('option')).map(o => String(o.value || '').toUpperCase()).filter(Boolean) : [];
function countAfter(label) {
  const m = text.match(new RegExp(label + '\\s+(\\d+)', 'i'));
  return m ? Number(m[1]) : null;
}
function contractCount() { const m = text.match(/CONTRACTS\s+(\d+)/i); return m ? Number(m[1]) : null; }
function strikeCount() { const m = text.match(/STRIKES\s+(\d+)/i); return m ? Number(m[1]) : null; }
return {
  ready: !!input && !!expiry && !!strikes && upper.includes('OPTION CHAIN'),
  body: text.slice(0, 40000),
  universeCount: countAfter('DHAN UNIVERSE'),
  equityOptionCount: countAfter('EQ OPT'),
  expiryCount: countAfter('EXPIRIES'),
  contractCount: contractCount(),
  strikeCount: strikeCount(),
  discoveryDegraded: upper.includes('DISCOVERY DEGRADED'),
  noRows: upper.includes('NO VERIFIED BROKER CHAIN ROWS'),
  chainMismatch: upper.includes('WRONG-SYMBOL ROWS ARE HIDDEN') || upper.includes('WHILE UI SELECTED'),
  allStrikes: Array.from(strikes?.options || []).some(o => /^ALL STRIKES/i.test(String(o.textContent || ''))),
  selectedStrikeMode: strikes?.selectedOptions?.[0]?.textContent || null,
  selectedExpiry: expiry?.value || '',
  expiries: expiry ? Array.from(expiry.options).map(o => String(o.value || '')).filter(Boolean) : [],
  universeValues: values,
  sourceDhan: /source=dhan\b/i.test(text) || /priority=dhan_option_chain_live/i.test(text),
  completeChain: /complete_chain=true/i.test(text),
  liveOff: /LIVE\s+OFF/i.test(text) || /ANALYZER\s*\/\s*PAPER/i.test(text),
};
"""
    value = browser._request(
        "POST",
        f"/session/{browser.session_id}/execute/sync",
        {"script": script, "args": []},
        timeout=15,
    )
    return value if isinstance(value, dict) else {}


def _select_symbol(browser: ChromeDriverSession, symbol: str) -> None:
    script = r"""
const symbol = arguments[0];
const input = document.querySelector('input[aria-label="Search option underlying"]');
if (!input || !input.form) return false;
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
setter.call(input, symbol);
input.dispatchEvent(new Event('input', {bubbles:true}));
input.dispatchEvent(new Event('change', {bubbles:true}));
if (input.form.requestSubmit) input.form.requestSubmit(); else input.form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
return true;
"""
    ok = browser._request("POST", f"/session/{browser.session_id}/execute/sync", {"script": script, "args": [symbol]}, timeout=15)
    if ok is not True:
        raise RuntimeError("ui_symbol_select_failed")


def _select_expiry(browser: ChromeDriverSession, expiry: str) -> None:
    script = r"""
const value = arguments[0];
const select = document.querySelector('select[aria-label="Option expiry"]');
if (!select || !Array.from(select.options).some(o => o.value === value)) return false;
const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set;
setter.call(select, value);
select.dispatchEvent(new Event('change', {bubbles:true}));
return true;
"""
    ok = browser._request("POST", f"/session/{browser.session_id}/execute/sync", {"script": script, "args": [expiry]}, timeout=15)
    if ok is not True:
        raise RuntimeError("ui_expiry_select_failed")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "state": "FAIL",
        "source": "actual_deployed_production_ui",
        "expected_sha": EXPECTED_SHA,
        "mutations_called": False,
        "checks": {},
        "failures": [],
    }
    try:
        if len(EXPECTED_SHA) != 40:
            raise RuntimeError("expected_git_sha_missing")
        dashboard_url = f"{_service_url()}/ui?tab=chain"
        with ChromeDriverSession(page_load_timeout_s=60) as browser:
            browser.set_viewport(1600, 1000)
            browser.navigate(dashboard_url)
            baseline = _wait_until(browser, "return {ready: !!document.querySelector('input[aria-label=\"Search option underlying\"]') && !!document.querySelector('select[aria-label=\"Option expiry\"]')};", [], 25)
            if not isinstance(baseline, dict) or not baseline.get("ready"):
                raise RuntimeError("option_chain_controls_not_rendered")
            time.sleep(2)
            baseline = _snapshot(browser)
            baseline_hash = browser.screenshot(OUT / "01-option-chain-baseline.png")

            universe = [str(x).upper() for x in (baseline.get("universeValues") or []) if x]
            equity_candidates = [s for s in universe if s not in CORE]
            sample = "RELIANCE" if "RELIANCE" in equity_candidates else (equity_candidates[0] if equity_candidates else "")

            checks = {
                "controls_rendered": bool(baseline.get("ready")),
                "broker_universe_visible": isinstance(baseline.get("universeCount"), (int, float)) and int(baseline["universeCount"]) > len(CORE),
                "equity_option_count_visible": isinstance(baseline.get("equityOptionCount"), (int, float)) and int(baseline["equityOptionCount"]) > 0,
                "broker_universe_datalist": len(universe) > len(CORE),
                "equity_sample_discoverable": bool(sample),
                "not_discovery_degraded": not bool(baseline.get("discoveryDegraded")),
                "all_strikes_control_visible": bool(baseline.get("allStrikes")),
                "all_strikes_default": str(baseline.get("selectedStrikeMode") or "").upper().startswith("ALL STRIKES"),
                "safety_visible": bool(baseline.get("liveOff")),
            }

            equity_snapshot: dict[str, Any] = {}
            if sample:
                _select_symbol(browser, sample)
                equity_snapshot = _wait_until(
                    browser,
                    r"""const s=arguments[0]; const t=(document.body?.innerText||'').toUpperCase(); const e=document.querySelector('select[aria-label="Option expiry"]'); return {ready:t.includes('SYMBOL '+s) && !!e, body:t.slice(0,40000), expiries:e?Array.from(e.options).map(o=>o.value).filter(Boolean):[]};""",
                    [sample], 30,
                ) or {}
                time.sleep(1)
                equity_snapshot = _snapshot(browser)
                browser.screenshot(OUT / "02-equity-underlying.png")
                checks["equity_symbol_selected_in_ui"] = sample in str(equity_snapshot.get("body") or "").upper()
                checks["equity_expiries_visible"] = int(equity_snapshot.get("expiryCount") or 0) > 0 and len(equity_snapshot.get("expiries") or []) > 0
                expiries = list(equity_snapshot.get("expiries") or [])
                if expiries:
                    selected = str(expiries[0])
                    _select_expiry(browser, selected)
                    expiry_snapshot = _wait_until(
                        browser,
                        r"""const e=arguments[0]; const t=(document.body?.innerText||''); const c=(t.match(/CONTRACTS\s+(\d+)/i)||[])[1]; const s=(t.match(/STRIKES\s+(\d+)/i)||[])[1]; return {ready:t.includes('selected_expiry='+e) && Number(c||0)>0 && Number(s||0)>0, body:t.slice(0,40000)};""",
                        [selected], 35,
                    ) or {}
                    time.sleep(1)
                    expiry_snapshot = _snapshot(browser)
                    expiry_hash = browser.screenshot(OUT / "03-equity-expiry-full-chain.png")
                    result["selected_expiry"] = selected
                    result["expiry_snapshot"] = {k: v for k, v in expiry_snapshot.items() if k not in {"body", "universeValues"}}
                    result["expiry_screenshot_sha256"] = expiry_hash
                    checks["explicit_expiry_selected_in_ui"] = expiry_snapshot.get("selectedExpiry") == selected
                    checks["broker_rows_visible_for_expiry"] = int(expiry_snapshot.get("contractCount") or 0) > 0 and int(expiry_snapshot.get("strikeCount") or 0) > 0 and not bool(expiry_snapshot.get("noRows"))
                    checks["full_chain_truth_visible"] = bool(expiry_snapshot.get("completeChain"))
                    checks["dhan_source_visible"] = bool(expiry_snapshot.get("sourceDhan"))
                    checks["no_symbol_mismatch"] = not bool(expiry_snapshot.get("chainMismatch"))
                else:
                    checks["explicit_expiry_selected_in_ui"] = False
                    checks["broker_rows_visible_for_expiry"] = False
                    checks["full_chain_truth_visible"] = False
                    checks["dhan_source_visible"] = False
                    checks["no_symbol_mismatch"] = False

            failures = [name for name, ok in checks.items() if ok is not True]
            result.update({
                "checks": checks,
                "failures": failures,
                "baseline": {k: v for k, v in baseline.items() if k not in {"body", "universeValues"}},
                "baseline_universe_values_count": len(universe),
                "sample_equity": sample,
                "equity_snapshot": {k: v for k, v in equity_snapshot.items() if k not in {"body", "universeValues"}},
                "baseline_screenshot_sha256": baseline_hash,
                "state": "PASS" if not failures else "FAIL",
            })
    except Exception as exc:
        result["fatal_error"] = f"{type(exc).__name__}:{str(exc)[:240]}"
        result["failures"] = list(result.get("failures") or []) + [result["fatal_error"]]
        result["state"] = "FAIL"

    (OUT / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("OPTION_CHAIN_UI_PARITY_PROOF " + json.dumps({
        "state": result["state"],
        "expected_sha": EXPECTED_SHA,
        "sample_equity": result.get("sample_equity"),
        "selected_expiry": result.get("selected_expiry"),
        "failures": result.get("failures"),
        "mutations_called": False,
    }, sort_keys=True))
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
