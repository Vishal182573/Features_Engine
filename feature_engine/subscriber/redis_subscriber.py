import asyncio
import redis.asyncio as redis
import json
from typing import Callable, Coroutine, Any
import logging

logger = logging.getLogger(__name__)

class RedisSubscriber:
    def __init__(self, market_data_url: str, timeseries_url: str):
        self.md_redis = redis.from_url(market_data_url, decode_responses=True)
        self.ts_redis = redis.from_url(timeseries_url, decode_responses=True)
        self.running = False

    async def start(self, symbols: list, on_tick: Callable, on_candle: Callable):
        self.running = True
        
        md_streams = {f"ticks:{sym}": '$' for sym in symbols}
        # time series streams
        ts_streams = {}
        for sym in symbols:
            ts_streams[f"candles:{sym}:1m"] = '$'
            ts_streams[f"candles:{sym}:5m"] = '$'

        task1 = asyncio.create_task(self._listen_loop(self.md_redis, md_streams, on_tick))
        task2 = asyncio.create_task(self._listen_loop(self.ts_redis, ts_streams, on_candle))
        
        await asyncio.gather(task1, task2)

    async def _listen_loop(self, r: redis.Redis, streams: dict, callback: Callable):
        try:
            while self.running:
                response = await r.xread(streams, count=100, block=1000)
                if not response:
                    continue
                
                for stream_name, messages in response:
                    for message_id, message_data in messages:
                        # Update the pointer for next read
                        streams[stream_name] = message_id
                        
                        try:
                            # Process the incoming dict format
                            parsed_data = {k: self._try_parse(v) for k, v in message_data.items()}
                            await callback(stream_name, parsed_data)
                        except Exception as e:
                            logger.error(f"Error processing message from {stream_name}: {e}")
        except asyncio.CancelledError:
            pass

    def _try_parse(self, val: str) -> Any:
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val

    async def stop(self):
        self.running = False
        await self.md_redis.aclose()
        await self.ts_redis.aclose()
