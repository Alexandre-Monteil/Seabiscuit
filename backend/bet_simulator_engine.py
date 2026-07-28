"""
SEABISCUIT - Quantitative Bet Simulator Engine (French Pari-Mutuel & Wall Street Hedge Fund Edition)
Simulates Gagnant, Placé, Duo (Couplé), Trio, Quarté, and Quinté+ combinations using Harville Joint Probability Models.
"""

from typing import List, Dict, Any
import numpy as np

try:
    from .utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int


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
    def simulate_duo_couple(cls, runner_a: Dict[str, Any], runner_b: Dict[str, Any], stake_usd: float = 10.0, exact_order: bool = False) -> Dict[str, Any]:
        """
        Simulates Duo (Couplé Gagnant / Ordre / Placé) using Harville 1st & 2nd place joint probability formula:
        P(A 1st, B 2nd) = p_A * (p_B / (1 - p_A))
        """
        if not isinstance(runner_a, dict) or not isinstance(runner_b, dict):
            return {}

        odds_a = safe_float(runner_a.get("decimal_odds"), default=3.0)
        odds_b = safe_float(runner_b.get("decimal_odds"), default=5.0)

        p_a = safe_float(runner_a.get("win_percent"), default=1.0 / odds_a)
        p_b = safe_float(runner_b.get("win_percent"), default=1.0 / odds_b)

        # Harville joint probabilities
        p_ab_exact = p_a * (p_b / max(0.01, 1.0 - p_a))
        p_ba_exact = p_b * (p_a / max(0.01, 1.0 - p_b))
        
        p_joint = p_ab_exact if exact_order else (p_ab_exact + p_ba_exact)

        # Estimated Pari-Mutuel dividend multiplier
        estimated_odds = round((odds_a * odds_b * 0.72) if exact_order else (odds_a * odds_b * 0.42), 2)
        estimated_odds = max(2.5, estimated_odds)

        payout = round(stake_usd * estimated_odds, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_joint * estimated_odds - 1.0) * 100.0, 1)

        return {
            "type": "Couplé Ordre" if exact_order else "Couplé Gagnant (Duo)",
            "runner_a": runner_a.get("horse"),
            "runner_b": runner_b.get("horse"),
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_joint * 100.0, 2),
            "estimated_odds": estimated_odds,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }

    @classmethod
    def simulate_trio(cls, runners: List[Dict[str, Any]], stake_usd: float = 10.0, exact_order: bool = False) -> Dict[str, Any]:
        """
        Simulates Trio (Trifecta 3-Runner Combination) using Harville 1st, 2nd, 3rd probability model.
        """
        if len(runners) < 3:
            return {}

        odds = [safe_float(r.get("decimal_odds"), 4.0) for r in runners[:3]]
        probs = [safe_float(r.get("win_percent"), 1.0 / o) for r, o in zip(runners[:3], odds)]

        p1, p2, p3 = probs[0], probs[1], probs[2]
        
        # Harville exact 1-2-3 probability
        p_exact = p1 * (p2 / max(0.01, 1.0 - p1)) * (p3 / max(0.01, 1.0 - p1 - p2))
        
        # 6 permutations for désordre (any order)
        p_trio_any = p_exact * 4.5 if not exact_order else p_exact

        mult = 0.55 if exact_order else 0.22
        estimated_odds = round(max(5.0, odds[0] * odds[1] * odds[2] * mult), 2)

        payout = round(stake_usd * estimated_odds, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_trio_any * estimated_odds - 1.0) * 100.0, 1)

        return {
            "type": "Trio Ordre" if exact_order else "Trio Désordre",
            "runners": [r.get("horse") for r in runners[:3]],
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_trio_any * 100.0, 3),
            "estimated_odds": estimated_odds,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }

    @classmethod
    def simulate_quinte(cls, runners: List[Dict[str, Any]], stake_usd: float = 2.0) -> Dict[str, Any]:
        """
        Simulates Quinté+ (Top 5 Big Prize Jackpot Combination).
        """
        if len(runners) < 5:
            return {}

        odds = [safe_float(r.get("decimal_odds"), 5.0) for r in runners[:5]]
        probs = [safe_float(r.get("win_percent"), 1.0 / o) for r, o in zip(runners[:5], odds)]

        # Combination jackpot dividend estimate
        combined_product = odds[0] * odds[1] * odds[2] * odds[3] * odds[4]
        estimated_quinte_dividend = round(max(250.0, combined_product * 0.08), 2)
        
        p_quinte = min(0.08, (1.0 / max(10.0, combined_product)) * 12.0)

        payout = round(stake_usd * estimated_quinte_dividend, 2)
        profit = round(payout - stake_usd, 2)
        ev_pct = round((p_quinte * estimated_quinte_dividend - 1.0) * 100.0, 1)

        return {
            "type": "Quinté+ Top 5 Jackpot",
            "runners": [r.get("horse") for r in runners[:5]],
            "stake_usd": stake_usd,
            "joint_prob_pct": round(p_quinte * 100.0, 4),
            "estimated_dividend_odds": estimated_quinte_dividend,
            "payout_usd": payout,
            "profit_usd": profit,
            "ev_pct": ev_pct
        }
