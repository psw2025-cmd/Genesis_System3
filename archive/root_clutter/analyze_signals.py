import pandas as pd

df = pd.read_csv('storage/live/angel_index_ai_signals.csv')

print("="*60)
print("SIGNAL FILE ANALYSIS")
print("="*60)

print(f"\nTotal rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\n[SIGNAL DISTRIBUTION]")
print(df['signal'].value_counts())

print("\n[FINAL SCORE STATS]")
print(df['final_score'].describe())

print("\n[ENTRY CONFIDENCE STATS]")
print(df['entry_confidence'].describe())

print("\n[FILTERING ANALYSIS]")
high_score = df[df['final_score'].abs() > 0.5]
print(f"Signals with |final_score| > 0.5: {len(high_score)}")

high_conf = df[df['entry_confidence'] > 0.4]
print(f"Signals with entry_confidence > 0.4: {len(high_conf)}")

not_hold = df[df['signal'] != 'HOLD']
print(f"Signals that are not HOLD: {len(not_hold)}")

high_quality = df[
    (df['final_score'].abs() > 0.5) &
    (df['entry_confidence'] > 0.4) &
    (df['signal'] != 'HOLD')
]
print(f"High quality signals (all criteria): {len(high_quality)}")

print("\n[RECOMMENDATION]")
if len(high_quality) < 20:
    print("ISSUE: Most signals have low scores and filtered out.")
    print("The signal generation likely needs recalibration.")
    print("Current script uses RANDOM data - need REAL market data!")
