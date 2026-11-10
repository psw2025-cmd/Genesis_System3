"""Blocker finder must not crash Windows post-market pipeline on console encoding."""

from pathlib import Path
import subprocess
import sys

from scripts.system3_blocker_finder import parse_blocker_finder_args, run_automated_scan


def test_parse_api_base_does_not_steal_repo_root():
    args = parse_blocker_finder_args(["--api-base", "http://127.0.0.1:8000"])
    assert args.api_base == "http://127.0.0.1:8000"
    assert Path(args.repo_root).is_dir()
    assert not str(args.repo_root).startswith("--")
    assert "http://" not in str(args.output_dir)


def test_scan_prints_are_ascii_safe(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "scripts.system3_blocker_finder.SystemBlockerFinder.generate_report",
        lambda self, path, api_url=None: {
            "summary": {
                "total_findings": 0,
                "repo_findings": 0,
                "runtime_issues": 0,
                "known_blockers": 0,
                "new_potential_blockers": 0,
            },
            "recommendations": ["FIX_PRIORITY: example"],
        },
    )
    report = run_automated_scan(str(tmp_path), str(tmp_path / "out"))
    out = capsys.readouterr().out
    assert report["summary"]["new_potential_blockers"] == 0
    assert out.encode("cp1252")  # must not raise UnicodeEncodeError
    assert "Starting automated blocker scan" in out


def test_scan_skips_reports_tree(tmp_path):
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "ok.py").write_text("# clean\n", encoding="utf-8")
    reports = tmp_path / "reports" / "latest"
    reports.mkdir(parents=True)
    (reports / "huge.json").write_text('{"BLOCKER": "noise"}\n' * 1000, encoding="utf-8")
    from scripts.system3_blocker_finder import SystemBlockerFinder

    finder = SystemBlockerFinder(tmp_path, tmp_path / "out")
    files = finder._candidate_scan_files(
        {".git", "reports", "storage", "logs", "node_modules", "dist", "build", "__pycache__"}
    )
    rels = {str(p.relative_to(tmp_path)).replace("\\", "/") for p in files}
    assert "core/ok.py" in rels
    assert not any(r.startswith("reports/") for r in rels)


def test_blocker_finder_cli_with_api_base_exits_zero(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "system3_blocker_finder.py"
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONIOENCODING"] = "cp1252"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            str(tmp_path),
            str(tmp_path / "out"),
            "--api-base",
            "http://127.0.0.1:8000",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[-1500:] or proc.stdout[-1500:]
    assert (tmp_path / "out" / "blocker_report.json").is_file()
