"""
SEABISCUIT - Monte Carlo Race Simulation Engine (Plackett-Luce / Gumbel-Max Sampling)
Simulates 10,000+ full race orderings per race from each runner's empirical win probability,
producing genuine Win/Place/Show frequencies and Exacta/Trifecta/Quinte joint probabilities
(as opposed to closed-form Harville approximations, which degrade with field size).
"""

from typing import Dict, List, Any
import numpy as np

try:
    from .utils import safe_float
except (ImportError, ValueError):
    from backend.utils import safe_float


class EquineMonteCarloEngine:
    """
    Simulates full finishing orders via the Plackett-Luce model using the Gumbel-Max trick:
    for each simulated race, each runner draws score = log(strength) + Gumbel(0,1) noise,
    and the descending score order is an exact sample from the Plackett-Luce ranking
    distribution parameterized by `strength`. This scales to any field size and yields
    unbiased Monte Carlo estimates of win/place/show and exact multi-runner combinations,
    unlike the Harville formula which assumes independence that breaks down for combinations
    beyond 3 runners.
    """

    DEFAULT_TAKEOUT = 0.20  # Typical French PMU/pari-mutuel pool takeout (~18-25%)

    @classmethod
    def simulate_race(cls, equity_assets: List[Dict[str, Any]], n_sims: int = 10000,
                       takeout: float = DEFAULT_TAKEOUT, seed: int = None) -> Dict[str, Any]:
        """Runs a full Plackett-Luce Monte Carlo simulation and returns win/place/show
        frequencies per runner plus the highest-probability exacta/trifecta combinations."""
        valid = [a for a in equity_assets if isinstance(a, dict)]
        n_runners = len(valid)
        if n_runners < 2:
            return cls._empty_result()

        tickers = [str(a.get("ticker", f"$RUNNER_{i}")) for i, a in enumerate(valid)]
        horses = [str(a.get("horse", "Runner")) for a in valid]

        strengths = np.array([max(1e-4, safe_float(a.get("win_percent"), default=1.0 / n_runners)) for a in valid])
        strengths = strengths / strengths.sum()
        log_strength = np.log(strengths)

        rng = np.random.default_rng(seed)
        # Gumbel-Max trick: exact Plackett-Luce sampling, fully vectorized.
        uniform = rng.random((n_sims, n_runners))
        gumbel_noise = -np.log(-np.log(np.clip(uniform, 1e-12, 1.0 - 1e-12)))
        scores = log_strength[None, :] + gumbel_noise
        order = np.argsort(-scores, axis=1)  # order[:, 0] = winner index, order[:, 1] = 2nd, ...

        places_paid = 3 if n_runners >= 8 else (2 if n_runners >= 5 else 1)

        win_counts = np.zeros(n_runners)
        place_counts = np.zeros(n_runners)
        for pos in range(min(places_paid, n_runners)):
            idx, counts = np.unique(order[:, pos], return_counts=True)
            place_counts[idx] += counts
            if pos == 0:
                win_counts[idx] = counts

        win_pct = win_counts / n_sims
        place_pct = place_counts / n_sims

        runner_probs = []
        for i in range(n_runners):
            runner_probs.append({
                "ticker": tickers[i],
                "horse": horses[i],
                "win_pct": round(float(win_pct[i]) * 100.0, 2),
                "place_pct": round(float(place_pct[i]) * 100.0, 2),
                "fair_odds": round(cls._fair_odds(float(win_pct[i]), takeout), 2)
            })
        runner_probs.sort(key=lambda r: r["win_pct"], reverse=True)

        exacta = cls._top_combinations(order, [0, 1], tickers, horses, n_sims, takeout, top_n=5)
        trifecta = cls._top_combinations(order, [0, 1, 2], tickers, horses, n_sims, takeout, top_n=5) \
            if n_runners >= 3 else []

        return {
            "n_sims": n_sims,
            "places_paid": places_paid,
            "takeout": takeout,
            "runner_probs": runner_probs,
            "exacta_top": exacta,
            "trifecta_top": trifecta,
        }

    @staticmethod
    def _fair_odds(prob: float, takeout: float) -> float:
        """Pari-mutuel fair dividend: (1 - takeout) / probability, floored at 1.01."""
        if prob <= 0.0:
            return 999.0
        return max(1.01, (1.0 - takeout) / prob)

    @classmethod
    def _top_combinations(cls, order: np.ndarray, positions: List[int], tickers: List[str],
                           horses: List[str], n_sims: int, takeout: float, top_n: int) -> List[Dict[str, Any]]:
        """Counts joint finishing-order combinations across simulations and returns the most
        probable ones with Monte Carlo-derived probability and fair dividend odds."""
        combo_cols = order[:, positions]
        combos, counts = np.unique(combo_cols, axis=0, return_counts=True)
        ranked = sorted(zip(combos.tolist(), counts.tolist()), key=lambda x: x[1], reverse=True)[:top_n]

        results = []
        for combo_idx, count in ranked:
            prob = count / n_sims
            results.append({
                "runners": [f"{tickers[i]} ({horses[i]})" for i in combo_idx],
                "prob_pct": round(prob * 100.0, 3),
                "fair_odds": round(cls._fair_odds(prob, takeout), 2)
            })
        return results

    @classmethod
    def simulate_combo_probability(cls, equity_assets: List[Dict[str, Any]], target_tickers: List[str],
                                    exact_order: bool = False, n_sims: int = 10000,
                                    takeout: float = DEFAULT_TAKEOUT, seed: int = None) -> Dict[str, Any]:
        """Runs a full-field Plackett-Luce simulation and scores the Monte Carlo probability
        that a specific set of tickers occupies the top-k finishing positions (Couplé/Trio/
        Quinté-style combination bets), either in exact order or in any order."""
        valid = [a for a in equity_assets if isinstance(a, dict)]
        tickers = [str(a.get("ticker", f"$RUNNER_{i}")) for i, a in enumerate(valid)]
        k = len(target_tickers)
        n_runners = len(valid)

        if n_runners < k or k == 0:
            return {"prob_pct": 0.0, "fair_odds": 999.0, "n_sims": 0}

        try:
            target_idx = np.array([tickers.index(t) for t in target_tickers])
        except ValueError:
            return {"prob_pct": 0.0, "fair_odds": 999.0, "n_sims": 0}

        strengths = np.array([max(1e-4, safe_float(a.get("win_percent"), default=1.0 / n_runners)) for a in valid])
        strengths = strengths / strengths.sum()
        log_strength = np.log(strengths)

        rng = np.random.default_rng(seed)
        uniform = rng.random((n_sims, n_runners))
        gumbel_noise = -np.log(-np.log(np.clip(uniform, 1e-12, 1.0 - 1e-12)))
        order = np.argsort(-(log_strength[None, :] + gumbel_noise), axis=1)

        top_k = order[:, :k]
        if exact_order:
            match = np.all(top_k == target_idx[None, :], axis=1)
        else:
            match = np.all(np.sort(top_k, axis=1) == np.sort(target_idx)[None, :], axis=1)

        prob = float(match.mean())
        return {
            "prob_pct": round(prob * 100.0, 4),
            "fair_odds": round(cls._fair_odds(prob, takeout), 2),
            "n_sims": n_sims
        }

    @classmethod
    def sample_single_outcome(cls, equity_assets: List[Dict[str, Any]], seed: int = None) -> List[str]:
        """Draws ONE Plackett-Luce finishing order (list of tickers, 1st to last) — used by
        backtest_engine.py to evaluate whether a specific generated bet would have hit against
        a single realized race result, as opposed to the frequency statistics from simulate_race."""
        valid = [a for a in equity_assets if isinstance(a, dict)]
        n_runners = len(valid)
        if n_runners == 0:
            return []

        tickers = [str(a.get("ticker", f"$RUNNER_{i}")) for i, a in enumerate(valid)]
        strengths = np.array([max(1e-4, safe_float(a.get("win_percent"), default=1.0 / n_runners)) for a in valid])
        strengths = strengths / strengths.sum()
        log_strength = np.log(strengths)

        rng = np.random.default_rng(seed)
        gumbel_noise = -np.log(-np.log(np.clip(rng.random(n_runners), 1e-12, 1.0 - 1e-12)))
        order = np.argsort(-(log_strength + gumbel_noise))

        return [tickers[i] for i in order]

    @classmethod
    def simulate_exacta_matrix(cls, equity_assets: List[Dict[str, Any]], n_sims: int = 10000,
                                seed: int = None) -> Dict[str, Any]:
        """Returns the full runner x runner P(row wins, col finishes 2nd) matrix from a single
        Plackett-Luce simulation batch, for exacta probability heatmap visualization."""
        valid = [a for a in equity_assets if isinstance(a, dict)]
        n_runners = len(valid)
        if n_runners < 2:
            return {"tickers": [], "horses": [], "matrix": []}

        tickers = [str(a.get("ticker", f"$RUNNER_{i}")) for i, a in enumerate(valid)]
        horses = [str(a.get("horse", "Runner")) for a in valid]

        strengths = np.array([max(1e-4, safe_float(a.get("win_percent"), default=1.0 / n_runners)) for a in valid])
        strengths = strengths / strengths.sum()
        log_strength = np.log(strengths)

        rng = np.random.default_rng(seed)
        uniform = rng.random((n_sims, n_runners))
        gumbel_noise = -np.log(-np.log(np.clip(uniform, 1e-12, 1.0 - 1e-12)))
        order = np.argsort(-(log_strength[None, :] + gumbel_noise), axis=1)

        winner, second = order[:, 0], order[:, 1]
        combined = winner * n_runners + second
        counts = np.bincount(combined, minlength=n_runners * n_runners).reshape(n_runners, n_runners)
        matrix_pct = (counts / n_sims * 100.0)

        return {"tickers": tickers, "horses": horses, "matrix": matrix_pct.round(2).tolist()}

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {"n_sims": 0, "places_paid": 0, "takeout": 0.0, "runner_probs": [], "exacta_top": [], "trifecta_top": []}
