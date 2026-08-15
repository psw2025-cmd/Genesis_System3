from scripts.security_audit_summary import _bandit, _reviewed_static_shell_finding


def _finding(test_id: str, code: str, severity: str = "HIGH"):
    return {
        "issue_severity": severity,
        "filename": "scripts/example.py",
        "line_number": 10,
        "test_id": test_id,
        "test_name": "example",
        "code": code,
    }


def test_exact_static_terminal_clear_is_reviewable_but_not_erased():
    row = _finding("B605", '9 def clear():\n10     os.system("cls" if os.name == "nt" else "clear")\n')
    assert _reviewed_static_shell_finding(row) == "STATIC_TERMINAL_CLEAR_ONLY"
    result = _bandit({"results": [row]}, None)
    assert result["state"] == "WARN"
    assert result["counts"]["HIGH"] == 1
    assert result["unreviewed_high_count"] == 0
    assert len(result["reviewed_static_high_findings"]) == 1


def test_exact_static_windows_taskkill_is_reviewable_but_not_erased():
    row = _finding(
        "B602",
        '9 subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True, shell=True)\n',
    )
    assert _reviewed_static_shell_finding(row) == "STATIC_WINDOWS_TASKKILL_ARGV_ONLY"
    result = _bandit({"results": [row]}, None)
    assert result["state"] == "WARN"
    assert result["unreviewed_high_count"] == 0


def test_dynamic_shell_command_remains_hard_failure():
    row = _finding("B605", "10     os.system(user_supplied_command)\n")
    assert _reviewed_static_shell_finding(row) is None
    result = _bandit({"results": [row]}, None)
    assert result["state"] == "FAIL"
    assert result["unreviewed_high_count"] == 1
    assert result["high_findings"][0]["test_id"] == "B605"


def test_shell_true_with_dynamic_command_remains_hard_failure():
    row = _finding("B602", "10     subprocess.run(command, shell=True)\n")
    assert _reviewed_static_shell_finding(row) is None
    result = _bandit({"results": [row]}, None)
    assert result["state"] == "FAIL"
    assert result["unreviewed_high_count"] == 1
