#!/usr/bin/env python3
"""
Weekly QC audit: run comprehensive_qc_audit and archive results in proof/archive.
Creates proof/archive/qc_audit_YYYYMMDD.json and qc_audit_YYYYMMDD_summary.txt.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOF_DIR = ROOT / "proof"
PROOF_ARCHIVE = PROOF_DIR / "archive"
QC_SCRIPT = ROOT / "comprehensive_qc_audit.py"
QC_REPORT = ROOT / "QC_AUDIT_REPORT_DETAILED.json"


def main():
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    PROOF_ARCHIVE.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    result = subprocess.run(
        [sys.executable, str(QC_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Archive in proof/ (primary) and proof/archive/ (copy)
    archive_json = PROOF_DIR / f"qc_audit_{today}.json"
    archive_txt = PROOF_DIR / f"qc_audit_{today}_summary.txt"
    archive_json_copy = PROOF_ARCHIVE / f"qc_audit_{today}.json"
    archive_txt_copy = PROOF_ARCHIVE / f"qc_audit_{today}_summary.txt"

    if QC_REPORT.exists():
        data = json.loads(QC_REPORT.read_text(encoding="utf-8"))
        for p in (archive_json, archive_json_copy):
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        c = data.get("critical", 0)
        w = data.get("warning", 0)
        i = data.get("info", 0)
        lines = [
            f"QC audit archive {today}",
            f"  critical={c} warning={w} info={i}",
            f"  source={QC_REPORT}",
            f"  exit_code={result.returncode}",
        ]
        if c > 0:
            lines.append("  ACTION: Document and propose fixes.")
        else:
            lines.append("  No action required — already optimal." if (w == 0 and c == 0) else "  Monitor warnings.")
        content = "\n".join(lines)
        archive_txt.write_text(content, encoding="utf-8")
        archive_txt_copy.write_text(content, encoding="utf-8")
        print(f"[OK] QC audit archived: {archive_json.relative_to(ROOT)}, {archive_txt.relative_to(ROOT)}")
    else:
        for p in (archive_txt, archive_txt_copy):
            p.write_text(
                f"QC audit run {today}; report not found (exit_code={result.returncode}).\n",
                encoding="utf-8",
            )
        print(f"[WARN] QC report not found; summary only: {archive_txt.relative_to(ROOT)}")

    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
