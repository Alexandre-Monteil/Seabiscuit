"""
SEABISCUIT - Machine-Learned Alpha Calibration Engine (XGBoost)
Replaces the flat linear A/E heuristic with a gradient-boosted regressor trained on real
historical results (see theracingapi_client.get_historical_results) whenever enough data is
reachable, falling back to a domain-grounded synthetic dataset otherwise.
"""

import statistics
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import xgboost as xgb

try:
    from .utils import safe_float
    from .theracingapi_client import TheRacingAPIClient
except (ImportError, ValueError):
    from backend.utils import safe_float
    from backend.theracingapi_client import TheRacingAPIClient

FEATURE_NAMES = ["or_z", "market_implied_prob", "field_size", "headgear_flag"]
MIN_REAL_TRAINING_ROWS = 500


def _first_valid(*vals) -> Optional[str]:
    """Skips None/empty/"-" placeholder values (The Racing API's marker for an unpublished
    rating), matching theracingapi_client._first_valid_rating."""
    for v in vals:
        if v is not None and str(v).strip() not in ("", "-"):
            return v
    return None


class EquineWinProbabilityModel:
    """Gradient-boosted A/E alpha ratio calibrator, trained once and cached at class level."""

    _model = None
    _training_source = None  # "real" or "synthetic", for diagnostics/transparency

    @classmethod
    def training_source(cls) -> str:
        """Returns which dataset actually trained the currently cached model."""
        cls._get_model()
        return cls._training_source or "synthetic"

    @classmethod
    def _get_model(cls) -> xgb.XGBRegressor:
        if cls._model is None:
            X, y, source = cls._get_training_data()
            cls._model = cls.fit(X, y)
            cls._training_source = source
        return cls._model

    @staticmethod
    def fit(X: np.ndarray, y: np.ndarray) -> xgb.XGBRegressor:
        """Trains the A/E calibration model. Accepts any (X, y) matching FEATURE_NAMES —
        real historical results when reachable, synthetic otherwise."""
        model = xgb.XGBRegressor(
            n_estimators=200, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            objective="reg:squarederror", random_state=7
        )
        model.fit(X, y)
        return model

    @classmethod
    def _get_training_data(cls) -> Tuple[np.ndarray, np.ndarray, str]:
        """Tries to train on real settled results first; falls back to the synthetic dataset
        if the API is unreachable or too few usable rows come back."""
        try:
            races = TheRacingAPIClient().get_historical_results(days_back=60, region="gb", max_races=2500)
            rows = cls._build_real_training_rows(races)
            if len(rows) >= MIN_REAL_TRAINING_ROWS:
                X, y = cls._bin_calibrate(rows)
                return X, y, "real"
        except Exception:
            pass

        X, y = cls._synthesize_training_data(n_samples=12000, seed=7)
        return X, y, "synthetic"

    @staticmethod
    def _build_real_training_rows(races: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Extracts one row per runner with a usable starting price and finishing position:
        official-rating-vs-field-average (or_z), market-implied win probability, field size,
        and headgear flag — every feature available both here and at inference time on a
        pre-race racecard, so there's no train/inference skew."""
        rows: List[Dict[str, float]] = []

        for race in races:
            runners = race.get("runners", [])
            valid = []
            for r in runners:
                sp_dec = safe_float(r.get("sp_dec"), default=0.0)
                position = str(r.get("position", "")).strip()
                if sp_dec < 1.01 or not position.isdigit():
                    continue
                or_raw = _first_valid(r.get("or"))
                valid.append({
                    "or": safe_float(or_raw, default=None) if or_raw is not None else None,
                    "sp_dec": sp_dec,
                    "won": 1.0 if position == "1" else 0.0,
                    "headgear": 1.0 if str(r.get("headgear") or "").strip() not in ("", "-") else 0.0,
                })

            if len(valid) < 3:
                continue

            or_values = [v["or"] for v in valid if v["or"] is not None]
            field_or_mean = statistics.mean(or_values) if or_values else 90.0
            field_or_std = statistics.pstdev(or_values) if len(or_values) > 1 else 8.0
            field_size = float(len(valid))

            for v in valid:
                or_z = ((v["or"] if v["or"] is not None else field_or_mean) - field_or_mean) / max(5.0, field_or_std)
                market_p = max(0.01, min(0.95, 1.0 / v["sp_dec"]))
                rows.append({
                    "or_z": or_z,
                    "market_implied_prob": market_p,
                    "field_size": field_size,
                    "headgear_flag": v["headgear"],
                    "won": v["won"]
                })

        return rows

    @staticmethod
    def _bin_calibrate(rows: List[Dict[str, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """Bins runners by market-probability decile x or_z tertile and computes the empirical
        A/E ratio (actual win rate / mean market-implied probability) per bin — the standard
        value-betting calibration technique — then assigns each runner its bin's empirical
        ratio as the regression target, clipped to a sane range before training."""
        df = pd.DataFrame(rows)

        df["p_bin"] = pd.qcut(df["market_implied_prob"], q=5, labels=False, duplicates="drop")
        df["or_bin"] = pd.qcut(df["or_z"], q=3, labels=False, duplicates="drop")

        grouped = df.groupby(["p_bin", "or_bin"], observed=True).agg(
            win_rate=("won", "mean"),
            mean_p=("market_implied_prob", "mean")
        )
        grouped["empirical_ae"] = (grouped["win_rate"] / grouped["mean_p"].clip(lower=0.01)).clip(0.5, 1.6)

        df = df.join(grouped["empirical_ae"], on=["p_bin", "or_bin"])
        df["empirical_ae"] = df["empirical_ae"].fillna(1.0)

        X = df[FEATURE_NAMES].to_numpy(dtype=float)
        y = df["empirical_ae"].to_numpy(dtype=float)
        return X, y

    @staticmethod
    def _synthesize_training_data(n_samples: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generates a synthetic but domain-grounded (feature -> true A/E multiplier) dataset,
        used only when real historical results can't be reached (offline dev, API outage,
        no credentials)."""
        rng = np.random.default_rng(seed)

        or_z = rng.normal(0.0, 1.0, n_samples)
        market_p = np.clip(rng.beta(2.0, 6.0, n_samples), 0.02, 0.9)
        field_size = rng.integers(4, 18, n_samples).astype(float)
        headgear_flag = rng.binomial(1, 0.35, n_samples).astype(float)

        true_mult = (
            1.0
            + 0.16 * np.tanh(or_z / 1.2)
            + 0.10 * headgear_flag
            - 0.05 * np.tanh((field_size - 10.0) / 6.0)
        )
        noise = rng.normal(0.0, 0.035, n_samples)
        y = np.clip(true_mult + noise, 0.5, 1.6)

        X = np.column_stack([or_z, market_p, field_size, headgear_flag])
        return X, y

    @classmethod
    def predict_ae_ratio(cls, runner: Dict[str, Any], field_or_mean: float = 90.0,
                          field_or_std: float = 8.0, field_size: int = 8) -> float:
        """Predicts a bounded [0.75, 1.35] A/E alpha ratio for a single runner, given the
        field's Official Rating distribution (see EquineStockEngine.process_racecard, which
        computes field_or_mean/std once per race before scoring each runner)."""
        model = cls._get_model()

        official_rating = safe_float(runner.get("official_rating"), default=field_or_mean)
        or_z = (official_rating - field_or_mean) / max(5.0, field_or_std)
        decimal_odds = max(1.01, safe_float(runner.get("decimal_odds"), default=4.0))
        market_p = max(0.01, min(0.95, 1.0 / decimal_odds))
        headgear_flag = 1.0 if str(runner.get("headgear") or "").strip() not in ("", "-") else 0.0

        features = np.array([[or_z, market_p, float(field_size), headgear_flag]])
        pred = float(model.predict(features)[0])
        return round(min(1.35, max(0.75, pred)), 2)
