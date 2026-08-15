from scripts.gcp_ui_tab_visual_proof import evaluate_tab_semantics


def test_paper_loading_screen_can_never_pass_again():
    snapshot = {
        "mainText": "Paper Trading Console\nLoading paper positions + Dhan mark-to-market…",
        "paperProofState": "loading",
        "paperLedgerSource": None,
    }
    failures = evaluate_tab_semantics("paper", snapshot)
    joined = " ".join(failures)
    assert "paper_not_settled" in joined
    assert "paper_firestore_ledger_not_proven" in joined
    assert "unsettled_or_error_marker" in joined


def test_paper_settled_firestore_truth_passes_semantic_contract():
    snapshot = {
        "mainText": (
            "Paper Trading Console\n"
            "Durable source: FIRESTORE_PAPER_LEDGER · Ledger v9 · READY\n"
            "Paper Truth Provenance\nFIRESTORE_PAPER_LEDGER\n"
            "Dhan /orders API INTENTIONALLY NOT CALLED\n"
            "Open Paper Positions (0)\nNo open paper positions; durable ledger is available."
        ),
        "paperProofState": "settled",
        "paperLedgerSource": "FIRESTORE_PAPER_LEDGER",
    }
    assert evaluate_tab_semantics("paper", snapshot) == []


def test_generic_signal_loading_screen_fails_even_when_tab_is_active():
    snapshot = {"mainText": "Signals\nLoading signals..."}
    failures = evaluate_tab_semantics("signals", snapshot)
    assert failures
    assert any("LOADING" in item for item in failures)


def test_blank_or_nearly_blank_active_tab_fails():
    assert evaluate_tab_semantics("positions", {"mainText": "Positions"})


def test_truthful_pending_panel_can_pass_when_content_is_settled():
    # PENDING/BLOCKED are truthful analyzer states and are deliberately not
    # treated as browser failures when the panel itself rendered completely.
    snapshot = {
        "mainText": (
            "Prediction Audit\nStatus PENDING\n"
            "No validated prediction outcome is available for this session yet. "
            "LIVE trading remains disabled until evidence gates pass."
        )
    }
    assert evaluate_tab_semantics("prediction-audit", snapshot) == []
