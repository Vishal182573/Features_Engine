# Quant Feature Engine ⚡

A high-performance, asynchronous feature calculation engine built in Python designed to ingest real-time tick and candle data, compute deep market features (Alpha), and distribute them to both hot storage (Redis) and cold persistence (PostgreSQL) instantly.

## 🌟 System Architecture Overview

The system bridges the gap between raw market data streams and quantitative/machine learning strategies. 

```mermaid
graph TD;
    subgraph Instances
        A[Redis: Market Data stream]
        B[Redis: Time Series Data]
    end
    
    subgraph Feature Engine
        C(Layer 1 - Data Subscriber)
        D(Layer 2 - Rolling Window Manager)
        E(Layer 3 - Feature Calculators)
        F(Layer 4 - Publisher)
        G(Layer 5 - Writer)
    end
    
    subgraph Destinations
        H[Redis: Feature Store Hash]
        I[(PostgreSQL: Cold Store)]
    end

    A -- "Ticks" --> C;
    B -- "1m / 5m Candles" --> C;
    C --> D;
    D -- "DataFrames" --> E;
    E --> F;
    E --> G;
    F --> H;
    G --> I;
```

## 📁 Directory Structure Breakdown

The codebase is logically partitioned to maintain a clean separation of concerns:

- `config/settings.py`: Resolves environment variables mapped to all our required endpoint bindings. 
- `subscriber/redis_subscriber.py`: Non-blocking event loop listener consuming streams via `XREAD`.
- `rolling_window/window_manager.py`: Thread-safe Deque managers retaining histories (`1000 ticks`, `500 candles`).
- `features/`: The brain module containing specialized sub-modules to formulate hundreds of indicators natively utilizing vector math.
- `publisher/redis_publisher.py`: Fast caching emitter inserting calculated hashes straight to a separate Redis DB.
- `storage/postgres_writer.py`: Thread-pooled batch sink for PostgreSQL table distribution seamlessly offloading standard blocking queries.
- `main.py`: The system orchestrator bridging connections, executing data passes natively, and coordinating concurrency tasks.

## 🧮 Feature Categories

The engine transforms raw inputs using computational analysis categorizing them into highly reactive metrics:

### 1. 📈 Price Features (`price_features.py`)
Moving Averages (`EMA 9/21/50/100/200`, `SMA`), Oscillators (`RSI` slope + divergence flags, `MACD` histograms, signal crosses), Boundaries (`Bollinger Bands` properties like squeeze and bandwidth), momentum metrics (`Stochastic` conditions), and holistic metrics (`Ichimoku` cloud parameters).

### 2. 🌊 Volatility Features (`volatility_features.py`)
Dynamic boundaries analyzing expected risk formats like `ATR` (14, normalized, and ranked) and `Keltner Channels`. Converts standard close arrays directly to log returns and isolates historical/annualized standard derivations.

### 3. 📊 Volume Features (`volume_features.py`)
Volume-Weighted conditions heavily utilized by institutions like `VWAP`, deviations, `VWMA` mappings, `OBV` (On-Balance Volume) and logic gates filtering active or thin trading sessions using rolling averages.

### 4. ⏱️ Tick Features (`tick_features.py`)
Extreme-micro features natively constructed from pure order events (Order Flow): `CVD` (Cumulative Volume Delta) analysis, Bid/Ask spread constraints, algorithmic velocity speeds (Ticks per second), and large footprint radar tracking.

### 5. 📉 Trend Features (`trend_features.py`)
Classifies overall asset direction using `ADX` plus directionals (`+DI / -DI`) routing simple structural states into a text matrix representing robust `Market Regimes` (e.g. `TRENDING_UP`, `RANGING`, `HIGH_VOLATILITY`).

### 6. 📐 Stat Features (`stat_features.py`)
Quant-native metrics generating periodic normalized returns (1/5/20 block), `Z-Scores`, isolated individual candlestick structural physics (Wick dimensions, doji flags), and localized cross-asset analysis vectors (like rolling BTC vs ETH correlation limits).

## 🚀 Speed & Concurrency Design

Python typically suffers heavily from Global Interpreter Lock (GIL) limitations. This engine breaks out of those constraints seamlessly:
1. **Async HTTP & Redis Calls**: Powered inherently by `asyncio` and `aioredis`, listening and sending out data doesn't freeze computation capabilities.
2. **PostgreSQL Hand-off**: `psycopg2` is intrinsically a blocking driver. `PostgresWriter` intercepts writes routing heavy batched SQL execution through decoupled `asyncio.to_thread` pools effectively rendering db queries lock-free.
3. **C-Powered Analytics**: All statistical indicators lean onto `pandas` & `pandas-ta`. These computations pass arrays immediately into optimized C backend extensions (NumPy vectorization) meaning calculations over hundreds of elements compute in under milliseconds.

## ⚙️ Installation & Usage

### Prerequisites
- Python 3.10+
- Access to 3 Redis Instances/Databases (Market Data, Time Series, Features Out)
- PostgreSQL Database instance

### Setup

We highly recommend using a Python virtual environment to keep dependencies isolated:

1. Clone / Access the repository
2. Create and activate a Virtual Environment:
```powershell
# Open your terminal inside the project directory
cd c:\Users\sharm\Documents\quant\Features_Engine

# Create the virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# OR (Windows cmd)
# .\venv\Scripts\activate.bat
```
3. Install the dependencies:
```powershell
pip install -r requirements.txt
```

### Environment Configuration
Either natively export these variables onto your environment or supply a `.env` file at the root.

```env
# Example .env Configuration
MARKET_DATA_REDIS_URL="redis://localhost:6379/0"
TIMESERIES_REDIS_URL="redis://localhost:6379/1"
FEATURE_REDIS_URL="redis://localhost:6379/2"
POSTGRES_DSN="postgresql://user:password@localhost:5432/quant_db"
TARGET_SYMBOLS="BTCUSDT,ETHUSDT,SOLUSDT"
```

### Running the Engine
Simply boot the orchestrator payload located within the main module scope.
```bash
cd feature_engine
python main.py
```
The program will attach onto streams infinitely and begin continuous calculations instantly logging out operations. 
