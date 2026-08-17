from scripts.github_workflow_truth import _classify


def test_missing_run_is_missing():
    assert _classify(None, "abc") == "MISSING"


def test_old_sha_is_stale_even_if_green():
    run = {"head_sha": "old", "status": "completed", "conclusion": "success"}
    assert _classify(run, "new") == "STALE"


def test_exact_sha_in_progress_is_pending():
    run = {"head_sha": "abc", "status": "in_progress", "conclusion": None}
    assert _classify(run, "abc") == "PENDING"


def test_exact_sha_success_is_pass():
    run = {"head_sha": "abc", "status": "completed", "conclusion": "success"}
    assert _classify(run, "abc") == "PASS"


def test_exact_sha_failure_is_fail():
    run = {"head_sha": "abc", "status": "completed", "conclusion": "failure"}
    assert _classify(run, "abc") == "FAIL"
