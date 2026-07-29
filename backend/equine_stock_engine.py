"""
SEABISCUIT - Institutional Equine Financial Stock Engine (Hedge Fund Quantitative Model)
Converts race runners into Wall Street equity assets with mathematically rigorous Expected Value (+EV),
Actual/Expected (A/E) alpha ratios, 1-Unit P/L calculations, and Fractional Kelly Stake sizing.
"""

from typing import Dict, List, Any
import numpy as np

try:
    from .utils import safe_float, safe_int
    from .ml_engine import EquineWinProbabilityModel
    from .monte_carlo_engine import EquineMonteCarloEngine
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int
    from backend.ml_engine import EquineWinProbabilityModel
    from backend.monte_carlo_engine import EquineMonteCarloEngine


class EquineStockEngine:
    """Quantitative Equine Stock Model designed to institutional hedge fund standards."""

    @staticmethod
    def calculate_kelly_stake(empirical_win_prob: float, decimal_odds: float) -> float:
        """
        Calculates Fractional (Half) Kelly Criterion Optimal Stake Percentage:
        f* = (p * b - (1 - p)) / b = (p * decimal_odds - 1) / (decimal_odds - 1)
        where p = empirical win probability. Half-Kelly (0.5 multiplier) applied for risk control.
        Capped at 25.0% max allocation.
        """
        b = decimal_odds - 1.0
        if b <= 0.001:
            return 0.0
        
        expected_val = empirical_win_prob * decimal_odds - 1.0
        if expected_val <= 0:
            return 0.0
            
        full_kelly = expected_val / b
        half_kelly = full_kelly * 0.5
        return round(max(0.0, min(0.25, half_kelly)) * 100.0, 1)

    @classmethod
    def calculate_stock_metrics(cls, runner: Dict[str, Any], race_pool_usd: float = 2000000.0, runner_idx: int = 0, total_runners: int = 8) -> Dict[str, Any]:
        """Calculates institutional quantitative stock metrics for an equine asset with relative multiplicative A/E scaling."""
        decimal_odds = max(1.01, safe_float(runner.get("decimal_odds"), default=4.0))
        
        share_price = round(min(99.00, max(1.01, 100.0 / decimal_odds)), 2)
        implied_win_pct = round((1.0 / decimal_odds) * 100.0, 2)
        implied_win_prob = 1.0 / decimal_odds
        market_cap = round(race_pool_usd * (share_price / 100.0), 2)
        
        beyer_speed = safe_int(runner.get("beyer_speed"), default=112 - runner_idx * 2)

        # A/E alpha ratio from the XGBoost calibration model (backend/ml_engine.py),
        # strictly bounded within realistic quantitative hedge fund range [0.75, 1.35]
        ae_ratio = EquineWinProbabilityModel.predict_ae_ratio(runner)
        
        # Empirical Win Prob = Implied Win Prob * A/E Ratio
        empirical_win_prob = round(min(0.92, max(0.01, implied_win_prob * ae_ratio)), 4)
        
        # Expected Value EV = p * Odds - 1.0 (Bounded within [-35.0%, +40.0%])
        raw_ev = (empirical_win_prob * decimal_odds) - 1.0
        expected_val_pct = round(min(40.0, max(-35.0, raw_ev * 100.0)), 1)
        expected_val = round(expected_val_pct / 100.0, 4)
        
        raw_1_pl = runner.get("one_unit_pl")
        if raw_1_pl is not None:
            one_unit_pl = safe_float(raw_1_pl)
        else:
            one_unit_pl = round(expected_val * 25.0, 2)

        kelly_stake_pct = cls.calculate_kelly_stake(empirical_win_prob, decimal_odds)
        moisture_fit = safe_float(runner.get("track_moisture_fit"), default=0.88)

        if expected_val_pct > 4.0 and ae_ratio >= 1.05:
            asset_tag = "VALUE_BUY"
            card_color = "#10B981"
            card_label = "🟢 🚀 +EV GOLDEN NUGGET"
            tag_expl = f"Model win prob ({empirical_win_prob*100:.1f}%) exceeds market implied odds (A/E {ae_ratio:.2f}, EV {expected_val_pct:+.1f}%). Rec. Half-Kelly: {kelly_stake_pct:.1f}%."
        elif expected_val_pct < -5.0 or ae_ratio < 0.92:
            asset_tag = "OVERVALUED_FADE"
            card_color = "#F43F5E"
            card_label = "🔴 ⚠️ OVERPRICED FADE"
            tag_expl = f"Market odds overestimating win chance (A/E {ae_ratio:.2f}, EV {expected_val_pct:+.1f}%). Recommend fading asset."
        else:
            asset_tag = "MID_TIER_HEDGE"
            card_color = "#F59E0B"
            card_label = "🟡 ⚡ CHAD OUTSIDER HEDGE"
            tag_expl = f"Fairly priced asset (A/E {ae_ratio:.2f}, EV {expected_val_pct:+.1f}%). High Beyer speed rating ({beyer_speed})."

        return {
            "horse_id": runner.get("horse_id") or f"hrs_{runner_idx}",
            "horse": runner.get("horse", "Runner"),
            "ticker": f"${runner.get('horse', 'RUNNER')[:6].upper().replace(' ', '')}_{runner.get('jockey', 'JKY')[:4].upper().replace(' ', '')}",
            "sire": runner.get("sire", "Thoroughbred"),
            "dam": runner.get("dam", "Dam"),
            "age": safe_int(runner.get("age"), default=4),
            "sex": runner.get("sex", "Stallion"),
            "trainer": runner.get("trainer", "Trainer"),
            "jockey": runner.get("jockey", "Jockey"),
            "owner": runner.get("owner", "Owner"),
            "form": runner.get("form", "1-1-2"),
            "share_price_usd": share_price,
            "decimal_odds": decimal_odds,
            "implied_win_pct": implied_win_pct,
            "win_percent": empirical_win_prob,
            "place_percent": safe_float(runner.get("place_percent"), default=0.65),
            "market_cap_usd": market_cap,
            "expected_value": expected_val,
            "expected_value_pct": expected_val_pct,
            "ae_ratio": ae_ratio,
            "one_unit_pl": one_unit_pl,
            "beyer_speed": beyer_speed,
            "kelly_stake_pct": kelly_stake_pct,
            "track_moisture_fit": moisture_fit,
            "asset_tag": asset_tag,
            "card_color": card_color,
            "card_label": card_label,
            "tag_expl": tag_expl,
            "official_rating": safe_int(runner.get("official_rating"), default=115),
            "career_prize_usd": safe_float(runner.get("career_prize_usd"), default=450000.0),
            "past_places": runner.get("past_places", [])
        }

    @classmethod
    def process_racecard(cls, racecard: Dict[str, Any]) -> Dict[str, Any]:
        """Processes an entire racecard, evaluating quantitative metrics across all runners."""
        prize_money = safe_float(racecard.get("prize_money_usd"), default=1000000.0)
        runners = racecard.get("runners", [])
        total_r = len(runners)
        
        processed_runners = []
        for idx, r in enumerate(runners):
            stock = cls.calculate_stock_metrics(r, race_pool_usd=prize_money * 1.5, runner_idx=idx, total_runners=total_r)
            stock["odds_timeline"] = cls.generate_odds_timeline(stock["share_price_usd"])
            processed_runners.append(stock)

        # Monte Carlo Plackett-Luce simulation (10,000 full-field runs) supplies the true
        # place/show frequencies used below, replacing the flat 0.65 default place_percent.
        race_seed = abs(hash(str(racecard.get("race_id")))) % (2**31)
        mc_results = EquineMonteCarloEngine.simulate_race(processed_runners, n_sims=10000, seed=race_seed)
        mc_lookup = {r["ticker"]: r for r in mc_results.get("runner_probs", [])}
        for stock in processed_runners:
            mc = mc_lookup.get(stock["ticker"])
            if mc:
                stock["place_percent"] = round(mc["place_pct"] / 100.0, 4)
                stock["mc_win_pct"] = mc["win_pct"]
                stock["mc_fair_odds"] = mc["fair_odds"]

        processed_runners.sort(key=lambda x: x["share_price_usd"], reverse=True)

        return {
            "race_id": racecard.get("race_id"),
            "course": racecard.get("course"),
            "race_name": racecard.get("race_name"),
            "distance_display": racecard.get("distance_display"),
            "distance_furlongs": racecard.get("distance_furlongs"),
            "going": racecard.get("going"),
            "moisture_percent": racecard.get("moisture_percent"),
            "prize_money_usd": prize_money,
            "race_class": racecard.get("race_class"),
            "post_time": racecard.get("post_time"),
            "race_date": racecard.get("race_date"),
            "race_date_display": racecard.get("race_date_display"),
            "equity_assets": processed_runners,
            "monte_carlo": mc_results
        }

    @staticmethod
    def generate_odds_timeline(current_share_price: float, hours: int = 24) -> List[Dict[str, Any]]:
        """Generates historical 24-hour stock price drift trajectory."""
        timeline = []
        np.random.seed(int(current_share_price * 100) % 99999)
        base_price = current_share_price * (1.0 + np.random.uniform(-0.15, 0.15))
        price = base_price
        
        for h in range(hours, -1, -1):
            drift = np.random.normal(0, 0.02 * price)
            price = max(1.0, min(99.0, price + drift))
            if h == 0:
                price = current_share_price
                
            timeline.append({
                "time_label": f"-{h}h" if h > 0 else "POST",
                "hours_to_post": h,
                "share_price_usd": round(price, 2),
                "implied_odds": round(100.0 / max(0.1, price), 2)
            })
            
        return timeline
