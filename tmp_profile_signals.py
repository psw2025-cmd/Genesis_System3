import pandas as pd, json, pathlib
root = pathlib.Path('c:/Genesis_System3')
files = {
    'angel_index_ai_signals.csv': root / 'storage/live/angel_index_ai_signals.csv',
    'angel_index_ai_signals_curated.csv': root / 'storage/live/angel_index_ai_signals_curated.csv',
    'angel_index_ai_signals_with_forward.csv': root / 'storage/live/angel_index_ai_signals_with_forward.csv',
    'angel_virtual_orders.csv': root / 'storage/live/angel_virtual_orders.csv',
    'angel_index_ai_pnl_log.csv': root / 'storage/live/angel_index_ai_pnl_log.csv',
}

def profile(p: pathlib.Path):
    if not p.exists():
        return {'exists': False}
    try:
        df = pd.read_csv(p)
    except Exception as e:
        return {'exists': True, 'error': str(e)}
    return {
        'exists': True,
        'rows': len(df),
        'n_cols': len(df.columns),
        'cols': list(df.columns),
    }

def main():
    out = {k: profile(v) for k, v in files.items()}
    mdr = root / 'storage/live/diagnostics/model_drift_report.csv'
    out['model_drift_report.csv'] = {'exists': mdr.exists()}
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
