# auto_security_patch.py
# SYSTEM3 Auto Security Patch (Windows + Python 3.10)
# - Removes subprocess(..., shell=True) usage (Bandit B602/B605) with safe list form
# - Adds timeout=5 to requests.* calls missing timeout (Bandit/B113 style operational hardening)
# - Replaces "--host 0.0.0.0" with "--host 127.0.0.1" in .bat/.ps1/.md/.txt (safe local binding)
# - Leaves Jupyter intact (no removal)
#
# Usage:
#   1) Activate venv:
#        .\.venv\Scripts\Activate.ps1
#   2) Run from repo root:
#        python auto_security_patch.py --apply
#      (or preview only)
#        python auto_security_patch.py
#
# Output:
#   - outputs/proof/security_patch_report_<timestamp>.txt
#   - creates backups next to each modified file: <file>.bak_<timestamp>

from __future__ import annotations
import argparse
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(r"C:\Genesis_System3")
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".git",
    "logs",
    "outputs",
    "storage",
    "models",
    "agent_memory",
}

TEXT_EXTS = {
    ".py", ".ps1", ".bat", ".cmd", ".json", ".yaml", ".yml", ".ini", ".cfg", ".toml"
}

REQUESTS_CALL_RE = re.compile(r"\brequests\.(get|post|put|delete|patch|head|options)\s*\(", re.IGNORECASE)

# Very conservative: only patch shell=True when command looks like a single string literal.
# Example: subprocess.run(['python', 'script.py'], check=True)
SHELL_TRUE_SIMPLE_RE = re.compile(
    r"""
    (?P<prefix>\bsubprocess\.(?:run|call|check_call|check_output)\s*\(\s*)
    (?P<q>["\'])
    (?P<cmd>[^"\']+)
    (?P=q)
    (?P<rest>\s*,\s*[^)]*?)
    \bshell\s*=\s*True\b
    (?P<suffix>[^)]*\))
    """,
    re.VERBOSE,
)

# Replace host binding in script-like text files
HOST_0000_RE = re.compile(r"(--host\s+)0\.0\.0\.0\b")

def is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False

def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and not is_excluded(p) and (p.suffix.lower() in TEXT_EXTS):
            yield p

def backup_file(path: Path, stamp: str) -> Path:
    bak = path.with_name(path.name + f".bak_{stamp}")
    shutil.copy2(path, bak)
    return bak

def patch_shell_true(content: str) -> Tuple[str, List[str]]:
    """
    Convert subprocess.*("cmd string", shell=True) -> subprocess.*(["cmd","arg"], check=True)
    For safety, we only patch when the command is a single string literal.
    We do not attempt to patch dynamic expressions.
    """
    changes = []
    def repl(m: re.Match) -> str:
        cmd = m.group("cmd").strip()
        # Convert to a minimal safe tokenization:
        # - split on whitespace but keep quoted segments basic (simple approach)
        # Better would be shlex, but shlex on Windows differs; keep conservative.
        parts = re.findall(r'''(?:[^\s"']+|"(?:[^"]*)"|'(?:[^']*)')+''', cmd)
        # strip quotes around tokens
        parts = [t[1:-1] if (len(t) >= 2 and ((t[0] == t[-1] == '"') or (t[0] == t[-1] == "'"))) else t for t in parts]
        # Ensure we always add check=True if not present
        rest = m.group("rest")
        suffix = m.group("suffix")
        # Remove shell=True from rest (already matched) and ensure commas are tidy
        rest2 = re.sub(r"\s*,?\s*\bshell\s*=\s*True\b\s*,?\s*", ", ", rest, flags=re.IGNORECASE)
        # If check= not in arguments, add check=True
        if re.search(r"\bcheck\s*=", rest2) is None and re.search(r"\bsubprocess\.(?:run|call)\b", m.group("prefix")):
            # For call/run, check=True is meaningful; for check_output it is not accepted.
            # Determine which function:
            func = re.search(r"subprocess\.(run|call|check_call|check_output)", m.group("prefix"))
            func_name = func.group(1) if func else "run"
            if func_name in {"run", "call"}:
                # insert check=True near end before suffix's closing
                # We'll append to rest2 if it has other args
                rest2 = rest2.rstrip()
                if rest2.endswith(","):
                    rest2 += " check=True"
                else:
                    rest2 += ", check=True"

        new = f'{m.group("prefix")}{parts!r}{rest2}{suffix}'
        changes.append(f"Patched shell=True command: {cmd!r} -> {parts!r}")
        return new

    new_content = SHELL_TRUE_SIMPLE_RE.sub(repl, content)
    return new_content, changes

def patch_requests_timeout(content: str) -> Tuple[str, List[str]]:
    """
    Add timeout=5 to requests.<method>(...) calls when missing.
    Conservative: only modifies the call's argument list opening line until first ')'
    """
    changes = []
    lines = content.splitlines(True)
    out = []
    for line in lines:
        if REQUESTS_CALL_RE.search(line) and ("timeout=" not in line):
            # Insert timeout=5 before closing ) if it appears on same line
            if ")" in line:
                # insert before last ')'
                idx = line.rfind(")")
                before, after = line[:idx], line[idx:]
                # If there are already args (other than '('), add comma.
                if before.strip().endswith("("):
                    new_line = before + "timeout=5" + after
                else:
                    # ensure comma separation
                    new_line = before.rstrip() + ", timeout=5" + after
                out.append(new_line)
                changes.append("Added timeout=5 to requests call (single-line).")
            else:
                out.append(line)
        else:
            out.append(line)
    return "".join(out), changes

def patch_host_binding(content: str) -> Tuple[str, List[str]]:
    changes = []
    new_content, n = HOST_0000_RE.subn(r"\g<1>127.0.0.1", content)
    if n:
        changes.append(f"Replaced --host 0.0.0.0 with --host 127.0.0.1 ({n} occurrences).")
    return new_content, changes

def patch_file(path: Path) -> Tuple[bool, List[str]]:
    """
    Returns (modified, changes)
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, [f"SKIP {path}: read error: {e}"]

    changes_all: List[str] = []
    new = raw

    if path.suffix.lower() == ".py":
        new, ch = patch_shell_true(new); changes_all += [f"{path.name}: {c}" for c in ch]
        new, ch = patch_requests_timeout(new); changes_all += [f"{path.name}: {c}" for c in ch]

    # host binding patch for script-like text files
    if path.suffix.lower() in {".bat", ".cmd", ".ps1"}:
        new, ch = patch_host_binding(new); changes_all += [f"{path.name}: {c}" for c in ch]

    modified = (new != raw)
    if modified:
        path.write_text(new, encoding="utf-8", errors="ignore")
    return modified, changes_all

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Apply changes (otherwise preview only)")
    args = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    proof_dir = ROOT / "outputs" / "proof"
    proof_dir.mkdir(parents=True, exist_ok=True)
    report_path = proof_dir / f"security_patch_report_{stamp}.txt"

    modified_files = []
    report_lines = []
    report_lines.append(f"ROOT: {ROOT}")
    report_lines.append(f"MODE: {'APPLY' if args.apply else 'PREVIEW'}")
    report_lines.append(f"STAMP: {stamp}")
    report_lines.append("")

    for f in iter_files(ROOT):
        try:
            raw = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            report_lines.append(f"SKIP {f}: read error: {e}")
            continue

        # compute changes without applying (preview) by patching in-memory
        if args.apply:
            # backup before patch
            bak = backup_file(f, stamp)
            modified, changes = patch_file(f)
            if modified:
                modified_files.append(f)
                report_lines.append(f"MODIFIED: {f} (backup: {bak.name})")
                report_lines.extend(changes if changes else ["(no change details)"])
                report_lines.append("")
            else:
                # If no modification, remove backup to avoid clutter
                try:
                    bak.unlink(missing_ok=True)
                except Exception:
                    pass
        else:
            # preview mode: patch in-memory
            changes_all = []
            new = raw
            if f.suffix.lower() == ".py":
                new, ch = patch_shell_true(new); changes_all += ch
                new, ch = patch_requests_timeout(new); changes_all += ch
            if f.suffix.lower() in {".bat", ".cmd", ".ps1", ".md", ".txt"}:
                new, ch = patch_host_binding(new); changes_all += ch

            if new != raw:
                report_lines.append(f"WOULD MODIFY: {f}")
                report_lines.extend([f" - {c}" for c in changes_all] if changes_all else [" - (no change details)"])
                report_lines.append("")

    report_lines.append("SUMMARY")
    report_lines.append(f"Modified files: {len(modified_files)}" if args.apply else "Preview completed.")
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Report written: {report_path}")
    if args.apply:
        print(f"Modified files: {len(modified_files)}")
        print("Next recommended commands:")
        print(r"  python -m bandit -r . -q -x "".venv,node_modules,logs,outputs,storage,models,agent_memory,docs""")
        print(r"  pip-audit")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())