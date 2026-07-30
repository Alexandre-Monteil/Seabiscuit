"""
SEABISCUIT - Quantitative Bet Generator Backtest & Bankroll Equity Curve Engine
Simulates cumulative P/L, ROI %, Win Rate %, Sharpe Ratio, and Drawdown for the SEABISCUIT
Bet Generator strategy (a straight Gagnant bet on the top sanely-priced runner, or no bet
at all — see bet_generator_engine.py) rather than flat-staking whichever single runner has
max nominal EV%.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

try:
    from .utils import safe_float
    from .equine_stock_engine import EquineStockEngine
    from .bet_generator_engine import SeabiscuitBetGenerator
except (ImportError, ValueError):
    from backend.utils import safe_float
    from backend.equine_stock_engine import EquineStockEngine
    from backend.bet_generator_engine import SeabiscuitBetGenerator


class EquineBacktestEngine:
    """Quantitative Bet Generator Backtest & P/L Tracking Suite."""

    @staticmethod
    def _has_real_result(assets: List[Dict[str, Any]]) -> bool:
        """True only for races normalized from settled /v1/results (see
        theracingapi_client._normalize_result_as_racecard), which carry a real
        finishing_position per runner. Live today/tomorrow racecards have no result yet —
        there's nothing to backtest against, so they're excluded rather than simulated."""
        return any(a.get("finishing_position") for a in assets)

    @staticmethod
    def _real_outcome_order(assets: List[Dict[str, Any]]) -> List[str]:
        """Builds the actual finishing order (tickers, 1st to last) from each runner's real
        settled finishing_position. Non-numeric positions (fell, pulled up, etc.) sort last."""
        def pos_key(a: Dict[str, Any]) -> int:
            try:
                return int(str(a.get("finishing_position", "")).strip())
            except (ValueError, TypeError):
                return 999
        return [a.get("ticker") for a in sorted(assets, key=pos_key)]

    @staticmethod
    def _chronological_sort_key(rc: Dict[str, Any]):
        """(date, minutes-since-midnight) so races are walked oldest-to-newest — the equity
        curve should read as a walk forward through real history, not API response order."""
        date_str = str(rc.get("race_date", "1900-01-01"))
        time_part = str(rc.get("post_time", "00:00")).split(" ")[0]
        try:
            hh, mm = time_part.split(":")
            minutes = int(hh) * 60 + int(mm[:2])
        except (ValueError, IndexError):
            minutes = 0
        return (date_str, minutes)

    @classmethod
    def run_ev_strategy_backtest(cls, racecards: List[Dict[str, Any]], initial_bankroll_usd: float = 1000.0,
                                  unit_bet_usd: float = 10.0, seed: int = 42) -> Dict[str, Any]:
        """
        Runs the SEABISCUIT Bet Generator against real, settled race results only (racecards
        normalized from /v1/results — see theracingapi_client.py), walked in chronological order.
        Live today/tomorrow racecards have no result yet, so they're excluded from the backtest
        entirely rather than settled against a simulated outcome, which would test the model
        against its own assumptions instead of against what actually happened.

        Both the strategy and the baseline stake a flat `unit_bet_usd` per bet — simple to
        understand and hand-check — but stop betting once the bankroll can't cover the stake
        rather than going negative, same as a real bettor going bust.
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

        backtestable_cards = [
            rc for rc in processed_cards
            if cls._has_real_result([a for a in rc.get("equity_assets", []) if isinstance(a, dict)])
        ]
        backtestable_cards.sort(key=cls._chronological_sort_key)

        if not backtestable_cards:
            return cls._empty_backtest(initial_bankroll_usd)

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
        strategy_busted = False

        baseline_curve = [initial_bankroll_usd]
        baseline_bankroll = initial_bankroll_usd
        baseline_bets = 0
        baseline_wins = 0
        baseline_staked = 0.0
        baseline_profit = 0.0
        baseline_busted = False

        for idx, rc in enumerate(backtestable_cards):
            assets = [a for a in rc.get("equity_assets", []) if isinstance(a, dict)]
            if len(assets) < 2:
                continue

            race_name = str(rc.get("race_name", "Race"))
            race_date = str(rc.get("race_date", "2026-07-24"))
            course = str(rc.get("course", "Track"))

            # The REAL finishing order for this race — shared by the generated bet and the
            # baseline, both settled against what actually happened.
            outcome_order = cls._real_outcome_order(assets)

            # --- Baseline: always back the market favorite, flat stake ---
            if not baseline_busted and baseline_bankroll >= unit_bet_usd:
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
                if baseline_bankroll < unit_bet_usd:
                    baseline_busted = True

            # --- SEABISCUIT Bet Generator: flat stake, stop once busted ---
            if strategy_busted or current_bankroll < unit_bet_usd:
                strategy_busted = True
                continue

            rec = SeabiscuitBetGenerator.generate_bet(rc)
            if rec is None:
                races_skipped += 1
                continue

            target_ticker = rec["runners"][0]
            runner = next((a for a in assets if a.get("ticker") == target_ticker), assets[0])
            odds = safe_float(runner.get("decimal_odds"), default=4.0)
            won = bool(outcome_order and outcome_order[0] == target_ticker)

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
            dates.append(f"{race_date} #{idx+1}")

            stats = bet_type_stats.setdefault(rec["bet_type"], {"count": 0, "wins": 0, "profit": 0.0})
            stats["count"] += 1
            stats["wins"] += int(won)
            stats["profit"] += net_pl

            bets_history.append({
                "trade_id": total_bets,
                "date": race_date,
                "course": course,
                "race": race_name,
                "bet_type": rec["bet_type"],
                "runners": " + ".join(rec["runner_names"]),
                "confidence_pct": rec["confidence_pct"],
                "odds": odds,
                "stake_usd": unit_bet_usd,
                "outcome": "🏆 WIN" if won else "❌ LOST",
                "payout_usd": round(payout, 2),
                "net_pl_usd": round(net_pl, 2),
                "bankroll_usd": round(current_bankroll, 2)
            })

        # Computed unconditionally — the baseline runs independently of whether the generator
        # found anything to bet on, so a strategy that (correctly) skips every race shouldn't
        # also lose its baseline comparison numbers.
        baseline_roi_pct = round((baseline_profit / max(1.0, baseline_staked)) * 100.0, 1)
        baseline_win_rate_pct = round((baseline_wins / max(1, baseline_bets)) * 100.0, 1)
        df_baseline_equity = pd.DataFrame({
            "step": [f"Race {i}" for i in range(len(baseline_curve))],
            "bankroll": baseline_curve
        })

        if total_bets == 0:
            result = cls._empty_backtest(initial_bankroll_usd)
            result["races_skipped"] = races_skipped
            result["races_considered"] = len(backtestable_cards)
            result["baseline_final_bankroll_usd"] = round(baseline_bankroll, 2)
            result["baseline_roi_pct"] = baseline_roi_pct
            result["baseline_win_rate_pct"] = baseline_win_rate_pct
            result["baseline_bets"] = baseline_bets
            result["baseline_equity_df"] = df_baseline_equity
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
            "races_considered": len(backtestable_cards),
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
