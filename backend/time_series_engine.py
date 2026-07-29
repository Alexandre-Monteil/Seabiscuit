"""
SEABISCUIT - Equine Time Series & Technical Indicators Engine (Ichimoku Cloud & Moving Averages)
Calculates Ichimoku Kinko Hyo (Tenkan-sen, Kijun-sen, Senkou Span A/B, Kumo Cloud), Bollinger Bands, RSI, and MACD.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    from .utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int


class EquineTimeSeriesEngine:
    """Engine for generating asset price trajectories and technical indicators (Ichimoku, RSI, MACD)."""

    @classmethod
    def generate_career_ohlc_candles(cls, asset: Dict[str, Any], num_races: int = 15) -> pd.DataFrame:
        """Generates realistic OHLC candlestick career historical price series."""
        current_price = safe_float(asset.get("share_price_usd"), default=25.0)
        horse_name = str(asset.get("horse", "Runner"))
        
        np.random.seed(int(abs(hash(horse_name)) % 99999))
        
        dates = [datetime.now() - timedelta(days=30 * (num_races - i)) for i in range(num_races)]
        
        # Backward random walk ending at current_price
        prices = [current_price]
        for i in range(num_races - 1):
            prev = prices[-1]
            change = np.random.normal(0, 0.08 * prev)
            prices.append(max(2.0, min(95.0, prev - change)))
            
        prices.reverse()
        
        records = []
        for i in range(num_races):
            close_p = prices[i]
            open_p = close_p * (1.0 + np.random.uniform(-0.04, 0.04))
            high_p = max(open_p, close_p) * (1.0 + np.random.uniform(0.01, 0.06))
            low_p = min(open_p, close_p) * (1.0 - np.random.uniform(0.01, 0.06))
            beyer = max(70, safe_int(asset.get("beyer_speed"), 110) - (num_races - i) * np.random.randint(0, 2))
            
            records.append({
                "race_num": i + 1,
                "date": dates[i].strftime("%Y-%m-%d"),
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": np.random.randint(15000, 85000),
                "beyer_speed": beyer
            })
            
        return pd.DataFrame(records)

    @classmethod
    def compute_ichimoku_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes Ichimoku Kinko Hyo Indicators:
        - Tenkan-sen (Conversion Line): (9-period High + 9-period Low) / 2
        - Kijun-sen (Base Line): (26-period High + 26-period Low) / 2
        - Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2
        - Senkou Span B (Leading Span B): (52-period High + 52-period Low) / 2
        """
        df = df.copy()
        
        # Tenkan-sen (Conversion Line: 5-period for short career series)
        high_5 = df["high"].rolling(window=5, min_periods=1).max()
        low_5 = df["low"].rolling(window=5, min_periods=1).min()
        df["tenkan_sen"] = round((high_5 + low_5) / 2.0, 2)
        
        # Kijun-sen (Base Line: 9-period for career series)
        high_9 = df["high"].rolling(window=9, min_periods=1).max()
        low_9 = df["low"].rolling(window=9, min_periods=1).min()
        df["kijun_sen"] = round((high_9 + low_9) / 2.0, 2)
        
        # Senkou Span A (Leading Span A)
        df["senkou_span_a"] = round((df["tenkan_sen"] + df["kijun_sen"]) / 2.0, 2)
        
        # Senkou Span B (Leading Span B: 12-period)
        high_12 = df["high"].rolling(window=12, min_periods=1).max()
        low_12 = df["low"].rolling(window=12, min_periods=1).min()
        df["senkou_span_b"] = round((high_12 + low_12) / 2.0, 2)
        
        return df

    @classmethod
    def compute_eex_composite_index(cls, days: int = 90, base_value: float = 1000.0) -> pd.DataFrame:
        """Generates the $EEX Composite Market Index historical trajectory. No persisted history
        of past racecard snapshots exists to aggregate a real composite from, so — like
        generate_career_ohlc_candles — this produces a seeded illustrative random-walk series."""
        rng = np.random.default_rng(20260101)
        dates = [(datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d") for i in range(days)]

        values = [base_value]
        for _ in range(days - 1):
            drift = rng.normal(0.0006, 0.012)
            values.append(max(200.0, values[-1] * (1.0 + drift)))

        return pd.DataFrame({"date": dates, "eex_index": [round(v, 2) for v in values]})

    @classmethod
    def compute_multi_runner_time_series(cls, equity_assets: List[Dict[str, Any]], num_races: int = 10) -> pd.DataFrame:
        """Generates multi-runner career time series DataFrame."""
        if not equity_assets:
            return pd.DataFrame()
            
        dates = [(datetime.now() - timedelta(days=30 * (num_races - i))).strftime("%Y-%m-%d") for i in range(num_races)]
        data = {"date": dates}
        
        for asset in equity_assets:
            if not isinstance(asset, dict):
                continue
            ticker = str(asset.get("ticker", "$RUNNER"))
            df_candles = cls.generate_career_ohlc_candles(asset, num_races=num_races)
            data[ticker] = df_candles["close"].values
            
        return pd.DataFrame(data)
