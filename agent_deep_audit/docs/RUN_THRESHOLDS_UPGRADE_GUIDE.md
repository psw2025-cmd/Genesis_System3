# Run Thresholds Upgrade - Quick Guide

## Single Command Execution

Run the complete thresholds upgrade workflow with a single batch file:

```bash
run_thresholds_upgrade.bat
```

## What It Does

The batch file runs all steps in sequence:

1. **Phase 221**: Generates forward returns from curated CSV
2. **Phase 222**: Computes EV tables by underlying and score bins
3. **Threshold Proposer**: Automatically generates thresholds from EV tables
4. **Test Mode**: Validates thresholds (both auto and live)
5. **Summary**: Shows generated files and next steps

## Output Files

After running, check these files:

- `storage/live/dhan_index_ai_signals_with_forward.csv` - Enriched signals
- `logs/research/system3_signal_edge_report.md` - EV tables
- `storage/meta/system3_live_thresholds.json` - Live thresholds
- `docs/system3_thresholds_comparison.md` - Threshold comparison

## Manual Steps (if needed)

If you prefer to run steps individually:

```bash
# Step 1: Forward Returns
python core/engine/system3_phase221_forward_returns.py

# Step 2: EV Tables
python core/engine/system3_phase222_signal_edge.py

# Step 3: Threshold Proposer
python core/engine/system3_threshold_proposer.py

# Step 4: Test Mode (auto-thresholds)
python system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds

# Step 4: Test Mode (live-thresholds)
python system3_signal_test_mode.py --lookback-snapshots 200 --use-live-thresholds
```

## Monitoring

After running the upgrade:

1. The signal engine will automatically use new thresholds from `system3_live_thresholds.json`
2. Monitor signal generation in logs
3. Check signal counts (should see more BUY/SELL signals)
4. Review EV tables periodically to adjust thresholds

## Troubleshooting

- **Python not found**: Activate venv first (`venv\Scripts\activate`)
- **CSV not found**: Run signal generation first to create signals CSV
- **No EV tables**: Check if forward returns were computed (Phase 221)
- **Thresholds not loading**: Check JSON file format in `storage/meta/`

