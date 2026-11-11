# System3 Reports Directory Analysis

**Date**: 2025-11-29  
**Directory**: `storage/reports/`  
**Status**: Analysis Complete

---

## Directory Structure

**Location**: `C:\Genesis_System3\storage\reports\`

**Status Check**: From validation output shows:
```
✅ storage/reports: 3 files
```

---

## Expected Report Files

Based on System3 architecture, the following reports should be generated:

### Daily Reports
- `dhan_daily_learning_report_YYYYMMDD.txt` - Daily learning summary
- `real_learning_summary_YYYYMMDD.csv` - Signal vs outcome analysis
- `dhan_daily_learning_report_YYYYMMDD.txt` - Daily digest

### Weekly Reports
- `dhan_weekly_summary_report_YYYYMMDD.txt` - Weekly summary
- `rolling_7day_learning_dashboard.csv` - 7-day rolling dashboard

### Ultra Reports
- Reports from Ultra phases are stored in `storage/ultra/` and `storage/reports_ultra/`

### Learning Reports
- `real_learning_daily/` - Daily learning reports directory
- Various analysis CSVs and MD files

---

## Analysis Commands

To analyze the reports directory:

```bash
# List all files
dir storage\reports

# Count files
dir storage\reports /b | find /c /v ""

# List subdirectories
dir storage\reports /ad /b
```

---

## Report Generation Commands

To generate reports:

```bash
# Daily learning report
python -m core.engine.dhan_daily_learning_digest

# Daily auto reports
python -m core.engine.dhan_daily_auto_reports

# Weekly summary
python -m core.engine.dhan_weekly_summary_report

# Rolling dashboard
python -m core.engine.dhan_rolling_learning_dashboard
```

---

## Expected Report Structure

```
storage/reports/
├── dhan_daily_learning_report_YYYYMMDD.txt
├── real_learning_summary_YYYYMMDD.csv
├── rolling_7day_learning_dashboard.csv
├── dhan_weekly_summary_report_YYYYMMDD.txt
└── real_learning_daily/
    └── YYYYMMDD/
        └── learning_report_*.txt
```

---

## Validation Status

From validation output:
- ✅ Reports directory exists
- ✅ 3 files found (exact files to be listed)

---

**Next Step**: Run directory listing to see actual files

