"""
SEABISCUIT - Quantitative Bet Generator Backtest & Bankroll Equity Curve Engine
Simulates cumulative P/L, ROI %, Win Rate %, Sharpe Ratio, and Drawdown for the SEABISCUIT
Bet Generator strategy (Gagnant/Placé, Duo, Trio, or Quinté+ per race, or no bet at all —
see bet_generator_engine.py) rather than flat-staking whichever single runner has max EV%.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

try:
    from .utils import safe_float
    from .equine_stock_engine import EquineStockEngine
    from .monte_carlo_engine import EquineMonteCarloEngine
    from .bet_generator_engine import SeabiscuitBetGenerator
except (ImportError, ValueError):
    from backend.utils import safe_float
    from backend.equine_stock_engine import EquineStockEngine
    from backend.monte_carlo_engine import EquineMonteCarloEngine
    from backend.bet_generator_engine import SeabiscuitBetGenerator


class EquineBacktestEngine:
    """Quantitative Bet Generator Backtest & P/L Tracking Suite."""

    @classmethod
    def run_ev_strategy_backtest(cls, racecards: List[Dict[str, Any]], initial_bankroll_usd: float = 1000.0,
                                  unit_bet_usd: float = 25.0, seed: int = 42) -> Dict[str, Any]:
        """
        Runs the SEABISCUIT Bet Generator across all races: for each one, the generator picks
        a bet type (Gagnant/Placé, Duo, Trio, Quinté+) and target runner(s) from the combined
        quantitative + qualitative signals, or skips the race entirely when there's no edge.
        A single Plackett-Luce outcome is sampled per race and used to settle both the
        generated bet and the "always back the favorite" baseline, so the two are compared
        against the same realized result rather than independent random draws.
        """
        if not racecards:
            return cls._empty_backtest(initial_bankroll_usd)

        processed_cards = []
        for rc in racecards:
            if isinstance(rc, dict):
                if "equity_assets" in rc:
                    processed_cards.append(rc)
                else:
                    processed_cards.append(EquineStockEngine.process_racecard(rc))

        if not processed_cards:
            return cls._empty_backtest(initial_bankroll_usd)

        rng = np.random.default_rng(seed)

        bets_history = []
        equity_curve = [initial_bankroll_usd]
        dates = ["Start"]
        current_bankroll = initial_bankroll_usd
        total_bets = 0
        winning_bets = 0
        total_staked = 0.0
        total_profit = 0.0
        returns_list = []
        bet_type_stats: Dict[str, Dict[str, float]] = {}
        races_skipped = 0

        baseline_curve = [initial_bankroll_usd]
        baseline_bankroll = initial_bankroll_usd
        baseline_bets = 0
        baseline_wins = 0
        baseline_staked = 0.0
        baseline_profit = 0.0

        for idx, rc in enumerate(processed_cards):
            assets = [a for a in rc.get("equity_assets", []) if isinstance(a, dict)]
            if len(assets) < 2:
                continue

            race_name = str(rc.get("race_name", "Race"))
            race_date = str(rc.get("race_date", "2026-07-24"))
            course = str(rc.get("course", "Track"))
            race_seed = int(rng.integers(0, 2**31))
            n_runners = len(assets)
            places_paid = 3 if n_runners >= 8 else (2 if n_runners >= 5 else 1)

            # One realized outcome per race, shared by the generated bet and the baseline.
            outcome_order = EquineMonteCarloEngine.sample_single_outcome(assets, seed=race_seed)

            # --- Baseline: always back the market favorite ---
            favorite = min(assets, key=lambda a: safe_float(a.get("decimal_odds"), default=99.0))
            fav_odds = safe_float(favorite.get("decimal_odds"), default=4.0)
            fav_won = bool(outcome_order and outcome_order[0] == favorite.get("ticker"))
            fav_payout = unit_bet_usd * fav_odds if fav_won else 0.0
            fav_pl = fav_payout - unit_bet_usd

            baseline_bankroll += fav_pl
            baseline_staked += unit_bet_usd
            baseline_profit += fav_pl
            baseline_bets += 1
            if fav_won:
                baseline_wins += 1
            baseline_curve.append(round(baseline_bankroll, 2))

            # --- SEABISCUIT Bet Generator ---
            rec = SeabiscuitBetGenerator.generate_bet(rc)
            if rec is None:
                races_skipped += 1
                continue

            bet_type = rec["bet_type"]
            target_tickers = rec["runners"]

            if bet_type == "GAGNANT":
                runner = next((a for a in assets if a.get("ticker") == target_tickers[0]), assets[0])
                odds = safe_float(runner.get("decimal_odds"), default=4.0)
                won = bool(outcome_order and outcome_order[0] == target_tickers[0])
            elif bet_type == "PLACE":
                runner = next((a for a in assets if a.get("ticker") == target_tickers[0]), assets[0])
                odds_win = safe_float(runner.get("decimal_odds"), default=4.0)
                odds = round(1.0 + (odds_win - 1.0) / 3.4, 2)
                won = target_tickers[0] in outcome_order[:places_paid]
            elif bet_type == "DUO":
                combo = EquineMonteCarloEngine.simulate_combo_probability(assets, target_tickers, exact_order=False, n_sims=6000, seed=race_seed + 1)
                odds = combo["fair_odds"]
                won = set(target_tickers) == set(outcome_order[:2])
            elif bet_type == "TRIO":
                combo = EquineMonteCarloEngine.simulate_combo_probability(assets, target_tickers, exact_order=False, n_sims=6000, seed=race_seed + 2)
                odds = combo["fair_odds"]
                won = set(target_tickers) == set(outcome_order[:3])
            else:  # QUINTE
                combo = EquineMonteCarloEngine.simulate_combo_probability(assets, target_tickers, exact_order=False, n_sims=10000, seed=race_seed + 3)
                odds = combo["fair_odds"]
                won = set(target_tickers) == set(outcome_order[:5])

            payout = unit_bet_usd * odds if won else 0.0
            net_pl = payout - unit_bet_usd

            current_bankroll += net_pl
            total_staked += unit_bet_usd
            total_profit += net_pl
            total_bets += 1
            if won:
                winning_bets += 1

            returns_list.append(net_pl / unit_bet_usd)
            equity_curve.append(round(current_bankroll, 2))
            dates.append(f"Race #{idx+1} ({bet_type})")

            stats = bet_type_stats.setdefault(bet_type, {"count": 0, "wins": 0, "profit": 0.0})
            stats["count"] += 1
            stats["wins"] += int(won)
            stats["profit"] += net_pl

            bets_history.append({
                "trade_id": total_bets,
                "date": race_date,
                "course": course,
                "race": race_name,
                "bet_type": bet_type,
                "runners": " + ".join(rec["runner_names"]),
                "confidence_pct": rec["confidence_pct"],
                "odds": odds,
                "stake_usd": unit_bet_usd,
                "outcome": "🏆 WIN" if won else "❌ LOST",
                "payout_usd": round(payout, 2),
                "net_pl_usd": round(net_pl, 2),
                "bankroll_usd": round(current_bankroll, 2)
            })

        if total_bets == 0:
            result = cls._empty_backtest(initial_bankroll_usd)
            result["races_skipped"] = races_skipped
            result["races_considered"] = len(processed_cards)
            return result

        roi_pct = round((total_profit / max(1.0, total_staked)) * 100.0, 1)
        win_rate_pct = round((winning_bets / max(1, total_bets)) * 100.0, 1)

        arr_eq = np.array(equity_curve)
        peak = np.maximum.accumulate(arr_eq)
        drawdown = (arr_eq - peak) / peak
        max_drawdown_pct = round(abs(float(np.min(drawdown))) * 100.0, 1)

        if len(returns_list) > 1 and np.std(returns_list) > 0:
            sharpe = round(float(np.mean(returns_list) / np.std(returns_list) * np.sqrt(252 / len(returns_list))), 2)
        else:
            sharpe = 0.0

        df_equity = pd.DataFrame({"step": dates, "bankroll": equity_curve})

        baseline_roi_pct = round((baseline_profit / max(1.0, baseline_staked)) * 100.0, 1)
        baseline_win_rate_pct = round((baseline_wins / max(1, baseline_bets)) * 100.0, 1)
        df_baseline_equity = pd.DataFrame({
            "step": [f"Race {i}" for i in range(len(baseline_curve))],
            "bankroll": baseline_curve
        })

        bet_type_breakdown = [
            {
                "bet_type": bt,
                "count": int(s["count"]),
                "win_rate_pct": round((s["wins"] / s["count"]) * 100.0, 1) if s["count"] else 0.0,
                "profit_usd": round(s["profit"], 2)
            }
            for bt, s in sorted(bet_type_stats.items(), key=lambda kv: kv[1]["count"], reverse=True)
        ]

        return {
            "initial_bankroll_usd": initial_bankroll_usd,
            "final_bankroll_usd": round(current_bankroll, 2),
            "total_profit_usd": round(total_profit, 2),
            "roi_pct": roi_pct,
            "total_bets": total_bets,
            "winning_bets": winning_bets,
            "win_rate_pct": win_rate_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe,
            "equity_df": df_equity,
            "bets_history": bets_history,
            "bet_type_breakdown": bet_type_breakdown,
            "races_considered": len(processed_cards),
            "races_skipped": races_skipped,
            "baseline_final_bankroll_usd": round(baseline_bankroll, 2),
            "baseline_roi_pct": baseline_roi_pct,
            "baseline_win_rate_pct": baseline_win_rate_pct,
            "baseline_bets": baseline_bets,
            "baseline_equity_df": df_baseline_equity
        }

    @staticmethod
    def _empty_backtest(initial_bankroll: float) -> Dict[str, Any]:
        """Returns empty placeholder backtest result."""
        return {
            "initial_bankroll_usd": initial_bankroll,
            "final_bankroll_usd": initial_bankroll,
            "total_profit_usd": 0.0,
            "roi_pct": 0.0,
            "total_bets": 0,
            "winning_bets": 0,
            "win_rate_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "equity_df": pd.DataFrame({"step": ["Start"], "bankroll": [initial_bankroll]}),
            "bets_history": [],
            "bet_type_breakdown": [],
            "races_considered": 0,
            "races_skipped": 0,
            "baseline_final_bankroll_usd": initial_bankroll,
            "baseline_roi_pct": 0.0,
            "baseline_win_rate_pct": 0.0,
            "baseline_bets": 0,
            "baseline_equity_df": pd.DataFrame({"step": ["Start"], "bankroll": [initial_bankroll]})
        }
