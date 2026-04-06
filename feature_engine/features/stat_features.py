import pandas as pd
import numpy as np
import scipy.stats as stats

def calculate_stat_features(df: pd.DataFrame, asset_data_dict: dict = None) -> dict:
    features = {}
    if df.empty or len(df) < 20:
        return features

    # Returns
    close = df['close']
    features['return_1b'] = (close.iloc[-1] / close.iloc[-2] - 1) if len(close) > 1 else 0
    features['return_5b'] = (close.iloc[-1] / close.iloc[-6] - 1) if len(close) > 5 else 0
    features['return_20b'] = (close.iloc[-1] / close.iloc[-21] - 1) if len(close) > 20 else 0
    features['log_return'] = np.log(close.iloc[-1] / close.iloc[-2]) if len(close) > 1 else 0

    # Z Score
    rolling_mean = close.rolling(20).mean().iloc[-1]
    rolling_std = close.rolling(20).std().iloc[-1]
    features['zscore_price'] = (close.iloc[-1] - rolling_mean) / rolling_std if rolling_std else 0

    # Candle Features
    body_size = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    upper_wick = df['high'].iloc[-1] - max(df['close'].iloc[-1], df['open'].iloc[-1])
    lower_wick = min(df['close'].iloc[-1], df['open'].iloc[-1]) - df['low'].iloc[-1]
    total_range = df['high'].iloc[-1] - df['low'].iloc[-1]

    features['body_size'] = body_size
    features['upper_wick'] = upper_wick
    features['lower_wick'] = lower_wick
    features['doji_flag'] = 1 if body_size <= (total_range * 0.1) else 0

    # Cross Asset
    # Assuming asset_data_dict has other assets' close prices as lists or series
    if asset_data_dict and 'BTCUSDT' in asset_data_dict and 'ETHUSDT' in asset_data_dict:
        try:
            btc_series = pd.Series(asset_data_dict['BTCUSDT'][-20:])
            eth_series = pd.Series(asset_data_dict['ETHUSDT'][-20:])
            if len(btc_series) == 20 and len(eth_series) == 20:
                corr = btc_series.corr(eth_series)
                features['btc_eth_corr'] = corr
                features['corr_breakdown'] = 1 if corr < 0.5 else 0
        except Exception:
            pass

    return features
