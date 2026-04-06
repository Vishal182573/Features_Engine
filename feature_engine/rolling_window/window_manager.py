import os
from collections import deque
import asyncio
from typing import Dict, Deque, Any, List

class RollingWindowManager:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        # Symbol -> Timeframe -> Deque
        self.candles_1m: Dict[str, Deque[Dict[str, Any]]] = {
            sym: deque(maxlen=500) for sym in symbols
        }
        self.candles_5m: Dict[str, Deque[Dict[str, Any]]] = {
            sym: deque(maxlen=500) for sym in symbols
        }
        # Symbol -> Deque of ticks
        self.ticks: Dict[str, Deque[Dict[str, Any]]] = {
            sym: deque(maxlen=1000) for sym in symbols
        }
        self.lock = asyncio.Lock()

    async def add_candle_1m(self, symbol: str, candle: Dict[str, Any]):
        async with self.lock:
            if symbol in self.candles_1m:
                self.candles_1m[symbol].append(candle)

    async def add_candle_5m(self, symbol: str, candle: Dict[str, Any]):
        async with self.lock:
            if symbol in self.candles_5m:
                self.candles_5m[symbol].append(candle)

    async def add_tick(self, symbol: str, tick: Dict[str, Any]):
        async with self.lock:
            if symbol in self.ticks:
                self.ticks[symbol].append(tick)

    async def get_1m_data(self, symbol: str) -> List[Dict[str, Any]]:
        async with self.lock:
            return list(self.candles_1m.get(symbol, []))

    async def get_5m_data(self, symbol: str) -> List[Dict[str, Any]]:
        async with self.lock:
            return list(self.candles_5m.get(symbol, []))

    async def get_tick_data(self, symbol: str) -> List[Dict[str, Any]]:
        async with self.lock:
            return list(self.ticks.get(symbol, []))
