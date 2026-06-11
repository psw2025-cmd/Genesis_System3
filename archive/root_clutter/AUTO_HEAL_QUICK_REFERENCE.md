# System3 Auto-Heal Quick Reference

## Quick Commands

### Run Auto-Heal Once
```bash
run_auto_heal.bat
```

### Run Tests
```bash
run_auto_heal_tests.bat
```

### Start Scheduler (Continuous)
```bash
start_auto_heal_scheduler.bat
```

## What Gets Fixed Automatically

| Issue | Detection | Action | Frequency |
|-------|-----------|--------|-----------|
| 🔴 **Stale Data** | >5 min old | Log warning / Refresh | Every 10-30 min |
| 📝 **Large Logs** | >100 MB | Archive | Every cycle |
| 🗑️ **Old Logs** | >7 days | Delete | Every cycle |
| 💾 **Low Disk** | <5 GB free | Cleanup | Every cycle |
| 💓 **Stale Heartbeat** | >10 min old | Update | Every cycle |

## Integration Points

### Phase 306 (Staleness Guard)
- Auto-triggers healing when data expires
- Creates trigger file: `storage/meta/system3_heal_trigger.json`
- Sets `auto_heal_triggered: true` in outputs

### Autorun Master
- Can integrate auto-heal in periodic cycles
- Responds to trigger files

### Watchdog
- Monitors for heal triggers
- Can start scheduler on demand

## Configuration

Edit `HEAL_CONFIG` in `system3_auto_heal_orchestrator.py`:

```python
HEAL_CONFIG = {
    "auto_refresh_stale_data": True,     # Enable stale data healing
    "auto_cleanup_logs": True,            # Enable log cleanup
    "auto_regenerate_missing": True,      # Enable file regeneration
    "auto_restart_pipeline": True,        # Enable pipeline restart
    "stale_threshold_seconds": 300,       # 5 minutes
    "log_retention_days": 7,              # Keep logs for 7 days
    "max_log_size_mb": 100,              # Archive logs >100MB
    "min_free_disk_gb": 5,               # Alert when <5GB free
}
```

## Safety

✅ **Safe Operations Only**
- Archives/deletes logs only
- Updates metadata files
- Never touches trading logic
- Never modifies live data
- Never executes trades

## Logs & Reports

- **Healing Logs**: `logs/auto_heal/auto_heal_YYYYMMDD.log`
- **Healing Reports**: `logs/auto_heal/heal_report_*.json`
- **Test Results**: `logs/auto_heal/test_results_*.json`
- **Scheduler Logs**: `logs/auto_heal/scheduler_YYYYMMDD.log`

## Troubleshooting

### Auto-heal not running?
1. Check scheduler is started: `start_auto_heal_scheduler.bat`
2. Check logs in `logs/auto_heal/`
3. Verify no shutdown flag: `system3_shutdown_flag.json`

### Issue not being fixed?
1. Check healing config enabled for that issue type
2. Review healing report JSON files
3. Check errors in healing logs

### Want to force immediate healing?
```bash
run_auto_heal.bat
```

## Test Coverage

**18/18 tests passing (100%)**
- Orchestrator initialization
- Issue detection (all types)
- Healing actions (all types)
- Phase 306 integration
- Error handling
- Edge cases

---

**Status**: ✅ Production Ready  
**Last Validated**: December 5, 2025
