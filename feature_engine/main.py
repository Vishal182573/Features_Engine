import asyncio
import logging
import pandas as pd
from typing import Dict, Any

from config.settings import TARGET_SYMBOLS, MARKET_DATA_REDIS_URL, TIMESERIES_REDIS_URL, FEATURE_REDIS_URL, POSTGRES_DSN
from subscriber.redis_subscriber import RedisSubscriber
from rolling_window.window_manager import RollingWindowManager
from publisher.redis_publisher import RedisPublisher
from storage.postgres_writer import PostgresWriter
from features import (
    calculate_price_features,
    calculate_volatility_features,
    calculate_volume_features,
    calculate_tick_features,
    calculate_trend_features,
    calculate_stat_features,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngine:
    def __init__(self):
        self.symbols = TARGET_SYMBOLS
        self.window_manager = RollingWindowManager(self.symbols)
        self.subscriber = RedisSubscriber(MARKET_DATA_REDIS_URL, TIMESERIES_REDIS_URL)
        self.publisher = RedisPublisher(FEATURE_REDIS_URL)
        self.writer = PostgresWriter(POSTGRES_DSN)

    async def _compute_and_publish(self, symbol: str, timeframe: str, timestamp: int, df: pd.DataFrame, is_tick: bool = False):
        try:
            features = {
                'symbol': symbol,
                'timestamp': timestamp,
                'timeframe': timeframe
            }

            if not is_tick:
                # Candle Features
                features.update(calculate_price_features(df))
                features.update(calculate_volatility_features(df))
                features.update(calculate_volume_features(df))
                features.update(calculate_trend_features(df))
                features.update(calculate_stat_features(df))
            else:
                # Tick Features
                features.update(calculate_tick_features(df))

            # Store in DB
            await self.writer.insert_features(symbol, timestamp, timeframe, features)

            # Publish to Redis
            await self.publisher.publish_features(symbol, timeframe, features)
            
            logger.info(f"Published features for {symbol} @ {timeframe}")

        except Exception as e:
            logger.error(f"Error computing features for {symbol} {timeframe}: {e}", exc_info=True)

    async def on_tick(self, stream_name: str, tick: Dict[str, Any]):
        symbol = stream_name.split(':')[-1]
        await self.window_manager.add_tick(symbol, tick)
        
        # Calculate tick features periodically or on every N ticks
        # Here we just fetch latest for computation
        data = await self.window_manager.get_tick_data(symbol)
        df = pd.DataFrame(data)
        if not df.empty and 'timestamp' in df.columns:
            ts = df['timestamp'].iloc[-1]
            await self._compute_and_publish(symbol, 'tick', ts, df, is_tick=True)

    async def on_candle(self, stream_name: str, candle: Dict[str, Any]):
        parts = stream_name.split(':')
        symbol = parts[1]
        timeframe = parts[2]

        if timeframe == '1m':
            await self.window_manager.add_candle_1m(symbol, candle)
            data = await self.window_manager.get_1m_data(symbol)
        else:
            await self.window_manager.add_candle_5m(symbol, candle)
            data = await self.window_manager.get_5m_data(symbol)

        df = pd.DataFrame(data)
        if not df.empty and 'timestamp' in df.columns:
            # Ensure columns are numeric for calculation
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])
            
            ts = df['timestamp'].iloc[-1]
            await self._compute_and_publish(symbol, timeframe, ts, df, is_tick=False)

    async def run(self):
        logger.info("Starting Feature Engine...")
        try:
            await self.subscriber.start(self.symbols, self.on_tick, self.on_candle)
        except Exception as e:
            logger.error(f"Feature engine error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        logger.info("Shutting down...")
        await self.subscriber.stop()
        await self.publisher.close()
        self.writer.close()

if __name__ == "__main__":
    engine = FeatureEngine()
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        logger.info("Interrupted.")
