#!/usr/bin/env python3
"""
Git Auto Workflow — Fully Automated Cloud-Only Git Pipeline
===========================================================
Implements the complete workflow shown in the diagram:

  git status → git diff → commit → push → create branch
  → open PR → auto-approve → merge to main
  → tag version → git pull → Done!

ZERO user action required. All decisions (commit msg, PR title,
version bump, merge approval) are made automatically.

Usage:
  python scripts/git_auto_workflow.py              # full auto
  python scripts/git_auto_workflow.py --dry-run    # preview only
  python scripts/git_auto_workflow.py --bump minor # force version bump type
  python scripts/git_auto_workflow.py --message "feat: my feature"
  python scripts/git_auto_workflow.py --branch feature/my-work
  python scripts/git_auto_workflow.py --skip-tests
  python scripts/git_auto_workflow.py --status     # just show status
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE  = ROOT_DIR / "config" / "git_workflow_config.json"
SEMVER_FILE  = ROOT_DIR / "state" / "semver.json"
WORKFLOW_LOG = ROOT_DIR / "state" / "git_workflow.log"

# Files that must NEVER be committed (security)
NEVER_COMMIT = {
    ".secrets/", ".env", "dhan.env", "*.totp", "credentials.json",
    "state/scheduler_daemon.pid",
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run(cmd: List[str], capture: bool = True, check: bool = False,
         cwd: Path = ROOT_DIR, env: dict = None) -> Tuple[int, str, str]:
    """Run a shell command; returns (returncode, stdout, stderr)."""
    full_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        cmd, capture_output=capture, text=True,
        cwd=str(cwd), env=full_env
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n{result.stderr}"
        )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _retry(fn, max_retries: int = 3, delay: float = 5.0, backoff: float = 2.0):
    """Run fn with exponential-backoff retry on exception."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            wait = delay * (backoff ** attempt)
            print(f"  ↻ retry {attempt+1}/{max_retries} after {wait:.0f}s — {e}")
            time.sleep(wait)
    raise last_exc


def _log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    WORKFLOW_LOG.parent.mkdir(exist_ok=True)
    with open(WORKFLOW_LOG, "a") as f:
        f.write(line + "\n")
    print(line if level in ("ERROR", "WARN") else msg)


def _ist_now() -> str:
    from datetime import timezone, timedelta
    ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    return ist.strftime("%Y-%m-%d %H:%M IST")


# ─────────────────────────────────────────────────────────────────────────────
# Semantic Versioning
# ─────────────────────────────────────────────────────────────────────────────

class SemVer:
    """Semantic version tracker with git-tag awareness."""

    def __init__(self):
        self._load()

    def _load(self):
        # First: check semver.json state file
        if SEMVER_FILE.exists():
            try:
                d = json.loads(SEMVER_FILE.read_text())
                self.major = int(d.get("major", 1))
                self.minor = int(d.get("minor", 0))
                self.patch = int(d.get("patch", 0))
                return
            except Exception:
                pass
        # Fallback: scan git tags
        _, tags, _ = _run(["git", "tag", "--sort=-v:refname"])
        for tag in tags.splitlines():
            m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag.strip())
            if m:
                self.major, self.minor, self.patch = (
                    int(m.group(1)), int(m.group(2)), int(m.group(3))
                )
                self._persist()
                return
        self.major, self.minor, self.patch = 1, 0, 0
        self._persist()

    def _persist(self, history_entry: str = ""):
        d = {"major": self.major, "minor": self.minor, "patch": self.patch,
             "last_tag": self.current(), "last_updated": datetime.now().isoformat()}
        if SEMVER_FILE.exists():
            try:
                old = json.loads(SEMVER_FILE.read_text())
                hist = old.get("history", [])[-49:]  # keep last 50
                if history_entry:
                    hist.append({"version": history_entry, "at": d["last_updated"]})
                d["history"] = hist
            except Exception:
                d["history"] = []
        SEMVER_FILE.parent.mkdir(exist_ok=True)
        SEMVER_FILE.write_text(json.dumps(d, indent=2))

    def current(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def next_version(self, bump: str) -> str:
        m, n, p = self.major, self.minor, self.patch
        if bump == "major":
            return f"v{m+1}.0.0"
        elif bump == "minor":
            return f"v{m}.{n+1}.0"
        else:
            return f"v{m}.{n}.{p+1}"

    def bump(self, kind: str) -> str:
        if kind == "major":
            self.major += 1; self.minor = 0; self.patch = 0
        elif kind == "minor":
            self.minor += 1; self.patch = 0
        else:
            self.patch += 1
        self._persist(self.current())
        return self.current()

    @staticmethod
    def infer_bump(commit_msg: str) -> str:
        """Infer semver bump from conventional commit message."""
        msg = commit_msg.lower()
        prefix = commit_msg.split(":")[0].lower()
        # BREAKING CHANGE or ! suffix = major
        if "breaking change" in msg or prefix.endswith("!"):
            return "major"
        # feat → minor; everything else → patch
        if prefix.startswith("feat"):
            return "minor"
        return "patch"


# ─────────────────────────────────────────────────────────────────────────────
# Commit message generation (AI + heuristic fallback)
# ─────────────────────────────────────────────────────────────────────────────

class CommitMsgGenerator:

    @staticmethod
    def _scope_from_files(files: List[str]) -> str:
        """Derive scope from most-changed directory."""
        dirs = Counter()
        for f in files:
            parts = Path(f).parts
            if len(parts) > 1:
                # Use second level for nested paths (src/ranking → ranking)
                top = parts[0]
                dirs[top] += 1
        if not dirs:
            return ""
        top = dirs.most_common(1)[0][0]
        return top

    @staticmethod
    def _type_from_files(files: List[str]) -> str:
        """Infer conventional commit type from file paths (majority-rules)."""
        scores: Dict[str, int] = Counter()
        for f in files:
            fl = f.lower()
            if fl.startswith("tests/") or "/test_" in fl:
                scores["test"] += 1
            elif fl.endswith(".md"):
                scores["docs"] += 1
            elif fl.startswith("src/") or fl.startswith("core/engine"):
                scores["feat"] += 5   # weighted — production code matters most
            elif fl.startswith("core/"):
                scores["feat"] += 3
            elif fl.startswith("scripts/") or fl.endswith(".yml"):
                scores["chore"] += 2
            elif fl.endswith(".json") or "config" in fl:
                scores["chore"] += 1
            else:
                scores["chore"] += 1
        return scores.most_common(1)[0][0] if scores else "chore"

    @classmethod
    def from_diff(cls, diff_stat: str, changed_files: List[str]) -> str:
        """Try AI first, fall back to heuristic."""
        # 1. Try Claude CLI
        ai_msg = cls._try_claude_cli(diff_stat)
        if ai_msg:
            return ai_msg

        # 2. Heuristic
        return cls._heuristic(changed_files)

    @staticmethod
    def _try_claude_cli(diff_stat: str) -> Optional[str]:
        """Generate commit message using Claude CLI (non-blocking, 15s timeout)."""
        try:
            prompt = (
                "Generate a SINGLE conventional commit message for these git changes. "
                "Format exactly: type(scope): short description — max 72 chars. "
                "Types: feat, fix, chore, docs, test, refactor. "
                "Output ONLY the commit message, nothing else — no quotes, no explanation.\n\n"
                f"Changes:\n{diff_stat[:2000]}"
            )
            rc, out, _ = _run(
                ["claude", "-p", prompt],
                cwd=ROOT_DIR
            )
            if rc == 0 and out:
                line = out.strip().split("\n")[0].strip('"\'')
                # Validate it looks like a conventional commit
                if ":" in line and len(line) <= 100:
                    return line[:72]
        except Exception:
            pass
        return None

    @classmethod
    def _heuristic(cls, changed_files: List[str]) -> str:
        """Build conventional commit message from file analysis."""
        commit_type  = cls._type_from_files(changed_files)
        scope = cls._scope_from_files(changed_files)
        n = len(changed_files)

        # Try to name key files (max 2)
        key = [Path(f).stem for f in changed_files
               if f.endswith(".py") and "test" not in f.lower()][:2]
        if key:
            description = f"update {', '.join(key)}"
        else:
            description = f"update {n} file{'s' if n > 1 else ''}"

        scope_str = f"({scope})" if scope else ""
        return f"{commit_type}{scope_str}: {description}"[:72]


# ─────────────────────────────────────────────────────────────────────────────
# Main workflow
# ─────────────────────────────────────────────────────────────────────────────

class GitAutoWorkflow:
    """
    Fully automated Git workflow — zero user interaction.
    Handles: detect → commit → push → PR → merge → tag → pull.
    """

    def __init__(self, config: dict, dry_run: bool = False):
        self.cfg = config
        self.dry_run = dry_run
        self.semver = SemVer()
        self._summary: List[str] = []

    # ── public entry point ────────────────────────────────────────────────

    def run(
        self,
        branch_name: Optional[str] = None,
        commit_message: Optional[str] = None,
        bump_override: Optional[str] = None,
        skip_tests: bool = False,
    ) -> bool:
        """
        Execute the full pipeline. Returns True on success.
        Steps:
          1  Preflight checks (git clean? remote reachable?)
          2  Run quality gates (tests, syntax)
          3  Stage files (exclude secrets)
          4  Generate / use commit message
          5  Commit
          6  Resolve branch (create auto/ if on main)
          7  Push to remote
          8  Create pull request
          9  Auto-approve + merge PR
          10 Tag version
          11 Pull latest main
          12 Print summary
        """
        print("\n" + "═" * 68)
        print("  GIT AUTO WORKFLOW  —  Genesis System3")
        print(f"  Started: {_ist_now()}")
        print("═" * 68)

        try:
            # ── Step 1: Preflight ─────────────────────────────────────────
            self._step("STEP 1/11 — Preflight checks")
            current_branch = self._current_branch()
            print(f"  Current branch : {current_branch}")
            print(f"  Current version: {self.semver.current()}")

            changed = self._get_changed_files()
            if not changed:
                print("  Nothing to commit — working tree is clean.")
                return True
            print(f"  Changed files  : {len(changed)}")

            # ── Step 2: Quality gates ────────────────────────────────────
            self._step("STEP 2/11 — Quality gates")
            if not skip_tests and self.cfg.get("quality_gates", {}).get("run_tests_before_commit"):
                self._run_tests()
            else:
                print("  Tests: SKIPPED")

            # ── Step 3: Stage files ──────────────────────────────────────
            self._step("STEP 3/11 — Staging files")
            staged = self._stage_files(changed)
            if not staged:
                print("  Nothing to stage after exclusions.")
                return True
            print(f"  Staged {len(staged)} file(s)")

            # ── Step 4: Commit message ───────────────────────────────────
            self._step("STEP 4/11 — Generating commit message")
            if not commit_message:
                _, diff_stat, _ = _run(["git", "diff", "--stat", "--cached"])
                commit_message = CommitMsgGenerator.from_diff(diff_stat, staged)
            print(f"  Message: {commit_message}")

            # ── Step 5: Commit ───────────────────────────────────────────
            self._step("STEP 5/11 — Committing")
            self._commit(commit_message)

            # ── Step 6: Branch resolution ────────────────────────────────
            self._step("STEP 6/11 — Branch resolution")
            target_branch, created = self._resolve_branch(
                current_branch, branch_name, commit_message
            )
            print(f"  Branch: {target_branch}  ({'created' if created else 'existing'})")

            # ── Step 7: Push ─────────────────────────────────────────────
            self._step("STEP 7/11 — Pushing to remote")
            self._push(target_branch)

            # ── Step 8: Pull request ─────────────────────────────────────
            self._step("STEP 8/11 — Opening pull request")
            pr_url, pr_number = self._create_pr(
                target_branch, commit_message, staged
            )
            print(f"  PR #{pr_number}: {pr_url}")

            # ── Step 9: Auto-merge ───────────────────────────────────────
            self._step("STEP 9/11 — Auto-approving & merging PR")
            self._auto_merge(pr_number, commit_message)

            # ── Step 10: Tag version ─────────────────────────────────────
            self._step("STEP 10/11 — Tagging version")
            bump = bump_override or self.semver.infer_bump(commit_message)
            new_tag = self._tag_version(bump, commit_message)
            print(f"  Tagged: {new_tag}  (bump={bump})")

            # ── Step 11: Pull latest ─────────────────────────────────────
            self._step("STEP 11/11 — Pulling latest main")
            self._pull_main()

            # ── Done ─────────────────────────────────────────────────────
            self._print_summary(commit_message, target_branch, pr_url, new_tag)
            return True

        except Exception as e:
            _log(f"WORKFLOW FAILED: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    # ── Steps ─────────────────────────────────────────────────────────────

    def _step(self, name: str):
        print(f"\n{'─'*68}")
        print(f"  {name}")
        print(f"{'─'*68}")
        _log(name)

    def _current_branch(self) -> str:
        _, branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return branch or "main"

    def _get_changed_files(self) -> List[str]:
        """Return list of ALL changed files (staged + unstaged + untracked)."""
        files = []
        _, out, _ = _run(["git", "status", "--porcelain"])
        for line in out.splitlines():
            if len(line) >= 3:
                status = line[:2].strip()
                path   = line[3:].strip()
                # Skip security-sensitive files
                if self._is_excluded(path):
                    print(f"  [EXCLUDED] {path}")
                    continue
                files.append(path)
        return files

    def _is_excluded(self, path: str) -> bool:
        for pattern in NEVER_COMMIT:
            if pattern.endswith("/") and path.startswith(pattern):
                return True
            if path.endswith(pattern.lstrip("*")):
                return True
            if pattern in path:
                return True
        return False

    def _run_tests(self):
        test_cmd = self.cfg.get("quality_gates", {}).get(
            "test_command", "python -m pytest tests/ -q --tb=short"
        )
        print(f"  Running: {test_cmd}")
        if self.dry_run:
            print("  [DRY-RUN] skipping test execution")
            return

        rc, out, err = _run(test_cmd.split())
        if rc == 0:
            # Extract pass count
            last_line = (out + err).strip().splitlines()[-1] if out or err else ""
            print(f"  Tests: PASSED  {last_line}")
        else:
            fail = self.cfg.get("quality_gates", {}).get("fail_on_test_failure", False)
            print(f"  Tests: FAILED  (fail_on_test_failure={fail})")
            if fail:
                raise RuntimeError("Tests failed — aborting commit.")

    def _stage_files(self, changed: List[str]) -> List[str]:
        """Stage all changed files (excluding secrets)."""
        staged = []
        for path in changed:
            if self.dry_run:
                staged.append(path)
                continue
            rc, _, err = _run(["git", "add", path])
            if rc == 0:
                staged.append(path)
            else:
                print(f"  [WARN] could not stage {path}: {err}")
        return staged

    def _commit(self, message: str):
        if self.dry_run:
            print(f"  [DRY-RUN] would commit: {message}")
            return

        # Note: do NOT override --author — Codespaces GPG signing requires
        # the real git user.email to match the authenticated GitHub account.
        rc, out, err = _run(["git", "commit", "-m", message])
        if rc != 0:
            # Nothing staged or other issue
            if "nothing to commit" in out + err:
                print("  Already committed — nothing new to commit.")
            else:
                raise RuntimeError(f"git commit failed: {err}")
        else:
            print(f"  Committed: {out.splitlines()[0] if out else 'ok'}")

    def _resolve_branch(
        self,
        current: str,
        requested: Optional[str],
        commit_msg: str,
    ) -> Tuple[str, bool]:
        """
        Choose/create the branch to push to.
        Rule:
          - If requested name given → use it (create if missing)
          - If on a protected branch (main/master) → create auto/YYYYMMDD-slug
          - Otherwise → stay on current branch
        """
        protected = self.cfg.get("protected_branches",
                                  ["main", "master", "production"])

        if requested:
            target = requested
        elif current in protected:
            slug = re.sub(r"[^a-z0-9-]", "-",
                          commit_msg.split(":")[0].lower())[:20].strip("-")
            date_str = datetime.now().strftime("%Y%m%d")
            target = f"auto/{date_str}-{slug}"
        else:
            target = current  # stay on current feature branch

        # Check if branch exists locally
        _, branches, _ = _run(["git", "branch"])
        exists_locally = any(
            b.strip().lstrip("*").strip() == target
            for b in branches.splitlines()
        )
        created = False

        if not exists_locally and target != current:
            if not self.dry_run:
                rc, _, err = _run(["git", "checkout", "-b", target])
                if rc != 0:
                    raise RuntimeError(f"Could not create branch {target}: {err}")
            created = True

        return target, created

    def _push(self, branch: str):
        if self.dry_run:
            print(f"  [DRY-RUN] would push: {branch}")
            return

        main = self.cfg["main_branch"]

        # Rebase onto latest main before pushing — prevents "not mergeable" errors
        # when a previous PR was squash-merged and left the branch behind.
        _run(["git", "fetch", "origin", main])
        rc_rb, _, rb_err = _run([
            "git", "rebase", f"origin/{main}", "--", "--autostash"
        ])
        if rc_rb != 0:
            # Abort conflicted rebase and push as-is (merge will handle it)
            _run(["git", "rebase", "--abort"])
            print(f"  [WARN] Rebase onto {main} had conflicts — pushing without rebase")
        else:
            print(f"  Rebased onto origin/{main}")

        def _do_push():
            rc, out, err = _run([
                "git", "push", "--set-upstream", "origin", branch, "--force-with-lease"
            ])
            if rc != 0:
                # force-with-lease rejected (remote moved) — force push
                rc2, out2, err2 = _run([
                    "git", "push", "--set-upstream", "origin", branch, "--force"
                ])
                if rc2 != 0:
                    raise RuntimeError(f"Push failed: {err2}")
                return out2
            return out

        _retry(_do_push,
               max_retries=self.cfg["retry"]["max_retries"],
               delay=self.cfg["retry"]["delay_seconds"])
        print(f"  Pushed to origin/{branch}")

    def _create_pr(
        self, branch: str, commit_msg: str, files: List[str]
    ) -> Tuple[str, int]:
        """Create PR from branch → main. Returns (pr_url, pr_number)."""
        main = self.cfg["main_branch"]

        # Check if PR already exists for this branch
        rc, existing, _ = _run([
            "gh", "pr", "list", "--head", branch,
            "--json", "number,url", "--limit", "1"
        ])
        if rc == 0 and existing.strip() not in ("[]", ""):
            try:
                data = json.loads(existing)
                if data:
                    url = data[0]["url"]
                    num = data[0]["number"]
                    print(f"  PR already exists: #{num}")
                    return url, num
            except Exception:
                pass

        title = commit_msg
        body = self._build_pr_body(commit_msg, files)

        if self.dry_run:
            print(f"  [DRY-RUN] would create PR: {title}")
            return "https://github.com/dry-run", 0

        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body",  body,
            "--base",  main,
            "--head",  branch,
        ]

        # Add labels if they exist on the repo
        for label in self.cfg.get("pr", {}).get("labels", []):
            cmd += ["--label", label]

        def _do_create():
            rc, out, err = _run(cmd)
            if rc == 0:
                return out.strip()
            # If label doesn't exist, retry without labels
            if "not found" in err and "--label" in " ".join(cmd):
                cmd_no_labels = [c for i, c in enumerate(cmd)
                                 if c != "--label" and (i == 0 or cmd[i-1] != "--label")]
                rc2, out2, err2 = _run(cmd_no_labels)
                if rc2 == 0:
                    return out2.strip()
                raise RuntimeError(f"gh pr create failed: {err2}")
            raise RuntimeError(f"gh pr create failed: {err}")

        pr_url = _retry(_do_create,
                        max_retries=self.cfg["retry"]["max_retries"],
                        delay=self.cfg["retry"]["delay_seconds"])

        # Extract PR number from URL
        m = re.search(r"/pull/(\d+)", pr_url)
        pr_number = int(m.group(1)) if m else 0
        return pr_url, pr_number

    def _build_pr_body(self, commit_msg: str, files: List[str]) -> str:
        n = len(files)
        file_list = "\n".join(f"  - `{f}`" for f in sorted(files)[:20])
        overflow = f"\n  - _(and {n - 20} more files)_" if n > 20 else ""

        return f"""## Auto-generated PR — Genesis System3

**Commit:** `{commit_msg}`
**Files changed:** {n}
**Timestamp:** {_ist_now()}

### Changed files
{file_list}{overflow}

### Quality gates
- [x] Secrets excluded (`.secrets/`, `.env`)
- [x] Conventional commit format
- [x] Auto-merge via admin bypass

---
🤖 Generated by `scripts/git_auto_workflow.py` | Claude Auto Workflow"""

    def _auto_merge(self, pr_number: int, commit_msg: str):
        """Merge PR using admin bypass — no review needed."""
        if self.dry_run or pr_number == 0:
            print("  [DRY-RUN] would merge PR")
            return

        strategy = self.cfg.get("pr", {}).get("merge_method", "squash")
        merge_flag = f"--{strategy}"

        # Convert draft to ready-for-review (draft PRs cannot be merged)
        rc_draft, pr_state, _ = _run([
            "gh", "pr", "view", str(pr_number),
            "--json", "isDraft", "--jq", ".isDraft"
        ])
        if rc_draft == 0 and pr_state.strip() == "true":
            print(f"  PR #{pr_number} is a draft — marking ready for review...")
            rc_ready, _, err_ready = _run(["gh", "pr", "ready", str(pr_number)])
            if rc_ready != 0:
                print(f"  [WARN] Could not mark ready: {err_ready}")
            else:
                print(f"  PR #{pr_number} is now ready for review")
                time.sleep(2)  # brief pause for GitHub to register state change

        def _do_merge():
            # Primary: admin bypass, squash
            rc, out, err = _run([
                "gh", "pr", "merge", str(pr_number),
                merge_flag, "--admin",
                "--subject", commit_msg,
            ])
            if rc == 0:
                print(f"  Merged PR #{pr_number} ({strategy})")
                return

            # If "not mergeable" — GitHub hasn't computed merge status yet; wait and retry
            if "not mergeable" in err.lower():
                print(f"  PR not mergeable yet (GitHub computing) — waiting 10s...")
                time.sleep(10)
                rc3, _, err3 = _run([
                    "gh", "pr", "merge", str(pr_number),
                    merge_flag, "--admin", "--subject", commit_msg,
                ])
                if rc3 == 0:
                    print(f"  Merged PR #{pr_number} ({strategy})")
                    return
                err = err3

            # Final fallback: regular merge commit (avoids squash conflict issues)
            print(f"  Squash failed ({err[:60]}) — trying regular merge commit...")
            rc2, _, err2 = _run([
                "gh", "pr", "merge", str(pr_number),
                "--merge", "--admin", "--subject", commit_msg,
            ])
            if rc2 != 0:
                raise RuntimeError(f"Merge failed: {err2}")
            print(f"  Merged PR #{pr_number} (merge commit)")

        _retry(_do_merge,
               max_retries=self.cfg["retry"]["max_retries"],
               delay=self.cfg["retry"]["delay_seconds"])

        # Delete branch after merge if configured
        if self.cfg.get("pr", {}).get("delete_branch_after_merge"):
            branch = self._current_branch()
            _run(["gh", "api", f"repos/{{owner}}/{{repo}}/git/refs/heads/{branch}",
                  "--method", "DELETE"])  # best-effort, ignore failure

    def _tag_version(self, bump: str, commit_msg: str) -> str:
        """Bump semver, create git tag, push to remote."""
        if self.dry_run:
            preview = self.semver.next_version(bump)
            print(f"  [DRY-RUN] would tag {preview}  (bump={bump})")
            return preview
        new_tag = self.semver.bump(bump)
        print(f"  {self.semver.current()} (bump={bump})")

        # Fetch latest main before tagging
        _run(["git", "fetch", "origin", self.cfg["main_branch"]])

        # Check if tag already exists
        _, existing_tags, _ = _run(["git", "tag"])
        if new_tag in existing_tags.splitlines():
            print(f"  Tag {new_tag} already exists — skipping.")
            return new_tag

        # Create annotated tag
        tag_msg = f"Release {new_tag} — {commit_msg}"
        rc, _, err = _run([
            "git", "tag", "-a", new_tag, "-m", tag_msg,
            f"origin/{self.cfg['main_branch']}"
        ])
        if rc != 0:
            # Fallback: tag current HEAD
            rc, _, err = _run(["git", "tag", "-a", new_tag, "-m", tag_msg, "HEAD"])

        if rc == 0:
            def _push_tag():
                rc2, _, err2 = _run(["git", "push", "origin", new_tag])
                if rc2 != 0:
                    raise RuntimeError(f"Push tag failed: {err2}")

            _retry(_push_tag,
                   max_retries=self.cfg["retry"]["max_retries"],
                   delay=self.cfg["retry"]["delay_seconds"])
            print(f"  Tag pushed: {new_tag}")
        else:
            print(f"  [WARN] Could not create tag: {err}")

        return new_tag

    def _pull_main(self):
        """Switch to main and pull latest."""
        main = self.cfg["main_branch"]
        if self.dry_run:
            print(f"  [DRY-RUN] would pull {main}")
            return

        # Stash any remaining local changes so checkout doesn't fail
        _, stash_out, _ = _run(["git", "stash", "push", "--include-untracked",
                                 "-m", "auto-workflow-pre-pull"])
        did_stash = "No local changes to save" not in stash_out and stash_out.strip()

        # Switch to main
        rc, _, err = _run(["git", "checkout", main])
        if rc != 0:
            # Unstash and stay on current branch
            if did_stash:
                _run(["git", "stash", "pop"])
            print(f"  [WARN] Could not checkout {main}: {err[:60]}")
            print(f"  Main is merged and tagged — remaining changes go in next workflow run.")
            return

        # Pull with rebase to keep clean history
        def _do_pull():
            rc, out, err = _run(["git", "pull", "--rebase", "origin", main])
            if rc != 0:
                raise RuntimeError(f"git pull failed: {err}")
            return out

        out = _retry(_do_pull,
                     max_retries=self.cfg["retry"]["max_retries"],
                     delay=self.cfg["retry"]["delay_seconds"])
        print(f"  Pulled latest {main}  ✓")

        # Restore any stashed changes back onto main for next workflow run
        if did_stash:
            rc_pop, _, _ = _run(["git", "stash", "pop"])
            if rc_pop == 0:
                print("  Stashed changes restored — run workflow again to commit them.")

    # ── Summary ───────────────────────────────────────────────────────────

    def _print_summary(self, commit_msg: str, branch: str,
                       pr_url: str, tag: str):
        print("\n" + "═" * 68)
        print("  DONE  ✓  Git Auto Workflow completed successfully")
        print("═" * 68)
        print(f"  Commit  : {commit_msg}")
        print(f"  Branch  : {branch} → {self.cfg['main_branch']}")
        print(f"  PR      : {pr_url}")
        print(f"  Version : {tag}")
        print(f"  Time    : {_ist_now()}")
        print("═" * 68 + "\n")

        # Append to CHANGE_LOG.md
        if self.cfg.get("changelog", {}).get("auto_append") and not self.dry_run:
            cl = ROOT_DIR / self.cfg["changelog"]["file"]
            if cl.exists():
                entry = (
                    f"\n### [{_ist_now()}] [AutoWorkflow] DEPLOYED {tag}\n"
                    f"- Commit: `{commit_msg}`\n"
                    f"- PR: {pr_url}\n"
                    f"- Branch: `{branch}` → `{self.cfg['main_branch']}`\n"
                )
                with open(cl, "a") as f:
                    f.write(entry)


# ─────────────────────────────────────────────────────────────────────────────
# Status / inspection mode
# ─────────────────────────────────────────────────────────────────────────────

def show_status():
    """Print current git state and pending changes."""
    print("\n" + "═" * 68)
    print("  GIT AUTO WORKFLOW — Status Report")
    print("═" * 68)

    semver = SemVer()
    _, branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, status, _ = _run(["git", "status", "--porcelain"])
    _, last_commit, _ = _run(["git", "log", "--oneline", "-3"])

    print(f"  Current branch  : {branch}")
    print(f"  Current version : {semver.current()}")
    print(f"  Next versions   : patch={semver.next_version('patch')}  "
          f"minor={semver.next_version('minor')}  "
          f"major={semver.next_version('major')}")
    print()

    changed = [l[3:] for l in status.splitlines() if l.strip()] if status else []
    print(f"  Pending changes : {len(changed)} file(s)")
    for f in changed[:15]:
        print(f"    {f}")
    if len(changed) > 15:
        print(f"    ...and {len(changed)-15} more")

    print()
    print("  Recent commits:")
    for c in last_commit.splitlines():
        print(f"    {c}")

    _, open_prs, _ = _run(["gh", "pr", "list", "--limit", "5"])
    print()
    print("  Open PRs:")
    for pr in open_prs.splitlines():
        print(f"    {pr}")
    print("═" * 68 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            # Merge with defaults for any missing keys
            defaults = {
                "main_branch": "main",
                "branch_prefix": "auto",
                "merge_strategy": "squash",
                "protected_branches": ["main", "master", "production"],
                "pr": {"merge_method": "squash", "delete_branch_after_merge": True, "labels": []},
                "quality_gates": {"run_tests_before_commit": True,
                                  "test_command": "python -m pytest tests/ -q",
                                  "fail_on_test_failure": False},
                "changelog": {"auto_append": True, "file": "CHANGE_LOG.md"},
                "retry": {"max_retries": 3, "delay_seconds": 5, "exponential_backoff": True},
            }
            for k, v in defaults.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception as e:
            print(f"[WARN] Could not load config: {e} — using defaults")
    return {
        "main_branch": "main", "branch_prefix": "auto", "merge_strategy": "squash",
        "protected_branches": ["main", "master", "production"],
        "pr": {"merge_method": "squash", "delete_branch_after_merge": True, "labels": []},
        "quality_gates": {"run_tests_before_commit": True,
                          "test_command": "python -m pytest tests/ -q",
                          "fail_on_test_failure": False},
        "changelog": {"auto_append": True, "file": "CHANGE_LOG.md"},
        "retry": {"max_retries": 3, "delay_seconds": 5, "exponential_backoff": True},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fully automated Git workflow — zero user action required",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--dry-run",    action="store_true",
                        help="Preview what would happen — no changes made")
    parser.add_argument("--status",     action="store_true",
                        help="Show current git status and pending changes")
    parser.add_argument("--branch",     metavar="BRANCH",
                        help="Override branch name (default: auto/YYYYMMDD-slug)")
    parser.add_argument("--message",    metavar="MSG",
                        help="Override commit message (default: AI-generated)")
    parser.add_argument("--bump",       choices=["major", "minor", "patch", "auto"],
                        default="auto", help="Force version bump type")
    parser.add_argument("--skip-tests", action="store_true",
                        help="Skip running tests before commit")
    parser.add_argument("--version",    action="store_true",
                        help="Show current version and exit")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    cfg = _load_config()

    if args.version:
        print(SemVer().current())
        return

    workflow = GitAutoWorkflow(cfg, dry_run=args.dry_run)
    success = workflow.run(
        branch_name=args.branch,
        commit_message=args.message,
        bump_override=None if args.bump == "auto" else args.bump,
        skip_tests=args.skip_tests,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
