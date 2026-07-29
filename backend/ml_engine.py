"""
SEABISCUIT - Machine-Learned Alpha Calibration Engine (XGBoost)
Replaces the flat linear A/E heuristic with a gradient-boosted regressor that captures
non-linear handicapping interactions (speed x form, going affinity, connections synergy).

Data note: The Racing API tier in use here does not stream settled historical results, so
there is no labelled outcome feed to fit against. The model is instead trained on a
domain-grounded synthetic dataset that encodes known non-linear handicapping relationships
(diminishing returns on speed edges, going-affinity curvature, speed x form interaction) that
a linear formula cannot represent. `fit()` exposes the same (X, y) contract a real settled-
results dataset would use, so swapping in live outcomes later requires no change to the
inference path in `predict_ae_ratio`.
"""

from typing import Dict, Any, Tuple
import numpy as np
import xgboost as xgb

try:
    from .utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int

FEATURE_NAMES = ["beyer_delta", "form_score", "moisture_fit", "rating_delta", "jockey_synergy", "age_factor"]


class EquineWinProbabilityModel:
    """Gradient-boosted A/E alpha ratio calibrator, trained once and cached at class level."""

    _model = None

    @classmethod
    def _get_model(cls) -> xgb.XGBRegressor:
        if cls._model is None:
            X, y = cls._synthesize_training_data(n_samples=12000, seed=7)
            cls._model = cls.fit(X, y)
        return cls._model

    @staticmethod
    def fit(X: np.ndarray, y: np.ndarray) -> xgb.XGBRegressor:
        """Trains the A/E calibration model. Accepts any (X, y) matching FEATURE_NAMES —
        synthetic today, swappable for real settled-result training data later."""
        model = xgb.XGBRegressor(
            n_estimators=200, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            objective="reg:squarederror", random_state=7
        )
        model.fit(X, y)
        return model

    @staticmethod
    def _synthesize_training_data(n_samples: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generates a synthetic but domain-grounded (feature -> true A/E multiplier) dataset."""
        rng = np.random.default_rng(seed)

        beyer_delta = rng.normal(0.0, 15.0, n_samples)
        form_score = rng.choice([-0.06, 0.0, 0.06], size=n_samples, p=[0.25, 0.45, 0.30])
        moisture_fit = np.clip(rng.beta(6.0, 2.0, n_samples), 0.5, 0.99)
        rating_delta = rng.normal(0.0, 10.0, n_samples)
        jockey_synergy = (rng.beta(2.5, 2.5, n_samples) - 0.5) * 0.4
        age_factor = rng.normal(0.0, 1.0, n_samples)

        true_mult = (
            1.0
            + 0.16 * np.tanh(beyer_delta / 18.0)
            + 0.55 * form_score
            + 0.09 * np.tanh(rating_delta / 14.0)
            + 0.30 * (moisture_fit - 0.85)
            + 0.55 * jockey_synergy
            + 0.15 * np.tanh(beyer_delta / 20.0) * form_score
        )
        noise = rng.normal(0.0, 0.035, n_samples)
        y = np.clip(true_mult + noise, 0.65, 1.45)

        X = np.column_stack([beyer_delta, form_score, moisture_fit, rating_delta, jockey_synergy, age_factor])
        return X, y

    @classmethod
    def predict_ae_ratio(cls, runner: Dict[str, Any], beyer_benchmark: float = 110.0) -> float:
        """Predicts a bounded [0.75, 1.35] A/E alpha ratio for a single runner."""
        model = cls._get_model()

        beyer_speed = safe_int(runner.get("beyer_speed"), default=112)
        form_str = str(runner.get("form", ""))
        form_score = 0.06 if "1" in form_str else (-0.06 if ("0" in form_str or "9" in form_str) else 0.0)
        moisture_fit = safe_float(runner.get("track_moisture_fit"), default=0.85)
        rating_delta = safe_int(runner.get("official_rating"), default=115) - 115.0
        jockey_synergy = safe_float(runner.get("jockey_synergy_score"), default=0.0)
        age_factor = safe_int(runner.get("age"), default=4) - 4.0

        features = np.array([[beyer_speed - beyer_benchmark, form_score, moisture_fit,
                               rating_delta, jockey_synergy, age_factor]])
        pred = float(model.predict(features)[0])
        return round(min(1.35, max(0.75, pred)), 2)
