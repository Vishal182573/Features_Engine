import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_volatility_features(df: pd.DataFrame) -> dict:
    features = {}
    if df.empty or len(df) < 50:
        return features

    # ATR
    atr14 = df.ta.atr(length=14)
    if atr14 is not None and not atr14.empty:
        features['atr14'] = atr14.iloc[-1]
        features['atr_percent'] = (features['atr14'] / df['close'].iloc[-1]) * 100
        atr_rank = atr14.rank(pct=True).iloc[-1]
        features['atr_percentile'] = atr_rank

    # Historical Volatility
    returns = np.log(df['close'] / df['close'].shift(1))
    features['rolling_std'] = returns.rolling(window=20).std().iloc[-1]
    features['log_return_std'] = returns.std()
    # Assuming daily or adjust for timeframe
    features['annualized_vol'] = features['rolling_std'] * np.sqrt(365*24*60) # roughly 1m bars in year

    # Keltner Channel
    kc = df.ta.kc(length=20, scalar=2)
    if kc is not None and not kc.empty:
        features['kc_lower'] = kc['KCLe_20_2'].iloc[-1]
        features['kc_middle'] = kc['KCBe_20_2'].iloc[-1]
        features['kc_upper'] = kc['KCUe_20_2'].iloc[-1]

    return features
