from scripts.security_audit_summary import (
    _bandit,
    _bandit_finding_source_line,
    _reviewed_static_shell_finding,
)


def _finding(test_id: str, code: str, severity: str = "HIGH", line_number: int = 10):
    return {
        "issue_severity": severity,
        "filename": "scripts/example.py",
        "line_number": line_number,
        "test_id": test_id,
        "test_name": "example",
        "code": code,
    }


def test_exact_static_terminal_clear_is_reviewable_but_not_erased():
    row = _finding("B605", '9 def clear():\n10     os.system("cls" if os.name == "nt" else "clear")\n')
    assert _bandit_finding_source_line(row) == 'os.system("cls" if os.name == "nt" else "clear")'
    assert _reviewed_static_shell_finding(row) == "STATIC_TERMINAL_CLEAR_ONLY"
    result = _bandit({"results": [row]}, None)
    assert result["state"] == "WARN"
    assert result["counts"]["HIGH"] == 1
    assert result["unreviewed_high_count"] == 0
    assert len(result["reviewed_static_high_findings"]) == 1


def test_exact_static_windows_taskkill_is_reviewable_but_not_erased():
    row = _finding(
        "B602",
        '10 subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True, shell=True)\n',
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


def test_shell_true_with_dynamic_command_remains_hard_failure():
    row = _finding("B602", "10     subprocess.run(command, shell=True)\n")
    assert _reviewed_static_shell_finding(row) is None
    assert _bandit({"results": [row]}, None)["state"] == "FAIL"


def test_safe_terminal_clear_on_neighbor_line_cannot_mask_dynamic_b605_finding():
    row = _finding(
        "B605",
        '9 os.system("cls" if os.name == "nt" else "clear")\n10 os.system(user_supplied_command)\n11 return None\n',
        line_number=10,
    )
    assert _bandit_finding_source_line(row) == "os.system(user_supplied_command)"
    assert _reviewed_static_shell_finding(row) is None
    assert _bandit({"results": [row]}, None)["state"] == "FAIL"


def test_safe_taskkill_on_neighbor_line_cannot_mask_dynamic_b602_finding():
    row = _finding(
        "B602",
        '9 subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True, shell=True)\n'
        '10 subprocess.run(command, shell=True)\n',
        line_number=10,
    )
    assert _bandit_finding_source_line(row) == "subprocess.run(command, shell=True)"
    assert _reviewed_static_shell_finding(row) is None
    assert _bandit({"results": [row]}, None)["state"] == "FAIL"


def test_ambiguous_multiline_unnumbered_bandit_code_fails_closed():
    row = _finding(
        "B605",
        'os.system("cls" if os.name == "nt" else "clear")\nos.system(user_supplied_command)\n',
        line_number=10,
    )
    assert _bandit_finding_source_line(row) == ""
    assert _reviewed_static_shell_finding(row) is None
    assert _bandit({"results": [row]}, None)["state"] == "FAIL"
