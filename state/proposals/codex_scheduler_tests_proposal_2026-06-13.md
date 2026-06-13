# Codex Proposal: Scheduler Daemon + Test Suite
**Date:** 2026-06-13  
**Author:** Codex  
**Status:** AWAITING Gemini cross-verification  
**File:** `state/proposals/codex_scheduler_tests_proposal_2026-06-13.md`

---

## Problem Summary

Two distinct gaps identified after reading SYSTEM_STATE.md, CHANGE_LOG.md, and all relevant source files:

### Gap 1 — Scheduler Time Enforcement
`config/system3_job_scheduler.json` has 7 jobs with `schedule_time` fields (`08:00`, `09:15`, `15:35`, `15:40`, `16:00`, `18:30`, and implicit `daily`). However, `core/engine/system3_phase82_job_scheduler.py:run_job()` completely ignores `schedule_time`. There is **no daemon loop** — the scheduler only runs jobs when invoked manually via `--run-once` or `--job-id`. The scheduling metadata is declared but never enforced.

Existing daemons in the repo (`dhan_token_auto_refresh.py`, `dhan_watchdog_runner.py`) each handle their own domain and are NOT general orchestrators. There are **no systemd unit files or crontab entries** in the repository (verified via `find` and `grep` — no `.service`, `.timer`, or crontab references in active code). The only cron references are in comments inside `setup_dhan_automation.py` and `daily_gain_rank_and_validate.py`.

**Conclusion: a `--daemon` mode added to the scheduler would not conflict with any existing systemd/cron setup. The field is entirely empty.**

### Gap 2 — No Tests for New Data Modules
Three new modules added 2026-06-13 have zero test coverage:
- `core/data/datasource_manager.py` — `_try_bhavcopy()` parser
- `core/data/datasource_manager.py` — fallback chain logic
- `core/data/nse_provider.py` — OI cache staleness guards

---

## Conflict Assessment: --daemon vs Existing Setup

**SAFE TO ADD — no conflicts.**

Evidence:
1. No `.service` or `.timer` files anywhere in the repo.
2. `setup_dhan_automation.py` only *prints* crontab instructions, never installs them.
3. The two running daemons (`dhan_token_auto_refresh.py`, `dhan_watchdog_runner.py`) run as ad-hoc background processes started manually, not via system init.
4. The job scheduler's `--run-once` mode is triggered manually (or from a calling script). Nobody calls it on a timer.
5. Adding `--daemon` is purely additive; `--run-once`, `--list`, and `--job-id` remain unchanged.

**One operational note:** If user later adds a crontab entry calling `--run-once`, they should NOT also run `--daemon` simultaneously — that would fire each job twice. The `--daemon` mode should log its PID to `state/scheduler_daemon.pid` to make it detectable.

---

## Part 1: Daemon Loop Implementation

### Code to insert into `core/engine/system3_phase82_job_scheduler.py`

Insert these imports at the top (no new dependencies — all standard library):

```python
import time
import signal
from datetime import timezone, timedelta
```

Insert the following functions before `main()`:

```python
# IST = UTC+5:30
_IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> datetime:
    """Current time in IST (no pytz dependency — stdlib only)."""
    return datetime.now(_IST)


def _time_matches(schedule_time: str, now: datetime, window_seconds: int = 60) -> bool:
    """
    Returns True if now (IST) is within window_seconds of schedule_time (HH:MM).
    schedule_time == 'daily' is handled by the caller (always True once per day).
    """
    if not schedule_time or schedule_time.lower() == "daily":
        return False  # 'daily' has no specific clock time — handled separately
    try:
        h, m = map(int, schedule_time.split(":"))
    except ValueError:
        return False
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    diff = abs((now - target).total_seconds())
    return diff <= window_seconds


def _is_weekday(now: datetime) -> bool:
    """Returns True if now is Monday–Friday (IST)."""
    return now.weekday() < 5  # 0=Mon … 4=Fri; 5=Sat, 6=Sun


def _append_change_log(message: str) -> None:
    """Append a one-line entry to CHANGE_LOG.md."""
    change_log = PROJECT_ROOT / "CHANGE_LOG.md"
    if not change_log.exists():
        return
    # Insert above the footer sentinel if present, else append
    try:
        text = change_log.read_text(encoding="utf-8")
        sentinel = "<!-- APPEND NEW ENTRIES ABOVE THIS LINE -->"
        entry = f"\n**{message}**\n"
        if sentinel in text:
            text = text.replace(sentinel, entry + sentinel)
        else:
            text += entry
        change_log.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"[PH82-Daemon] CHANGE_LOG write failed: {e}")


def run_daemon() -> None:
    """
    Daemon loop: checks every 60 seconds whether any enabled job is due to run.

    Scheduling rules:
      - schedule_time HH:MM  → fires once when IST clock enters that minute window
      - schedule_time 'daily' → fires once per calendar day (no specific time)
      - weekdays_only: true  → skipped on Saturday and Sunday (IST)
      - last_fired tracking  → prevents double-firing within the same minute window

    KeyboardInterrupt / SIGTERM → clean exit (saves state first).
    """
    pid_file = PROJECT_ROOT / "state" / "scheduler_daemon.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))

    print(f"[PH82-Daemon] Started PID={os.getpid()} at {_now_ist().strftime('%Y-%m-%d %H:%M:%S')} IST")
    print(f"[PH82-Daemon] Tick interval: 60 seconds | Config: {CONFIG_JSON}")

    # last_fired: {job_id: "YYYY-MM-DD HH:MM"} — prevents double-fire in same window
    last_fired: Dict[str, str] = {}

    # For 'daily' jobs: track which calendar day they last ran
    last_fired_date: Dict[str, str] = {}

    # Clean shutdown flag
    _shutdown = {"flag": False}

    def _handle_signal(signum, frame):
        print(f"\n[PH82-Daemon] Signal {signum} received — shutting down after current tick...")
        _shutdown["flag"] = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    config = load_config()
    state = load_state()
    if "jobs" not in state:
        state["jobs"] = {}

    while not _shutdown["flag"]:
        now = _now_ist()
        now_hhmm = now.strftime("%H:%M")
        today_str = now.strftime("%Y-%m-%d")

        # Reload config each tick (supports hot-reload of job config without restart)
        config = load_config()

        for job in config.get("jobs", []):
            if not job.get("enabled", False):
                continue

            job_id = job["id"]
            schedule_time = job.get("schedule_time", "daily")
            weekdays_only = job.get("weekdays_only", False)

            # Skip weekends for weekdays_only jobs
            if weekdays_only and not _is_weekday(now):
                continue

            should_fire = False

            if schedule_time.lower() == "daily":
                # 'daily' jobs fire once per calendar day (no specific time)
                fired_today = last_fired_date.get(job_id) == today_str
                if not fired_today:
                    should_fire = True
            else:
                # Time-specific job: check if we're inside the minute window
                if _time_matches(schedule_time, now, window_seconds=60):
                    # Check we haven't already fired in this minute window
                    fire_key = f"{today_str} {schedule_time}"
                    if last_fired.get(job_id) != fire_key:
                        should_fire = True
                        last_fired[job_id] = fire_key

            if should_fire:
                print(f"[PH82-Daemon] {now.strftime('%H:%M:%S')} IST — FIRING job: {job['name']} ({job_id})")
                result = run_job(job)
                state["jobs"][job_id] = result
                save_state(state)

                # Track daily-job firing date
                if schedule_time.lower() == "daily":
                    last_fired_date[job_id] = today_str

                # Log to CHANGE_LOG.md
                status = result.get("last_status", "UNKNOWN")
                _append_change_log(
                    f"[{now.strftime('%Y-%m-%d %H:%M')} IST] [Scheduler-Daemon] "
                    f"JOB FIRED: {job_id} — status={status}"
                )

                print(f"[PH82-Daemon] Job {job_id} done — status={status}")

        if _shutdown["flag"]:
            break

        time.sleep(60)

    # Cleanup
    print(f"[PH82-Daemon] Shutdown complete at {_now_ist().strftime('%Y-%m-%d %H:%M:%S')} IST")
    try:
        pid_file.unlink(missing_ok=True)
    except Exception:
        pass
    save_state(state)
```

### Changes to `main()` — add `--daemon` argument:

```python
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 82 - Job Scheduler")
    parser.add_argument("--list", action="store_true", help="List all jobs")
    parser.add_argument("--run-once", action="store_true", help="Run all enabled jobs immediately")
    parser.add_argument("--job-id", type=str, help="Run a single job by ID")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon: checks schedule_time every 60s, fires jobs in IST timezone",
    )

    args = parser.parse_args()

    try:
        if args.list:
            list_jobs()
        elif args.run_once:
            run_all_jobs()
        elif args.job_id:
            run_single_job(args.job_id)
        elif args.daemon:
            run_daemon()
        else:
            parser.print_help()

        return 0
    except Exception as e:
        print(f"\n[PH82] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
```

### Additional import to add at the top of the file:
```python
import os  # needed for os.getpid() in run_daemon
```
(Note: `os` is not currently imported in the file — must be added.)

### How to start the daemon:
```bash
# Start in background
python core/engine/system3_phase82_job_scheduler.py --daemon &

# Or via nohup for persistence
nohup python core/engine/system3_phase82_job_scheduler.py --daemon > /tmp/scheduler_daemon.log 2>&1 &

# Check if running
pgrep -f "system3_phase82_job_scheduler.*daemon"

# Graceful shutdown
kill $(cat state/scheduler_daemon.pid)
```

### IST Timezone Design Decision
The daemon uses `datetime.timezone(timedelta(hours=5, minutes=30))` — a fixed UTC+5:30 offset. This is correct for IST which does not observe DST. No `pytz` or `zoneinfo` import is needed (standard library only). The `schedule_time` values in the config (`08:00`, `09:15`, etc.) are all already expressed in IST, matching this offset.

### Handling `daily_status` job (no schedule_time field)
The `daily_status` job in the config has no `schedule_time` — it gets `"daily"` as the default in `run_daemon()`. This means it fires once per calendar day at the first tick after midnight IST. This is appropriate for a status-check job. If Claude wants it at a specific time, add `"schedule_time": "08:05"` to that job's config entry.

---

## Part 2: Test Suite Design

### Recommendation: Use `pytest` (not `unittest`)

**Rationale:**
- `pytest` is already in `requirements.txt` (confirmed).
- Existing test files (`tests/test_geni_master.py`) use `unittest.TestCase` classes, but `pytest` runs those transparently — no migration needed.
- `pytest` fixtures (`@pytest.fixture`, `tmp_path`, `monkeypatch`) are far superior to `setUp/tearDown` for mocking file I/O and datetime — exactly what these tests need.
- `pytest.raises()` is cleaner than `self.assertRaises()` for exception testing.
- New test files should be pure `pytest` style (plain functions, no class required).
- Convention to follow: place new tests in `tests/` root as `test_<module>.py`.

---

### Test File: `tests/test_bhavcopy_parser.py`

Tests `DataSourceManager._parse_bhavcopy()` in isolation using in-memory DataFrames. No network calls, no disk I/O.

#### Test Cases:

**TC-BP-1: UDiFF format — basic parse returns correct schema**
```
Input:  DataFrame with columns [TckrSymb, OptnTp, StrkPric, OpnIntrst, ChngInOpnIntrst,
                                 TtlTradgVol, ClsPric, XpryDt, FinInstrmTp]
        Row: TckrSymb=NIFTY, OptnTp=CE, StrkPric=23000, OpnIntrst=61295,
             ChngInOpnIntrst=60905, TtlTradgVol=1500, ClsPric=350.0,
             FinInstrmTp=IDO  ← this column intentionally NOT filtered on
Expected: result is not None; chain_df has columns [strike, option_type, oi,
          oi_change, prev_oi, volume, ltp, iv]; first row: strike=23000,
          option_type="CE", oi=61295, oi_change=60905, prev_oi=390
```

**TC-BP-2: UDiFF format — filter by symbol, NOT by FinInstrmTp**
```
Input:  DataFrame with 3 rows:
          Row 1: TckrSymb=NIFTY, OptnTp=CE, FinInstrmTp=IDO (index option)
          Row 2: TckrSymb=BANKNIFTY, OptnTp=CE, FinInstrmTp=IDO (different symbol)
          Row 3: TckrSymb=NIFTY, OptnTp=XX, FinInstrmTp=IDO (invalid option type)
Expected: only Row 1 survives (Row 2 wrong symbol, Row 3 invalid OptnTp)
          FinInstrmTp column is present but NOT used as a filter condition
```

**TC-BP-3: UDiFF format — both CE and PE returned, non-CE/PE rows dropped**
```
Input:  3 rows: TckrSymb=NIFTY with OptnTp in [CE, PE, "FUT"]
Expected: result has exactly 2 rows (CE + PE); "FUT" row excluded
```

**TC-BP-4: Old format (pre-Jul 2024) — SYMBOL + OPEN_INT columns**
```
Input:  DataFrame with columns [SYMBOL, OPTION_TYP, STRIKE_PR, OPEN_INT, CHG_IN_OI,
                                 CONTRACTS, CLOSE, INSTRUMENT]
        Row: SYMBOL=NIFTY, OPTION_TYP=PE, STRIKE_PR=22500, OPEN_INT=50000,
             CHG_IN_OI=-3000, CONTRACTS=800, CLOSE=120.5
Expected: result not None; oi=50000, oi_change=-3000, volume=800, ltp=120.5
          prev_oi = max(0, 50000 - (-3000)) = 53000
```

**TC-BP-5: Old format — negative oi_change (OI decreased)**
```
Input:  CHG_IN_OI = -3000, OPEN_INT = 50000
Expected: oi_change = -3000 (preserved as-is); prev_oi = 53000 (= oi - oi_change)
```

**TC-BP-6: Symbol mismatch — wrong symbol returns None**
```
Input:  TckrSymb=BANKNIFTY rows only; call _parse_bhavcopy(df, "NIFTY")
Expected: returns None (no rows pass symbol filter)
```

**TC-BP-7: Case-insensitive symbol matching**
```
Input:  TckrSymb="nifty" (lowercase); call _parse_bhavcopy(df, "NIFTY")
Expected: row is matched (case-insensitive comparison)
```

**TC-BP-8: oi_change returned directly from column, not computed from two sessions**
```
Input:  UDiFF row: OpnIntrst=100000, ChngInOpnIntrst=5000
Expected: chain_df["oi_change"].iloc[0] == 5000  ← comes directly from column,
          NOT computed by comparing two separate rows or sessions
```

**TC-BP-9: Unknown format (no TckrSymb, no SYMBOL) — returns None**
```
Input:  DataFrame with completely different column names [A, B, C]
Expected: returns None; logs warning "Unknown bhavcopy format"
```

**TC-BP-10: Empty DataFrame after symbol filter — returns None**
```
Input:  Valid UDiFF DataFrame but filtered result is empty after symbol+option filter
Expected: returns None (not an empty DataFrame)
```

---

### Test File: `tests/test_datasource_fallback.py`

Tests the full fallback chain in `DataSourceManager.fetch_option_chain()` using `unittest.mock.patch` and `monkeypatch`. No network calls.

#### Test Cases:

**TC-FB-1: NSE (P1) success — returns NSE data, bhavcopy never called**
```
Setup:  mock _try_dhan → None (guarded/skipped)
        mock _try_nse → (valid_df, 23000.0)
        mock _try_bhavcopy → raises AssertionError if called
Expected: fetch_option_chain("NIFTY") returns (valid_df, 23000.0)
          source tag in chain_df is "nse"
```

**TC-FB-2: NSE raises ConnectionError → bhavcopy (P3) is tried**
```
Setup:  mock _try_dhan → None
        mock _try_nse → raises ConnectionError
        mock _try_nsepython → raises ConnectionError  
        mock _try_bhavcopy → returns (bhavcopy_df, 0.0)
Expected: fetch_option_chain("NIFTY") returns (bhavcopy_df, 0.0)
          bhavcopy IS called after NSE fails
```

**TC-FB-3: NSE HTTP 503 (raise_for_status raises HTTPError) → fallback to bhavcopy**
```
Setup:  mock _try_nse → raises requests.HTTPError("503")
        mock _try_bhavcopy → returns (bhavcopy_df, 0.0)
Expected: bhavcopy source is tried; result is bhavcopy_df
```

**TC-FB-4: All network sources fail → synthetic fallback (P6)**
```
Setup:  _try_dhan, _try_nse, _try_nsepython → all return None or raise
        _try_bhavcopy, _try_jugaad → all return None (no local file)
        _try_yfinance → returns None
        _try_synthetic → returns (synthetic_df, 23000.0)
Expected: returns (synthetic_df, 23000.0); source tag is "synthetic"
```

**TC-FB-5: Synthetic result is NOT written to cache**
```
Setup:  All live sources fail; only synthetic succeeds
Expected: DataSourceManager._cache is empty after call
          (only non-synthetic results are cached per the live code logic)
```

**TC-FB-6: Empty DataFrame from NSE → continue to next source**
```
Setup:  _try_nse → returns (empty_df, 0.0) where empty_df.empty == True
        _try_bhavcopy → returns (valid_df, 0.0)
Expected: bhavcopy result is returned (empty result skipped)
```

**TC-FB-7: Cache hit within HEALTH_CACHE_MINUTES — source functions not called**
```
Setup:  Pre-populate _cache with (time.time(), valid_df, 23000.0)
        mock _try_nse → raises AssertionError if called
Expected: returns cached result without calling any source
```

---

### Test File: `tests/test_oi_cache.py`

Tests `nse_provider.load_oi_cache()` and `save_oi_cache()` using `tmp_path` pytest fixture for isolated file I/O.

#### Test Cases:

**TC-OI-1: Yesterday's cache — returns oi_data (normal case)**
```
Setup:  Write market_cache.json with cache_date = yesterday's date ISO string
        oi_data = {"NIFTY": 500000, "BANKNIFTY": 200000}
Expected: load_oi_cache() returns {"NIFTY": 500000, "BANKNIFTY": 200000}
```

**TC-OI-2: Same-day cache — returns {} (morning run guard)**
```
Setup:  Write market_cache.json with cache_date = today's date
        oi_data = {"NIFTY": 500000}
Expected: load_oi_cache() returns {}
          (guard prevents morning rank run from using today's validation save as prev_oi)
```

**TC-OI-3: Cache older than 3 days — returns {} (staleness guard)**
```
Setup:  Write market_cache.json with cache_date = 4 days ago
        oi_data = {"NIFTY": 500000}
Expected: load_oi_cache() returns {}
          (handles long weekends, market holidays)
```

**TC-OI-4: Cache exactly 3 days old — returns data (boundary: 3 days is still valid)**
```
Setup:  cache_date = 3 days ago
Expected: load_oi_cache() returns oi_data (age_days == 3, threshold is > 3)
```

**TC-OI-5: Cache exactly 4 days old — returns {} (boundary: 4 days is stale)**
```
Setup:  cache_date = 4 days ago
Expected: load_oi_cache() returns {} (age_days == 4 > MAX_OI_CACHE_AGE_DAYS=3)
```

**TC-OI-6: Missing file — returns {} (no crash)**
```
Setup:  MARKET_CACHE_FILE path points to a non-existent file
Expected: load_oi_cache() returns {} without raising exception
```

**TC-OI-7: Corrupt JSON — returns {} (no crash)**
```
Setup:  Write "NOT VALID JSON {{{" to MARKET_CACHE_FILE
Expected: load_oi_cache() returns {} without raising exception
```

**TC-OI-8: save_oi_cache() round-trip — data survives save→load**
```
Setup:  Call save_oi_cache({"NIFTY": 123456, "BANKNIFTY": 654321})
        Then call load_oi_cache() (with mocked date = tomorrow, so cache_date=today = yesterday from mock's perspective)
Expected: data round-trips correctly; cache_date field is set to today's ISO date
Note: This test must mock date.today() to be tomorrow after the save to simulate
      the "next morning" read scenario
```

**TC-OI-9: is_expiry_day() — Thursday returns True**
```
Setup:  Mock date.today() to return a Thursday (weekday() == 3)
Expected: is_expiry_day() returns True
```

**TC-OI-10: is_expiry_day() — Monday through Wednesday, Friday return False**
```
Setup:  Mock date.today() to return each of Mon, Tue, Wed, Fri
Expected: is_expiry_day() returns False for all four
```

**TC-OI-11: Missing cache_date field — returns oi_data (backward compat)**
```
Setup:  Write market_cache.json with oi_data but NO cache_date field
Expected: load_oi_cache() returns oi_data (no date → no staleness check → safe to use)
```

---

## Implementation Notes for Claude

When Claude implements the tests:

1. **Isolation of MARKET_CACHE_FILE**: `nse_provider.MARKET_CACHE_FILE` is a module-level constant. Tests must monkeypatch it to a `tmp_path` location to avoid writing to the real `state/market_cache.json`.
   ```python
   @pytest.fixture(autouse=True)
   def isolate_cache(tmp_path, monkeypatch):
       cache_file = str(tmp_path / "market_cache.json")
       monkeypatch.setattr("core.data.nse_provider.MARKET_CACHE_FILE", cache_file)
       return cache_file
   ```

2. **DataSourceManager isolation**: The `_try_*` methods are instance methods, so they can be patched via `monkeypatch.setattr(manager_instance, "_try_nse", mock_fn)` or via `unittest.mock.patch.object`.

3. **datetime mocking**: `load_oi_cache()` uses `from datetime import datetime, date` internally. To mock `date.today()`, patch `core.data.nse_provider.date` or use `freezegun` if available. Since we want stdlib-only, prefer `monkeypatch.setattr("core.data.nse_provider.date", FakeDateClass)` with a minimal fake class implementing `.today()` and `.strptime()` delegation.

4. **Test runner command**:
   ```bash
   pytest tests/test_bhavcopy_parser.py tests/test_datasource_fallback.py tests/test_oi_cache.py -v
   ```

5. **Total test count**: 10 + 7 + 11 = **28 focused tests** across 3 files.

---

## Success Metrics

- Daemon fires each job within ±60 seconds of its IST schedule_time on a weekday
- Daemon correctly skips all 7 jobs on Saturday and Sunday
- Daemon does not double-fire any job in the same minute window (verified via last_fired tracking)
- `daily_status` job fires exactly once per calendar day regardless of time
- All 28 test cases pass with `pytest -v` (no network access needed)
- `pytest tests/test_oi_cache.py -v` runs in under 1 second (pure unit tests)
- No new pip dependencies introduced by any of the above

---

## Files to be Modified/Created by Claude

1. **MODIFY:** `core/engine/system3_phase82_job_scheduler.py`
   - Add `import os`, `import time`, `import signal` at top
   - Add `from datetime import timezone, timedelta` extension to existing datetime import
   - Add `_IST`, `_now_ist()`, `_time_matches()`, `_is_weekday()`, `_append_change_log()`, `run_daemon()` functions
   - Add `--daemon` argument to `main()`

2. **CREATE:** `tests/test_bhavcopy_parser.py` (10 test cases)

3. **CREATE:** `tests/test_datasource_fallback.py` (7 test cases)

4. **CREATE:** `tests/test_oi_cache.py` (11 test cases)

---

## Gemini Cross-Verification Request

Gemini: please verify independently:
1. The IST timezone approach (stdlib `timezone(timedelta(hours=5,30))` vs pytz/zoneinfo)
2. Whether `_time_matches()` using absolute seconds is correct vs comparing hour:minute strings directly
3. Whether the `daily_status` job (no `schedule_time`) fires at a sensible time with the `daily` treatment
4. Whether 28 test cases are sufficient or if additional edge cases exist for the bhavcopy parser
5. Whether any test in TC-FB or TC-OI requires pandas to be installed (pandas IS in requirements.txt — but confirm)

Respond in CHANGE_LOG.md with AGREE / DISAGREE / PARTIAL.
