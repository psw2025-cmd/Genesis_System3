"""Maintain owner instruction documents; preserve originals and historical evidence."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
MARKER = "OWNER_NSE_DHAN_LIVE_CHECK_20261112"
RULE = """
## OWNER_NSE_DHAN_LIVE_CHECK_20261112 - current owner instruction

- Always check the actual current market using official NSE https://www.nseindia.com/
  and authenticated Dhan read-only market data. Never infer LIVE or market ON/OFF
  solely from weekday, local time, static calendars, HTTP 200, cached files or old reports.
- Verify NSE segment/session status, exchange timestamp, holidays, Muhurat and special
  sessions; inspect corporate actions before interpreting price jumps. Cross-check Dhan
  packet timestamps and same-instrument identity with NSE. Capture UTC and IST.
- LIVE requires fresh market packets (age <=60 seconds), valid positive price and
  independently checked clocks within 5 seconds. Retrieval time is not exchange time.
  A stale page that says Open is STALE, not evidence of current market status.
- Missing, denied, expired, stale or conflicting sources => UNKNOWN/UNVERIFIED or STALE;
  show the reason, never assume market closed or invent prices or green readiness.
- Dhan reads only: never call order routes or auto-renew tokens during a check.
  Do not print secrets. Stop on authentication/rate-limit errors; no retry hammering.
- Canonical mission/state: agent_deep_audit/.agents/mission and state. Other copies
  are OLD_IGNORE_DO_NOT_USE. Preserve historical evidence; do not import old PASS as proof.
- Latest owner permits autonomous discovery, backup, fixes, tests and safe branch push.
  Continue small batches; separate explicit YES still required for deployment, billing,
  IAM, secrets and deletion. No real orders. No unattended-monitoring claim without proof.
"""


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%SZ")
    paths = ["AGENTS.md", "GEMINI.md", "TASK_LIST.md",
             "agent_deep_audit/AGENTS.md", "agent_deep_audit/GEMINI.md",
             "agent_deep_audit/.agents/mission/OWNER_GOALS.md",
             "agent_deep_audit/.agents/mission/EVIDENCE_PASS_CONTRACT.md",
             "agent_deep_audit/.agents/state/PROGRESS.md",
             "agent_deep_audit/.agents/state/BLOCKERS.md",
             "agent_deep_audit/.agents/state/SESSION_HANDOFF.md",
             "docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md",
             "docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md",
             "agent_control_audit/AGENTS.md", "agent_control_audit/GEMINI.md",
             "agent_deep_audit/agent_control_audit/AGENTS.md",
             "agent_deep_audit/agent_control_audit/GEMINI.md"]
    double = ROOT / "agent_deep_audit/.agents/mission/MASTER_CONTRACT_FINAL.md.md"
    single = double.with_name("MASTER_CONTRACT_FINAL.md")
    if double.exists() and not single.exists():
        shutil.copy2(double, Path(str(double) + "_" + stamp + ".bak"))
        shutil.copy2(double, single)
        double.rename(Path(str(double) + ".OLD_IGNORE_DO_NOT_USE"))
    if single.exists():
        paths.append(str(single.relative_to(ROOT)))
    changed = []
    for rel in paths:
        path = ROOT / rel
        if not path.exists():
            continue
        old = path.read_text(encoding="utf-8-sig")
        if MARKER in old:
            continue
        shutil.copy2(path, Path(str(path) + "_" + stamp + ".bak"))
        prefix = ""
        if "agent_control_audit/" in rel or rel in ("agent_deep_audit/AGENTS.md", "agent_deep_audit/GEMINI.md"):
            prefix = "# OLD_IGNORE_DO_NOT_USE - historical local-first rules below are superseded\n"
        if "/state/" in rel:
            prefix += "# RE-VERIFY - historical PASS/RESOLVED below is not current certification\n"
        path.write_text(prefix + RULE + "\n" + old, encoding="utf-8")
        changed.append(rel)
    tracker = ROOT / "agent_deep_audit/.agents/state/INDEPENDENT_VERIFICATION.csv"
    source = ROOT / ".agents/state/INDEPENDENT_VERIFICATION.csv"
    if not tracker.exists():
        # Recover check identity and history, never promote the old independent verdict.
        with source.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        assert len(rows) == 1872 and len({r['ID'] for r in rows}) == 1872
        for row in rows:
            row["Independent Verdict"] = "UNVERIFIED"
            for field in ("Independent Raw Evidence URI", "Independent Reviewer", "Verified UTC", "Expected vs Observed"):
                row[field] = ""
            row["Blocker / Next Action"] = "Recovered historical identity only; fresh NSE+Dhan, cloud/UI and independent proof required."
        with tracker.open("x", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        changed.append(str(tracker.relative_to(ROOT)))
    print(json.dumps({"changed": changed, "tracker_sha256": hashlib.sha256(tracker.read_bytes()).hexdigest(),
                      "status": "Instruction maintenance only; no production acceptance"}))


if __name__ == "__main__":
    main()
