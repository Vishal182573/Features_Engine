import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_trend_features(df: pd.DataFrame) -> dict:
    features = {}
    if df.empty or len(df) < 50:
        return features

    # ADX
    adx = df.ta.adx(length=14)
    if adx is not None and not adx.empty:
        features['adx14'] = adx['ADX_14'].iloc[-1]
        features['plus_di'] = adx['DMP_14'].iloc[-1]
        features['minus_di'] = adx['DMN_14'].iloc[-1]
        features['adx_slope'] = adx['ADX_14'].iloc[-1] - adx['ADX_14'].iloc[-2]

    # Market Regime
    # Simple heuristic
    # TRENDING_UP, TRENDING_DOWN, RANGING, HIGH_VOLATILITY
    
    regime = "RANGING"
    if 'adx14' in features and features['adx14'] > 25:
        if features['plus_di'] > features['minus_di']:
            regime = "TRENDING_UP"
        else:
            regime = "TRENDING_DOWN"
    
    # Adding HV check based on ATR or simple std
    returns_std = np.log(df['close'] / df['close'].shift(1)).std()
    if returns_std > 0.05: # Arbitrary high vol threshold
        regime = "HIGH_VOLATILITY"

    features['market_regime'] = regime

    return features
