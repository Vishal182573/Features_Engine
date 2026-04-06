import pandas as pd
import pandas_ta as ta

def calculate_price_features(df: pd.DataFrame) -> dict:
    features = {}
    if df.empty or len(df) < 200:
        return features

    # EMA Set
    features['ema9'] = df.ta.ema(length=9).iloc[-1]
    features['ema21'] = df.ta.ema(length=21).iloc[-1]
    features['ema50'] = df.ta.ema(length=50).iloc[-1]
    features['ema100'] = df.ta.ema(length=100).iloc[-1]
    features['ema200'] = df.ta.ema(length=200).iloc[-1]

    # Ratios
    features['ema9_21_ratio'] = features['ema9'] / features['ema21'] if features['ema21'] else 0
    features['ema21_50_ratio'] = features['ema21'] / features['ema50'] if features['ema50'] else 0
    features['ema50_200_ratio'] = features['ema50'] / features['ema200'] if features['ema200'] else 0

    # SMA Set
    features['sma20'] = df.ta.sma(length=20).iloc[-1]
    features['sma50'] = df.ta.sma(length=50).iloc[-1]
    features['sma200'] = df.ta.sma(length=200).iloc[-1]

    price = df['close'].iloc[-1]
    features['dist_sma20'] = price - features['sma20']
    features['dist_sma50'] = price - features['sma50']
    features['dist_sma200'] = price - features['sma200']

    # RSI
    rsi14 = df.ta.rsi(length=14)
    rsi21 = df.ta.rsi(length=21)
    features['rsi14'] = rsi14.iloc[-1]
    features['rsi21'] = rsi21.iloc[-1]
    features['rsi_slope'] = rsi14.iloc[-1] - rsi14.iloc[-2] if len(rsi14) > 1 else 0
    features['rsi_divergence'] = 1 if (price > df['close'].iloc[-2] and features['rsi_slope'] < 0) else 0

    # MACD
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        features['macd_line'] = macd['MACD_12_26_9'].iloc[-1]
        features['macd_signal'] = macd['MACDs_12_26_9'].iloc[-1]
        features['macd_hist'] = macd['MACDh_12_26_9'].iloc[-1]
        features['macd_hist_slope'] = macd['MACDh_12_26_9'].iloc[-1] - macd['MACDh_12_26_9'].iloc[-2]
        features['macd_cross'] = 1 if features['macd_hist_slope'] > 0 and macd['MACDh_12_26_9'].iloc[-2] <= 0 else (-1 if features['macd_hist_slope'] < 0 and macd['MACDh_12_26_9'].iloc[-2] >= 0 else 0)

    # Bollinger Bands
    bbands = df.ta.bbands(length=20, std=2)
    if bbands is not None and not bbands.empty:
        features['bb_lower'] = bbands['BBL_20_2.0'].iloc[-1]
        features['bb_middle'] = bbands['BBM_20_2.0'].iloc[-1]
        features['bb_upper'] = bbands['BBU_20_2.0'].iloc[-1]
        features['bb_bandwidth'] = bbands['BBB_20_2.0'].iloc[-1]
        features['bb_percent'] = bbands['BBP_20_2.0'].iloc[-1]
        features['bb_squeeze'] = 1 if features['bb_bandwidth'] < bbands['BBB_20_2.0'].rolling(20).mean().iloc[-1] else 0

    # Stochastic
    stoch = df.ta.stoch(k=14, d=3)
    if stoch is not None and not stoch.empty:
        features['stoch_k'] = stoch['STOCHk_14_3_3'].iloc[-1]
        features['stoch_d'] = stoch['STOCHd_14_3_3'].iloc[-1]
        features['stoch_cross'] = 1 if features['stoch_k'] > features['stoch_d'] else -1
        features['stoch_divergence'] = 0 # simplified

    # Ichimoku
    ichimoku, _ = df.ta.ichimoku()
    if ichimoku is not None and not ichimoku.empty:
        features['ichi_tenkan'] = ichimoku['ITS_9'].iloc[-1]
        features['ichi_kijun'] = ichimoku['IKS_26'].iloc[-1]
        features['ichi_span_a'] = ichimoku['ISA_9'].iloc[-1]
        features['ichi_span_b'] = ichimoku['ISB_26'].iloc[-1]
        features['ichi_cloud_color'] = 1 if features['ichi_span_a'] > features['ichi_span_b'] else -1
        features['ichi_price_pos'] = 1 if price > features['ichi_span_a'] and price > features['ichi_span_b'] else (-1 if price < features['ichi_span_a'] and price < features['ichi_span_b'] else 0)

    return features
