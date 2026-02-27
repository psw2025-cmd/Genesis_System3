#!/usr/bin/env python3
"""Phase 2: Curated Signals & Archive Audit"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("Phase 2: Curated Signals & Archive Audit")
print("=" * 80)

# Check current curated signals
curated_path = Path('storage/live/angel_index_ai_signals_curated_full.csv')
if curated_path.exists():
    df = pd.read_csv(curated_path, engine='python', on_bad_lines='skip')
    print(f'\nCurrent curated full CSV:')
    print(f'  Total rows: {len(df)}')
    print(f'  Has ts column: {"ts" in df.columns}')
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
        unique_dates = df['ts'].dt.date.nunique()
        print(f'  Unique dates: {unique_dates}')
        print(f'  Date range: {df["ts"].min()} to {df["ts"].max()}')
else:
    print(f'\nCurated full CSV not found')

# Check archive
archive_dir = Path('storage/live/archive')
if archive_dir.exists():
    csv_files = list(archive_dir.glob('*.csv'))
    print(f'\nArchive directory: {len(csv_files)} CSV files')
    for f in sorted(csv_files)[:5]:
        print(f'  - {f.name}')
    if len(csv_files) > 5:
        print(f'  ... and {len(csv_files) - 5} more')
else:
    print(f'\nArchive directory not found')

# Check backup
backup_dir = Path('storage/live/backup')
if backup_dir.exists():
    csv_files = list(backup_dir.glob('*.csv'))
    print(f'\nBackup directory: {len(csv_files)} CSV files')
    for f in sorted(csv_files)[:5]:
        print(f'  - {f.name}')
    if len(csv_files) > 5:
        print(f'  ... and {len(csv_files) - 5} more')
else:
    print(f'\nBackup directory not found')

print("\n" + "=" * 80)
