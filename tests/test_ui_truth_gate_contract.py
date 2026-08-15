import re
from pathlib import Path


def _tab_pairs(text: str):
    return re.findall(r"\{\s*id:\s*'([^']+)',\s*label:\s*'([^']+)'", text)


def test_browser_truth_gate_covers_every_sidebar_tab_exactly_once():
    sidebar = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
    proof = Path("tools/playwright-setup/verify_all_ui_tabs.spec.ts").read_text(encoding="utf-8")

    sidebar_tabs = _tab_pairs(sidebar)
    proof_tabs = _tab_pairs(proof)

    assert len(sidebar_tabs) == 22
    assert len(proof_tabs) == len(sidebar_tabs)
    assert proof_tabs == sidebar_tabs
    assert len({tab_id for tab_id, _ in proof_tabs}) == len(proof_tabs)


def test_option_chain_browser_truth_gate_is_semantic_not_render_only():
    proof = Path("tools/playwright-setup/verify_all_ui_tabs.spec.ts").read_text(encoding="utf-8")

    required = [
        "DHAN_UNIVERSE_NOT_BROKER_BREADTH",
        "EQUITY_OPTIONS_MISSING",
        "EXPIRIES_MISSING",
        "OPTION_CONTRACTS_MISSING",
        "OPTION_STRIKES_MISSING",
        "ALL_STRIKES_VISIBILITY_NOT_PROVEN",
        "UNDERLYING_DISCOVERY_DEGRADED",
        "CHAIN_SYMBOL_MISMATCH",
    ]
    for marker in required:
        assert marker in proof


def test_proof_gate_retains_live_off_safety_visibility():
    proof = Path("tools/playwright-setup/verify_all_ui_tabs.spec.ts").read_text(encoding="utf-8")
    assert "'PAPER'" in proof
    assert "'LIVE OFF'" in proof
