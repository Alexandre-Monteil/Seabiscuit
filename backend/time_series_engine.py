"""
SEABISCUIT - Equine Time Series & Technical Indicators Engine (Ichimoku Cloud & Moving Averages)
Builds a career performance-figure series from real race times (The Racing API's
/v1/horses/{id}/analysis/distance-times) when a live horse_id is available, falling back to a
seeded illustrative random walk otherwise, then computes Ichimoku Kinko Hyo indicators on it.
"""

import statistics
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    from .utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int


class EquineTimeSeriesEngine:
    """Engine for generating asset performance trajectories and technical indicators (Ichimoku)."""

    @staticmethod
    def _parse_race_time_seconds(time_str: Any) -> Optional[float]:
        """Parses a race time like "1:11.16" (mm:ss.ss) or "58.32" (ss.ss) into seconds."""
        if time_str is None or str(time_str).strip() in ("", "-"):
            return None
        parts = str(time_str).split(":")
        try:
            if len(parts) == 2:
                return float(parts[0]) * 60.0 + float(parts[1])
            return float(parts[0])
        except ValueError:
            return None

    @classmethod
    def _fetch_real_performance_records(cls, horse_id: str) -> List[Dict[str, Any]]:
        """Converts real race times per distance bucket into a performance figure: 100 = that
        distance's own median time for this horse, faster than the median scores higher — so
        the series reflects genuine form, not a fixed external par time."""
        try:
            from .theracingapi_client import TheRacingAPIClient
        except (ImportError, ValueError):
            from backend.theracingapi_client import TheRacingAPIClient

        try:
            data = TheRacingAPIClient().get_horse_distance_times_analysis(horse_id)
        except Exception:
            return []

        records = []
        for dist_bucket in data.get("distances", []):
            times_list = dist_bucket.get("times", [])
            bucket_secs = [cls._parse_race_time_seconds(t.get("time")) for t in times_list]
            bucket_secs = [s for s in bucket_secs if s]
            if not bucket_secs:
                continue
            median_secs = statistics.median(bucket_secs)

            for t in times_list:
                secs = cls._parse_race_time_seconds(t.get("time"))
                if not secs or not t.get("date"):
                    continue
                records.append({
                    "date": t.get("date"),
                    "course": t.get("course"),
                    "going": t.get("going"),
                    "position": t.get("position"),
                    "distance": dist_bucket.get("dist"),
                    "performance_figure": round(100.0 * (median_secs / secs), 2)
                })

        return records

    @classmethod
    def generate_career_ohlc_candles(cls, asset: Dict[str, Any], num_races: int = 15) -> pd.DataFrame:
        """Builds a career performance series for one runner: real race-time-derived figures
        when a live horse_id is available, a seeded illustrative random walk otherwise. Each
        bar's open/high/low/close are set equal to that race's single performance figure
        (there's no real intra-race high/low to synthesize honestly) so downstream rolling
        Ichimoku calculations still work."""
        horse_id = asset.get("horse_id")
        records = cls._fetch_real_performance_records(horse_id) if horse_id else []

        if records:
            df = pd.DataFrame(records).sort_values("date").tail(num_races).reset_index(drop=True)
            df["race_num"] = range(1, len(df) + 1)
            df["open"] = df["performance_figure"]
            df["high"] = df["performance_figure"]
            df["low"] = df["performance_figure"]
            df["close"] = df["performance_figure"]
            df["volume"] = 0
            df["beyer_speed"] = safe_int(asset.get("beyer_speed"), default=110)
            return df[["race_num", "date", "open", "high", "low", "close", "volume", "beyer_speed",
                       "course", "going", "position", "distance"]]

        return cls._synthetic_ohlc_candles(asset, num_races)

    @staticmethod
    def _synthetic_ohlc_candles(asset: Dict[str, Any], num_races: int) -> pd.DataFrame:
        """Seeded illustrative random-walk fallback for runners without a live horse_id
        (synthetic horizon racecards) or when the API is unreachable."""
        current_price = safe_float(asset.get("share_price_usd"), default=25.0)
        horse_name = str(asset.get("horse", "Runner"))

        rng = np.random.default_rng(int(abs(hash(horse_name)) % 99999))
        dates = [datetime.now() - timedelta(days=30 * (num_races - i)) for i in range(num_races)]

        prices = [current_price]
        for _ in range(num_races - 1):
            prev = prices[-1]
            change = rng.normal(0, 0.08 * prev)
            prices.append(max(2.0, min(95.0, prev - change)))
        prices.reverse()

        records = []
        for i in range(num_races):
            close_p = prices[i]
            open_p = close_p * (1.0 + rng.uniform(-0.04, 0.04))
            high_p = max(open_p, close_p) * (1.0 + rng.uniform(0.01, 0.06))
            low_p = min(open_p, close_p) * (1.0 - rng.uniform(0.01, 0.06))
            beyer = max(70, safe_int(asset.get("beyer_speed"), 110) - (num_races - i) * rng.integers(0, 2))

            records.append({
                "race_num": i + 1,
                "date": dates[i].strftime("%Y-%m-%d"),
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": int(rng.integers(15000, 85000)),
                "beyer_speed": int(beyer)
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
        of past racecard snapshots exists to aggregate a real composite from, so — like the
        synthetic OHLC fallback — this produces a seeded illustrative random-walk series."""
        rng = np.random.default_rng(20260101)
        dates = [(datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d") for i in range(days)]

        values = [base_value]
        for _ in range(days - 1):
            drift = rng.normal(0.0006, 0.012)
            values.append(max(200.0, values[-1] * (1.0 + drift)))

        return pd.DataFrame({"date": dates, "eex_index": [round(v, 2) for v in values]})

    @classmethod
    def compute_multi_runner_time_series(cls, equity_assets: List[Dict[str, Any]], num_races: int = 10) -> pd.DataFrame:
        """Generates multi-runner career time series DataFrame (real performance figures per
        runner when available, aligned on a shared race-index axis since each horse's real
        race dates rarely coincide)."""
        if not equity_assets:
            return pd.DataFrame()

        race_labels = [f"Race -{num_races - i}" if i < num_races - 1 else "Latest" for i in range(num_races)]
        data = {"date": race_labels}

        for asset in equity_assets:
            if not isinstance(asset, dict):
                continue
            ticker = str(asset.get("ticker", "$RUNNER"))
            df_candles = cls.generate_career_ohlc_candles(asset, num_races=num_races)
            closes = list(df_candles["close"].values)
            if len(closes) < num_races:
                closes = [closes[0]] * (num_races - len(closes)) + closes if closes else [0.0] * num_races
            data[ticker] = closes[-num_races:]

        return pd.DataFrame(data)
