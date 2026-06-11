import pandas as pd
import numpy as np

def analyze_csv_consistency(file_path):
    print(f"Loading CSV file: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    issues = []

    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        issues.append(f"Missing values found:\n{missing[missing > 0]}")

    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append(f"Duplicate rows: {duplicates}")

    # Check data types
    print("\nData types:")
    print(df.dtypes)

    # Check for invalid probabilities (should be between 0 and 1)
    prob_cols = ['prob_BUY_CE', 'prob_BUY_PE', 'prob_HOLD', 'ml_probability', 'pred_proba']
    for col in prob_cols:
        if col in df.columns:
            try:
                # Convert to numeric, coercing errors to NaN
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                invalid_probs = numeric_col[(numeric_col < 0) | (numeric_col > 1)]
                if not invalid_probs.empty:
                    issues.append(f"Invalid probabilities in {col}: {len(invalid_probs)} rows")
            except Exception as e:
                issues.append(f"Error checking probabilities in {col}: {str(e)}")

    # Check for negative prices
    price_cols = ['spot', 'ltp', 'entry_price', 'stop_loss', 'target_price']
    for col in price_cols:
        if col in df.columns:
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                negative_prices = numeric_col[numeric_col < 0]
                if not negative_prices.empty:
                    issues.append(f"Negative prices in {col}: {len(negative_prices)} rows")
            except Exception as e:
                issues.append(f"Error checking negative prices in {col}: {str(e)}")

    # Check signal consistency
    if 'signal' in df.columns and 'prob_BUY_CE' in df.columns and 'prob_BUY_PE' in df.columns:
        buy_ce_signals = df[df['signal'] == 'BUY_CE']
        try:
            prob_ce_numeric = pd.to_numeric(buy_ce_signals['prob_BUY_CE'], errors='coerce')
            low_prob_ce = prob_ce_numeric[prob_ce_numeric < 0.5]
            if not low_prob_ce.empty:
                issues.append(f"BUY_CE signals with low prob_BUY_CE (<0.5): {len(low_prob_ce)} rows")
        except Exception as e:
            issues.append(f"Error checking BUY_CE signal consistency: {str(e)}")

        buy_pe_signals = df[df['signal'] == 'BUY_PE']
        try:
            prob_pe_numeric = pd.to_numeric(buy_pe_signals['prob_BUY_PE'], errors='coerce')
            low_prob_pe = prob_pe_numeric[prob_pe_numeric < 0.5]
            if not low_prob_pe.empty:
                issues.append(f"BUY_PE signals with low prob_BUY_PE (<0.5): {len(low_prob_pe)} rows")
        except Exception as e:
            issues.append(f"Error checking BUY_PE signal consistency: {str(e)}")

    # Check forward returns alignment
    fwd_cols = ['fwd_ret_1', 'fwd_ret_2', 'fwd_ret_3', 'fwd_ret_5', 'fwd_ret_10', 'fwd_ret_15']
    for col in fwd_cols:
        if col in df.columns:
            invalid_fwd = df[df[col].isnull() & df['signal'].notnull()]
            if not invalid_fwd.empty:
                issues.append(f"Signals without forward returns in {col}: {len(invalid_fwd)} rows")

    # Check IV values
    iv_cols = ['iv_estimate', 'iv']
    for col in iv_cols:
        if col in df.columns:
            try:
                numeric_iv = pd.to_numeric(df[col], errors='coerce')
                negative_iv = numeric_iv[numeric_iv < 0]
                if not negative_iv.empty:
                    issues.append(f"Negative IV in {col}: {len(negative_iv)} rows")
            except Exception as e:
                issues.append(f"Error checking IV values in {col}: {str(e)}")

    # Check Greeks
    greek_cols = ['delta', 'gamma', 'theta', 'vega', 'rho']
    for col in greek_cols:
        if col in df.columns:
            try:
                numeric_greeks = pd.to_numeric(df[col], errors='coerce')
                extreme_greeks = numeric_greeks[np.abs(numeric_greeks) > 10]
                if not extreme_greeks.empty:
                    issues.append(f"Extreme values in {col} (>10 or <-10): {len(extreme_greeks)} rows")
            except Exception as e:
                issues.append(f"Error checking extreme values in {col}: {str(e)}")

    # Check timestamps
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            future_ts = df[df['timestamp'] > pd.Timestamp.now()]
            if not future_ts.empty:
                issues.append(f"Future timestamps: {len(future_ts)} rows")
        except:
            issues.append("Timestamp column has invalid formats")

    if issues:
        print("\nConsistency Issues Found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\nNo major consistency issues found.")

    return issues

if __name__ == "__main__":
    file_path = "storage/live/angel_index_ai_signals_with_forward.csv"
    analyze_csv_consistency(file_path)
