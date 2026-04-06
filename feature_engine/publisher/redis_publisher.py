import json
import redis.asyncio as redis
from typing import Dict, Any

class RedisPublisher:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def publish_features(self, symbol: str, timeframe: str, features: Dict[str, Any]):
        """
        Publish to: features:BTCUSDT:1m
        """
        key = f"features:{symbol}:{timeframe}"
        # Redis HMSET is deprecated, use HSET with mapping
        await self.redis.hset(key, mapping={k: str(v) for k, v in features.items()})

    async def close(self):
        await self.redis.aclose()
