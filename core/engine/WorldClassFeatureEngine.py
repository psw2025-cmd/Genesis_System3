"""
World-Class Feature Engineering (v6.0) - BIG ALPHA
Sets a high 0.40% bar to ensure profit after institutional friction.
"""
import pandas as pd
import numpy as np

class WorldClassFeatureEngine:
    def engineer_features(self, df: pd.DataFrame, underlying: str) -> pd.DataFrame:
        df = df.copy()
        
        # 1. Force numeric
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['Close'])
        df = df.sort_index()

        # 2. STATIONARY TRANSFORMATIONS
        for period in [10, 20, 50]:
            sma = df['Close'].rolling(period).mean()
            std = df['Close'].rolling(period).std()
            df[f'norm_price_{period}'] = (df['Close'] - sma) / (sma + 1e-9)
            df[f'z_score_{period}'] = (df['Close'] - sma) / (std + 1e-9)
            df[f'log_ret_{period}'] = np.log(df['Close'] / df['Close'].shift(period))

        # 3. TIME-OF-DAY ALPHA
        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek

        # 4. TECHNICALS
        for w in [5, 14, 50]:
            df[f'rsi_{w}'] = self._calc_rsi(df['Close'], w)
        
        df['atr_rel'] = self._calc_atr(df, 14) / (df['Close'] + 1e-9)
        df['volu_shock'] = df['Volume'] / (df['Volume'].rolling(20).mean() + 1e-9)

        # 5. THE BIG ALPHA TARGET (ADAPTIVE ALPHA v7.0)
        df['target_1h'] = df['Close'].shift(-1) / df['Close'] - 1
        
        rolling_std = df['Close'].pct_change().rolling(20).std()
        df['adaptive_bar'] = (rolling_std * 1.5).clip(lower=0.0025)
        df['label_buy'] = (df['target_1h'] > df['adaptive_bar']).astype(int)
        
        return df.dropna()

    def _calc_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    def _calc_atr(self, df, period):
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()
