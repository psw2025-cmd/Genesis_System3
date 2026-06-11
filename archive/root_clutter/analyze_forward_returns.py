import pandas as pd

# Load the CSV file
df = pd.read_csv('storage/live/forward/phase221_forward_returns.csv')

# Basic info
print("Dataset shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nData types:")
print(df.dtypes)

# Summary statistics for numerical columns
print("\nSummary statistics:")
print(df.describe())

# Check for missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Unique values in categorical columns
categorical_cols = [
    'underlying', 'index_exch', 'opt_exch', 'side',
    'pred_label', 'signal', 'reconciled_label', 'data_source'
]
for col in categorical_cols:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].value_counts())

# Analyze prediction accuracy
if 'pred_label' in df.columns and 'reconciled_label' in df.columns:
    accuracy = (df['pred_label'] == df['reconciled_label']).mean()
    print(f"\nPrediction accuracy: {accuracy:.4f}")

# Analyze signal performance
if 'signal' in df.columns and 'fwd_ret_1' in df.columns:
    signal_performance = df.groupby('signal')['fwd_ret_1'].agg(['mean', 'std', 'count'])
    print("\nSignal performance (fwd_ret_1):")
    print(signal_performance)

# Analyze moneyness distribution
if 'moneyness' in df.columns:
    print("\nMoneyness distribution:")
    print(df['moneyness'].describe())

# Analyze forward returns
fwd_cols = [col for col in df.columns if col.startswith('fwd_ret')]
if fwd_cols:
    print("\nForward returns summary:")
    print(df[fwd_cols].describe())

# Correlation with final_score
if 'final_score' in df.columns and 'fwd_ret_1' in df.columns:
    corr = df['final_score'].corr(df['fwd_ret_1'])
    print(f"\nCorrelation between final_score and fwd_ret_1: "
          f"{corr:.4f}")

# Top performing signals
if 'signal' in df.columns and 'fwd_ret_1' in df.columns:
    top_signals = df.groupby('signal')['fwd_ret_1'].mean().sort_values(ascending=False)
    print("\nAverage fwd_ret_1 by signal (sorted):")
    print(top_signals)

# Check for outliers in returns
if 'fwd_ret_1' in df.columns:
    print("\nFwd_ret_1 outliers (IQR method):")
    Q1 = df['fwd_ret_1'].quantile(0.25)
    Q3 = df['fwd_ret_1'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df['fwd_ret_1'] < lower_bound) |
                  (df['fwd_ret_1'] > upper_bound)]
    print(f"Number of outliers: {len(outliers)}")
    print(f"Outlier percentage: {len(outliers)/len(df)*100:.2f}%")
