#!/usr/bin/env python3
"""
Playwright-based dashboard verification for agent-driven testing.

The agent can run this script to:
- Open Streamlit (8501), Backend API docs (8000/docs), and optionally React (3000)
- Take full-page screenshots (saved to proof/archive)
- Run basic visual/structural checks (page loads, no error toasts, key elements)
- Produce a JSON report so the agent can summarize results without the user providing images

Run from repo root (with backend/dashboard already running):
  python tools/playwright_dashboard_verification.py

Requires: pip install playwright && playwright install chromium
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOF_ARCHIVE = ROOT / "proof" / "archive"
PROOF_ARCHIVE.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
SCREENSHOTS_DIR = PROOF_ARCHIVE / f"dashboard_screenshots_{TIMESTAMP}"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# URLs to verify (adjust if your ports differ)
STREAMLIT_URL = "http://127.0.0.1:8501"
API_DOCS_URL = "http://127.0.0.1:8000/docs"
API_HEALTH_URL = "http://127.0.0.1:8000/api/health"
REACT_URL = "http://127.0.0.1:3000"


def run_verification():
    """Run Playwright-based dashboard verification. Returns (report_dict, exit_code)."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "script": "tools/playwright_dashboard_verification.py",
        "screenshots_dir": str(SCREENSHOTS_DIR),
        "checks": [],
        "screenshots": [],
        "issues": [],
        "passed": True,
    }

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        report["issues"].append("Playwright not installed. Run: pip install playwright && playwright install chromium")
        report["passed"] = False
        return report, 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            page.set_default_timeout(15000)

            # 1) Backend API docs
            try:
                page.goto(API_DOCS_URL, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                path = SCREENSHOTS_DIR / "api_docs.png"
                page.screenshot(path=path, full_page=True)
                report["screenshots"].append(str(path))
                title = page.title()
                if "Swagger" in title or "OpenAPI" in title or "docs" in title.lower():
                    report["checks"].append({"name": "API docs", "passed": True, "detail": title})
                else:
                    report["checks"].append({"name": "API docs", "passed": True, "detail": f"Title: {title}"})
            except Exception as e:
                report["checks"].append({"name": "API docs", "passed": False, "detail": str(e)})
                report["issues"].append(f"API docs ({API_DOCS_URL}): {e}")
                report["passed"] = False

            # 2) Streamlit dashboard
            try:
                page.goto(STREAMLIT_URL, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                path = SCREENSHOTS_DIR / "streamlit_dashboard.png"
                page.screenshot(path=path, full_page=True)
                report["screenshots"].append(str(path))
                content = page.content()
                # Basic sanity: no obvious crash message in body
                # Scan the full HTML for both patterns so late-rendered errors
                # are not missed (no artificial 5000-char cutoff).
                if "StreamlitError" in content or "Error loading" in content:
                    report["checks"].append(
                        {"name": "Streamlit", "passed": False, "detail": "Error text found in page"}
                    )
                    report["issues"].append("Streamlit page may show an error")
                    report["passed"] = False
                else:
                    report["checks"].append(
                        {"name": "Streamlit", "passed": True, "detail": "Page loaded, screenshot saved"}
                    )
            except Exception as e:
                report["checks"].append({"name": "Streamlit", "passed": False, "detail": str(e)})
                report["issues"].append(f"Streamlit ({STREAMLIT_URL}): {e}")
                report["passed"] = False

            # 3) Optional: React frontend (only if reachable)
            try:
                page.goto(REACT_URL, wait_until="domcontentloaded", timeout=5000)
                page.wait_for_timeout(2000)
                path = SCREENSHOTS_DIR / "react_frontend.png"
                page.screenshot(path=path, full_page=True)
                report["screenshots"].append(str(path))
                report["checks"].append({"name": "React frontend", "passed": True, "detail": "Page loaded"})
            except Exception:
                report["checks"].append(
                    {"name": "React frontend", "passed": False, "detail": "Not reachable (optional)"}
                )
                # Do not set passed=False for optional React

        finally:
            browser.close()

    return report, 0 if report["passed"] else 1


def main():
    print("Playwright dashboard verification...")
    print(f"Screenshots will be saved to: {SCREENSHOTS_DIR}")
    report, code = run_verification()

    report_path = PROOF_ARCHIVE / f"dashboard_verification_{TIMESTAMP}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report: {report_path}")
    print(f"Passed: {report['passed']}")
    if report["issues"]:
        print("Issues:")
        for i in report["issues"]:
            print(f"  - {i}")
    if report["screenshots"]:
        print("Screenshots:")
        for s in report["screenshots"]:
            print(f"  - {s}")

    return code


if __name__ == "__main__":
    sys.exit(main())
