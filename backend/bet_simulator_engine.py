"""
SEABISCUIT - Quantitative Bet Simulator & Order Book Engine (French Pari-Mutuel & Wall Street Hedge Fund Edition)
Simulates Gagnant, Placé, Duo (Couplé), Trio, and Quinté+ combinations plus synthetic L2
order book depth, both driven by Monte Carlo win probabilities and market capitalization.
"""

from typing import List, Dict, Any
import numpy as np

try:
    from .utils import safe_float
    from .monte_carlo_engine import EquineMonteCarloEngine
except (ImportError, ValueError):
    from backend.utils import safe_float
    from backend.monte_carlo_engine import EquineMonteCarloEngine


class QuantBetSimulatorEngine:
    """Quantitative Bet & Combination Simulator Engine."""

    @staticmethod
    def simulate_gagnant_place(asset: Dict[str, Any], stake_usd: float = 10.0) -> Dict[str, Any]:
        """Simulates single runner Gagnant (Win) and Placé (Place) bets."""
        if not isinstance(asset, dict):
            return {}

        odds_win = safe_float(asset.get("decimal_odds"), default=4.0)
        p_win = safe_float(asset.get("win_percent"), default=1.0 / odds_win)
        
        # Placé odds approximation (roughly 1 + (Odds - 1)/3.5 for 8+ runners)
        odds_place = round(1.0 + (odds_win - 1.0) / 3.4, 2)
        p_place = min(0.95, safe_float(asset.get("place_percent"), default=p_win * 2.2))

        # Gagnant Metrics
        win_payout = round(stake_usd * odds_win, 2)
        win_profit = round(win_payout - stake_usd, 2)
        win_ev_pct = round((p_win * odds_win - 1.0) * 100.0, 1)
        win_half_kelly_stake = round(max(0.0, ((win_ev_pct / 100.0) / max(0.1, odds_win - 1.0)) * 0.5 * 100.0), 2)

        # Placé Metrics
        place_payout = round(stake_usd * odds_place, 2)
        place_profit = round(place_payout - stake_usd, 2)
        place_ev_pct = round((p_place * odds_place - 1.0) * 100.0, 1)

        return {
            "horse": asset.get("horse", "Runner"),
            "ticker": asset.get("ticker", "$RUNNER"),
            "stake_usd": stake_usd,
            "win": {
                "odds": odds_win,
                "prob_pct": round(p_win * 100.0, 1),
                "payout_usd": win_payout,
                "profit_usd": win_profit,
                "ev_pct": win_ev_pct,
                "half_kelly_usd": round((win_half_kelly_stake / 100.0) * 100.0, 2)
            },
            "place": {
                "odds": odds_place,
                "prob_pct": round(p_place * 100.0, 1),
                "payout_usd": place_payout,
                "profit_usd": place_profit,
                "ev_pct": place_ev_pct
            }
        }

    @classmethod
    def simulate_duo_couple(cls, runner_a: Dict[str, Any], runner_b: Dict[str, Any], all_assets: List[Dict[str, Any]],
                             stake_usd: float = 10.0, exact_order: bool = False, n_sims: int = 10000) -> Dict[str, Any]:
        """
        Simulates Duo (Couplé Gagnant / Ordre) via full-field Monte Carlo (see monte_carlo_engine.py):
        the joint probability and pool-fair dividend come from 10,000 simulated finishing orders
        of the whole field, not a 2-runner Harville approximation blind to the rest of the race.
        """
        if not isinstance(runner_a, dict) or not isinstance(runner_b, dict):
            return {}

        seed = abs(hash((runner_a.get("ticker"), runner_b.get("ticker"), exact_order))) % (2**31)
        combo = EquineMonteCarloEngine.simulate_combo_probability(
            all_assets, [runner_a.get("ticker"), runner_b.get("ticker")],
            exact_order=exact_order, n_sims=n_sims, seed=seed
        )

        p_joint = combo["prob_pct"] / 100.0
        fair_odds = combo["fair_odds"]

        payout = round(stake_usd * fair_odds, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_joint * fair_odds - 1.0) * 100.0, 1)

        return {
            "type": "Couplé Ordre" if exact_order else "Couplé Gagnant (Duo)",
            "runner_a": runner_a.get("horse"),
            "runner_b": runner_b.get("horse"),
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_joint * 100.0, 2),
            "estimated_odds": fair_odds,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }

    @classmethod
    def simulate_trio(cls, runners: List[Dict[str, Any]], all_assets: List[Dict[str, Any]],
                       stake_usd: float = 10.0, exact_order: bool = False, n_sims: int = 10000) -> Dict[str, Any]:
        """Simulates Trio (Trifecta 3-Runner Combination) via full-field Monte Carlo simulation."""
        if len(runners) < 3:
            return {}

        target_tickers = [r.get("ticker") for r in runners[:3]]
        seed = abs(hash((tuple(target_tickers), exact_order))) % (2**31)
        combo = EquineMonteCarloEngine.simulate_combo_probability(
            all_assets, target_tickers, exact_order=exact_order, n_sims=n_sims, seed=seed
        )

        p_trio = combo["prob_pct"] / 100.0
        fair_odds = combo["fair_odds"]

        payout = round(stake_usd * fair_odds, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_trio * fair_odds - 1.0) * 100.0, 1)

        return {
            "type": "Trio Ordre" if exact_order else "Trio Désordre",
            "runners": [r.get("horse") for r in runners[:3]],
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_trio * 100.0, 3),
            "estimated_odds": fair_odds,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }

    @classmethod
    def simulate_quinte(cls, runners: List[Dict[str, Any]], all_assets: List[Dict[str, Any]],
                         stake_usd: float = 2.0, n_sims: int = 20000) -> Dict[str, Any]:
        """Simulates Quinté+ (Top 5, any order) via full-field Monte Carlo simulation."""
        if len(runners) < 5:
            return {}

        target_tickers = [r.get("ticker") for r in runners[:5]]
        seed = abs(hash(tuple(target_tickers))) % (2**31)
        combo = EquineMonteCarloEngine.simulate_combo_probability(
            all_assets, target_tickers, exact_order=False, n_sims=n_sims, seed=seed
        )

        p_quinte = combo["prob_pct"] / 100.0
        fair_dividend = combo["fair_odds"]

        payout = round(stake_usd * fair_dividend, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_quinte * fair_dividend - 1.0) * 100.0, 1)

        return {
            "type": "Quinté+ Top 5 Jackpot",
            "runners": [r.get("horse") for r in runners[:5]],
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_quinte * 100.0, 4),
            "estimated_dividend_odds": fair_dividend,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }

    @staticmethod
    def generate_order_book(asset: Dict[str, Any], all_assets: List[Dict[str, Any]], levels: int = 5) -> Dict[str, Any]:
        """
        Generates synthetic L2 order book depth for an equine asset. Unlike a fixed-percentage
        stub, spread and depth are driven by real inputs: spread widens with longer odds and
        with A/E model disagreement (mispricing = uncertainty = wider markets), while per-level
        liquidity scales with the runner's market capitalization (favorites trade deeper books
        than longshots), with a ticker-seeded jitter for level-to-level texture.
        """
        if not isinstance(asset, dict):
            return {}

        mid_price = safe_float(asset.get("share_price_usd"), default=25.0)
        decimal_odds = safe_float(asset.get("decimal_odds"), default=4.0)
        ae_ratio = safe_float(asset.get("ae_ratio"), default=1.0)
        market_cap = safe_float(asset.get("market_cap_usd"), default=100000.0)
        ticker = str(asset.get("ticker", "$RUNNER"))

        spread_pct = min(0.08, max(0.005, 0.004 + decimal_odds * 0.0025 + abs(ae_ratio - 1.0) * 0.03))
        liquidity_base = max(400.0, market_cap * 0.00025)
        decay = 0.62

        rng = np.random.default_rng(abs(hash(ticker)) % 99999)

        bids, asks = [], []
        for i in range(levels):
            level_gap_pct = spread_pct * (0.5 + i * 0.42)
            bid_price = round(mid_price * (1.0 - level_gap_pct), 2)
            ask_price = round(mid_price * (1.0 + level_gap_pct), 2)

            bid_vol = round(max(50.0, liquidity_base * (decay ** i) * rng.uniform(0.75, 1.25)), 0)
            ask_vol = round(max(50.0, liquidity_base * (decay ** i) * rng.uniform(0.75, 1.25)), 0)

            bids.append({"level": f"BID {i+1}", "price_usd": max(0.01, bid_price), "volume_usd": bid_vol})
            asks.append({"level": f"ASK {i+1}", "price_usd": ask_price, "volume_usd": ask_vol})

        total_bid_vol = sum(b["volume_usd"] for b in bids)
        total_ask_vol = sum(a["volume_usd"] for a in asks)
        imbalance_pct = round(((total_bid_vol - total_ask_vol) / max(1.0, total_bid_vol + total_ask_vol)) * 100.0, 1)

        if imbalance_pct > 8.0:
            imbalance_label = "🟢 BUY HEAVY"
        elif imbalance_pct < -8.0:
            imbalance_label = "🔴 SELL HEAVY"
        else:
            imbalance_label = "⚪ BALANCED"

        bid1, ask1 = bids[0], asks[0]
        spread_usd = round(ask1["price_usd"] - bid1["price_usd"], 2)
        micro_price = round(
            (bid1["price_usd"] * ask1["volume_usd"] + ask1["price_usd"] * bid1["volume_usd"]) /
            max(1.0, bid1["volume_usd"] + ask1["volume_usd"]), 2
        )

        return {
            "ticker": ticker,
            "horse": asset.get("horse", "Runner"),
            "bids": bids,
            "asks": asks,
            "spread_usd": spread_usd,
            "spread_pct": round(spread_pct * 100.0, 2),
            "micro_price": micro_price,
            "total_bid_vol_usd": total_bid_vol,
            "total_ask_vol_usd": total_ask_vol,
            "imbalance_pct": imbalance_pct,
            "imbalance_label": imbalance_label
        }
