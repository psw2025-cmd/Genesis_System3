import pandas as pd
import numpy as np

# Load the CSV data
df = pd.read_csv('storage/live/forward/phase221_forward_returns.csv')

print("Data Overview:")
print(f"Shape: {df.shape}")
print(f"Columns: {len(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())

print("\nData Types:")
print(df.dtypes)

print("\nSummary Statistics for Numeric Columns:")
numeric_cols = df.select_dtypes(include=[np.number]).columns
print(df[numeric_cols].describe())

print("\nPrediction Label Distribution:")
print(df['pred_label'].value_counts())

print("\nAverage Forward Returns by Prediction Label:")
ret_cols = ['fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5', 'fwd_ret_10', 'fwd_ret_15']
for ret_col in ret_cols:
    if ret_col in df.columns:
        print(f"\n{ret_col}:")
        print(df.groupby('pred_label')[ret_col].mean())

print("\nSignal Distribution:")
if 'signal' in df.columns:
    print(df['signal'].value_counts())

print("\nAverage Forward Returns by Signal:")
if 'signal' in df.columns:
    for ret_col in ['fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5']:
        if ret_col in df.columns:
            print(f"\n{ret_col} by signal:")
            print(df.groupby('signal')[ret_col].mean())

print("\nCorrelation between Prediction Confidence and Forward Returns:")
if 'pred_confidence' in df.columns and 'fwd_ret_1' in df.columns:
    corr = df[['pred_confidence', 'fwd_ret_1']].corr()
    print(corr)

print("\nTop Correlations with fwd_ret_1:")
if 'fwd_ret_1' in df.columns:
    numeric_df = df.select_dtypes(include=[np.number])
    correlations = numeric_df.corr()['fwd_ret_1'].sort_values(ascending=False)
    print(correlations.head(10))

print("\nVolatility Regime Distribution:")
if 'volatility_regime' in df.columns:
    print(df['volatility_regime'].value_counts())

print("\nAverage Returns by Volatility Regime:")
if 'volatility_regime' in df.columns and 'fwd_ret_1' in df.columns:
    print(df.groupby('volatility_regime')['fwd_ret_1'].mean())

print("\nUnderlying Distribution:")
print(df['underlying'].value_counts())

print("\nAverage Returns by Underlying:")
for ret_col in ['fwd_ret_1', 'fwd_ret_3']:
    if ret_col in df.columns:
        print(f"\n{ret_col} by underlying:")
        print(df.groupby('underlying')[ret_col].mean())
