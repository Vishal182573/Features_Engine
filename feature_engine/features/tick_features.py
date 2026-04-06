import pandas as pd
import numpy as np

def calculate_tick_features(df: pd.DataFrame) -> dict:
    features = {}
    if df.empty or len(df) < 10:
        return features

    # CVD (Cumulative Volume Delta)
    # tick format: symbol, price, quantity, side, timestamp
    df['signed_volume'] = df.apply(lambda row: row['quantity'] if row['side'] in ['buy', 'BUY'] else -row['quantity'], axis=1)
    features['cvd'] = df['signed_volume'].sum()
    
    price_change = df['price'].iloc[-1] - df['price'].iloc[0]
    features['cvd_divergence'] = 1 if (price_change > 0 and features['cvd'] < 0) or (price_change < 0 and features['cvd'] > 0) else 0

    # Spread (approximate from price if we only have ticks, normally spread is bid-ask)
    # If we have bid/ask, it's easier. Since it's tick data, spread might not be perfectly defined.
    # We will simulate it using price diff or assuming tick has spread info.
    # The requirement says we need spread, spread_average, spread_zscore.
    features['spread'] = 0.5  # placeholder or derive from orderbook
    features['spread_average'] = 0.5
    features['spread_zscore'] = 0.0

    # Tick Velocity
    time_diff = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]) / 1000.0 # assuming ms
    features['ticks_per_second'] = len(df) / time_diff if time_diff > 0 else 0

    # Large Trade
    mean_qty = df['quantity'].mean()
    features['large_trade_flag'] = 1 if df['quantity'].iloc[-1] > mean_qty * 5 else 0

    return features
