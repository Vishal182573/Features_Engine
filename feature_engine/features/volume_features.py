import pandas as pd
import pandas_ta as ta

def calculate_volume_features(df: pd.DataFrame) -> dict:
    features = {}
    if df.empty or len(df) < 50:
        return features
    
    # VWAP (simplified as rolling typical price * volume / volume)
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    features['vwap'] = (typical_price * df['volume']).rolling(window=20).sum() / df['volume'].rolling(window=20).sum()
    features['vwap'] = features['vwap'].iloc[-1]
    features['vwap_deviation'] = df['close'].iloc[-1] - features['vwap']
    features['vwap_bands_upper'] = features['vwap'] * 1.02
    features['vwap_bands_lower'] = features['vwap'] * 0.98

    # VWMA
    vwma20 = df.ta.vwma(length=20)
    if vwma20 is not None and not vwma20.empty:
        features['vwma20'] = vwma20.iloc[-1]
        features['vwma_vs_sma'] = features['vwma20'] - df.ta.sma(length=20).iloc[-1]
    
    # OBV
    obv = df.ta.obv()
    if obv is not None and not obv.empty:
        features['obv'] = obv.iloc[-1]
        features['obv_slope'] = obv.iloc[-1] - obv.iloc[-2]
        features['obv_divergence'] = 1 if (df['close'].iloc[-1] > df['close'].iloc[-2] and features['obv_slope'] < 0) else 0

    # Volume Ratio
    avg_vol = df['volume'].rolling(20).mean().iloc[-1]
    features['vol_ratio'] = df['volume'].iloc[-1] / avg_vol if avg_vol else 1
    features['vol_spike'] = 1 if features['vol_ratio'] > 3 else 0
    features['thin_market'] = 1 if features['vol_ratio'] < 0.3 else 0

    return features
