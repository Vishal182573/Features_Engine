import os
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
MARKET_DATA_REDIS_URL = os.getenv("MARKET_DATA_REDIS_URL", "redis://localhost:6379/0")
TIMESERIES_REDIS_URL = os.getenv("TIMESERIES_REDIS_URL", "redis://localhost:6379/1")
FEATURE_REDIS_URL = os.getenv("FEATURE_REDIS_URL", "redis://localhost:6379/2")

# Database Configuration
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://user:password@localhost:5432/db")

# Symbols to support
TARGET_SYMBOLS = os.getenv("TARGET_SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
