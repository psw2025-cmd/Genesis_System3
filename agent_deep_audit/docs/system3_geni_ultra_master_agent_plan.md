# System3 GENI Ultra Master Agent – Implementation Plan

Root folder:
- `C:\Genesis_System3`

Primary entry script today:
- `C:\Genesis_System3\system3_ultra.py`

Existing top-level structure:
- `C:\Genesis_System3\config\`
- `C:\Genesis_System3\core\`
- `C:\Genesis_System3\docs\`
- `C:\Genesis_System3\logs\`
- `C:\Genesis_System3\storage\`
- `C:\Genesis_System3\tests\`
- `C:\Genesis_System3\venv\`
- Various runners / BAT / PS1 / validation scripts (already working)

**Non-negotiable constraints (must respect fully):**
1. **Baseline protection:** do not modify or delete any existing baseline models, configs, or engine behavior. Only additive changes.
2. **Ultra isolation:** new GENI master logic must live in clearly separated modules and must not implicitly change live trade behavior.
3. **No real-order auto-execution:** all trade execution must remain DRY-RUN / shadow only. Do not add or enable any function that can send real orders to a broker automatically.
4. **Existing menu, tests, and scripts must continue to pass** without changes to current behavior.
5. **Everything must be deterministic and testable** via clear Python entry points and log outputs.

---

## PHASE 1 – Create GENI Core Module

### Goal
Introduce a small, focused “GENI core” package that knows:
- where everything is,
- how phases map to scripts,
- how to track high-level state,
- how to run validation and health checks in a structured way.

### Tasks

1. **Create package directory**

Create a new package:

- `core/geni/__init__.py`
- `core/geni/geni_config.py`
- `core/geni/geni_state.py`
- `core/geni/geni_tasks.py`
- `core/geni/geni_validator.py`
- `core/geni/geni_orchestrator.py`

Do not modify any existing modules under `core/engine/` or other folders.

2. **geni_config.py**

Implement a small config module:

- Expose constants and path helpers only, no heavy logic.

Required content:

- `PROJECT_ROOT = Path("C:/Genesis_System3").resolve()` (use `Path(__file__)` logic so it also works if root moves; but **default** should be consistent with current layout).
- Useful paths:
  - `PATH_CORE`
  - `PATH_STORAGE`
  - `PATH_LOGS`
  - `PATH_DOCS`
- References to key scripts:
  - `SYSTEM3_ULTRA_ENTRY = PROJECT_ROOT / "system3_ultra.py"`
  - `ULTRA_DAILY_RUNNER = PROJECT_ROOT / "system3_ultra_daily_runner.py"`
  - `ULTRA_RUNTIME_LOOPS = PROJECT_ROOT / "system3_ultra_runtime_loops.py"`
  - `ULTRA_VALIDATION = PROJECT_ROOT / "system3_ultra_validation.py"`
  - `FULL_VERIFICATION = PROJECT_ROOT / "run_full_verification_checklist.py"`

Also add a **safety flag block** (read-only, all False):

```python
AUTO_EXECUTE_REAL_TRADES = False
AUTO_UPDATE_CONFIGS = False
AUTO_PROMOTE_MODELS = False
GENI_ULTRA_LIVE_MODE = False


These must NOT be used to turn on anything live; they are only for future reference and must default to False.

geni_state.py

Implement a small GENI state model to represent high-level system status.

Define a GeniState dataclass with fields like:

timestamp

env_ok: bool

validation_passed: bool

last_validation_summary: str

live_loop_running: bool

pending_issues: list[str]

Provide functions:

load_state(path: Optional[Path] = None) -> GeniState

save_state(state: GeniState, path: Optional[Path] = None) -> None

Store state file in:

storage/geni/system3_geni_state.json

Create the storage/geni/ directory if needed.

State file logic must be safe:

If file missing/corrupt, create a new default state rather than failing.

geni_tasks.py

Implement a registry of high-level tasks that GENI can perform by calling existing scripts.

Create a simple Enum or Literal-based task type, e.g.:

"full_validation"

"quick_validation"

"run_daily_ultra"

"run_ultra_all_logged"

"run_live_watch"

"run_status_check"

"run_ultra_panel_test"

For each task:

Provide a descriptor object with:

name

description

command_line: list of strings (e.g. ["python", "run_full_verification_checklist.py"])

expected_logs (e.g. which log file should contain results)

estimated_runtime_sec (rough metadata only)

Implement:

get_all_tasks() -> dict[str, GeniTask]

get_task(name: str) -> Optional[GeniTask]

Do not execute anything here; only define metadata.

geni_validator.py

Implement helpers to run validation routines and parse their results.

Provide functions like:

run_full_validation() -> ValidationResult

run_quick_validation() -> ValidationResult

Each ValidationResult should contain:

success: bool

total_checks: int

passed: int

failed: int

warnings: list[str]

details: list[str]

Implementation approach:

Use subprocess.run([...], capture_output=True, text=True) to call:

python run_full_verification_checklist.py

OR python system3_ultra_validation.py (for quick validation)

Parse stdout non-fragilely:

Look for key markers like Validation complete, checks passed, etc.

If parsing fails, set success=False but do not crash.

Update GENI state via geni_state.save_state() after each run:

Set validation_passed based on success.

Log a short summary into last_validation_summary.

geni_orchestrator.py

High-level coordinator to:

Load current GeniState

Decide which predefined task(s) to run

Call validator helpers

Produce a clear, small JSON summary of any orchestrated run

Provide main entry:

def run_geni_master(mode: str = "status") -> int:
    ...


Supported modes:

"status": only read state + do a very light check (e.g., verify key files exist, maybe a quick validation if cheap).

"full_validation": run full validation and update state.

"daily_ultra": orchestrate a safe DRY-RUN daily cycle by calling existing drivers (see Phase 2).

"panel_test": run the ultra panel test and record result.

"all": do a combination of the above, but without starting live market loops.

All orchestrator calls must:

Respect safety flags (no real execution).

Use the task registry in geni_tasks.py.

Return 0 on success, non-zero on hard failure.

Write a summary JSON to:

storage/geni/system3_geni_last_run.json

PHASE 2 – Create GENI Master Entry Script
Goal

Add a new top-level entry script to drive GENI orchestration without touching system3_ultra.py.

Tasks

Create new script at root:

C:\Genesis_System3\system3_geni_master.py

Script behavior

Implement a command-line tool with modes:

python system3_geni_master.py status

python system3_geni_master.py full-validation

python system3_geni_master.py daily-ultra

python system3_geni_master.py panel-test

python system3_geni_master.py all

Internally:

Import from core.geni.geni_orchestrator.

Map CLI options → run_geni_master(mode=...).

Print a short human-readable summary to stdout, such as:

overall success / failure

paths of JSON summary and logs

next recommended action (read-only text)

No direct broker or trade execution; only coordination of existing scripts and validators.

Safety printing

Every run must print at top:

"System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)"

This is mandatory to avoid confusion.

PHASE 3 – Integrate with Existing Daily Scripts (Non-breaking)
Goal

Allow GENI master to reuse existing runners, but do not change their behavior.

Tasks

Use, but do not edit:

The following scripts should be called by GENI, not modified:

system3_ultra_daily_runner.py

system3_ultra_runtime_loops.py

system3_ultra_validation.py

run_full_verification_checklist.py

system3_ultra_daily_all.bat

run_system3_ultra_all_logged.BAT

Orchestrator integration

Inside geni_orchestrator.run_geni_master:

For mode "daily_ultra":

Call python system3_ultra_daily_runner.py using subprocess.

Then call python system3_ultra_validation.py.

Capture and summarize results into ValidationResult.

For mode "panel_test":

Call existing ultra panel test script if present (as per current docs/logs).

For mode "all":

Run: full validation → panel test → daily ultra (in that order).

Respect safety flags: no auto enablement of anything.

PHASE 4 – GENI Validation + Health Summary
Goal

Centralize a light-weight JSON + MD summary of GENI master status.

Tasks

Add summary writer in geni_orchestrator

After each run_geni_master:

Compose a dictionary with:

timestamp

mode

success

validation_passed

total_checks

failed_checks

warnings

pending_issues

Write to:

JSON: storage/geni/system3_geni_last_run.json

MD: storage/geni/system3_geni_last_run.md

MD format

The MD file should include:

Header with mode + timestamp

Box with success / failure

Bullet list of warnings (if any)

Next recommended actions (read-only, no execution)

Example structure (pseudo):

# System3 GENI Last Run – <MODE>

- Timestamp: ...
- Success: True/False
- Validation passed: True/False
- Total checks: X
- Failed: Y

## Warnings
- ...

## Recommended Next Actions
- ...

PHASE 5 – Tests and Verification
Goal

Ensure that GENI additions are correct and do not break existing System3 behavior.

Tasks

Add or update tests under tests/

Create new test file:

tests/test_geni_master.py

Tests to include:

Import checks:

import core.geni.geni_config

import core.geni.geni_state

import core.geni.geni_tasks

import core.geni.geni_validator

import core.geni.geni_orchestrator

Basic path correctness:

PROJECT_ROOT points to a directory that contains system3_ultra.py.

PATH_STORAGE exists.

State read/write:

Write a dummy GeniState and read it back; assert equality.

Orchestrator dry-run:

Call run_geni_master("status") inside a test and ensure:

Return code is 0.

system3_geni_last_run.json is created.

Manual verification steps (must all pass)

After implementing code:

Run these from C:\Genesis_System3:

# 1) GENI status
python system3_geni_master.py status

# 2) Full validation via GENI
python system3_geni_master.py full-validation

# 3) Daily ultra orchestration (still DRY-RUN / shadow)
python system3_geni_master.py daily-ultra

# 4) Combined
python system3_geni_master.py all


Expected:

No tracebacks.

Existing validation scripts still behave as before.

New files created:

storage/geni/system3_geni_state.json

storage/geni/system3_geni_last_run.json

storage/geni/system3_geni_last_run.md

PHASE 6 – Documentation
Goal

Provide a concise, operator-level document for using the GENI master.

Tasks

Create new doc file

docs/system3_geni_master_overview.md

Content outline:

What GENI master is

Safety guarantees (explicit bullets)

CLI commands:

status

full-validation

daily-ultra

panel-test

all

Where to find:

GENI state

last run summary

logs

How this interacts with:

system3_ultra.py

daily runners

verification scripts

Explicit note:

GENI master does not place real trades or promote models automatically.

All modes are SAFE and read-only orchestration.

FINAL CHECKLIST (WHAT I EXPECT AFTER IMPLEMENTATION)

After all phases:

New package created:

core/geni/ with the six modules described.

New entry script:

system3_geni_master.py at root.

New storage directory:

storage/geni/ with:

system3_geni_state.json

system3_geni_last_run.json

system3_geni_last_run.md

New tests:

tests/test_geni_master.py passing.

Existing behavior untouched:

system3_ultra.py and all menu options still behave exactly the same.

All commands below run without error:

python system3_geni_master.py status
python system3_geni_master.py full-validation
python system3_geni_master.py daily-ultra
python system3_geni_master.py all


Once implemented, I (the supervising assistant) will review:

system3_geni_master.py contents,

core/geni/*.py contents,

The generated storage/geni/system3_geni_last_run.* files,

And confirm that everything aligns with System3 design, safety, and Ultra architecture.