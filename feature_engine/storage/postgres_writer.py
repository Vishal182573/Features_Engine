import psycopg2
from psycopg2.extras import execute_values
import asyncio
from typing import List, Dict, Any
import json

class PostgresWriter:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None
        self._init_db()

    def _init_db(self):
        self.conn = psycopg2.connect(self.dsn)
        with self.conn.cursor() as cur:
            # Create tables based on timeframe
            for tf in ['1m', '5m', 'tick']:
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS features_{tf} (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(50) NOT NULL,
                        timestamp BIGINT NOT NULL,
                        features JSONB NOT NULL
                    )
                """)
                cur.execute(f"CREATE INDEX IF NOT EXISTS idx_features_{tf}_symbol_time ON features_{tf}(symbol, timestamp)")
        self.conn.commit()

    def _insert_batch(self, timeframe: str, records: List[tuple]):
        if not self.conn:
            self.conn = psycopg2.connect(self.dsn)
        
        query = f"INSERT INTO features_{timeframe} (symbol, timestamp, features) VALUES %s"
        with self.conn.cursor() as cur:
            execute_values(cur, query, records)
        self.conn.commit()

    async def insert_features(self, symbol: str, timestamp: int, timeframe: str, features: Dict[str, Any]):
        # Run blocking db call in a thread
        record = (symbol, timestamp, json.dumps(features))
        await asyncio.to_thread(self._insert_batch, timeframe, [record])

    def close(self):
        if self.conn:
            self.conn.close()
