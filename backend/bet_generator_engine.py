"""
SEABISCUIT - Bet Generator Engine
Decides whether to place a straight Gagnant (win) bet on a race's top-rated sane-priced
runner, or to skip it entirely — instead of always backing whichever runner has the
highest nominal EV%, which was dominated by longshots (see MAX_ODDS_TO_BET below).
"""

from typing import Dict, Any, Optional

try:
    from .utils import safe_float
except (ImportError, ValueError):
    from backend.utils import safe_float


class SeabiscuitBetGenerator:
    """
    Gagnant-only by design: Duo/Trio/Quinté+ combo bets are priced against our OWN
    model-derived fair odds (no real pool dividend data is available to backtest or
    validate them against), so any "edge" on them is circular by construction. Gagnant
    is the only bet type where we compare a genuine model probability against a real
    market price.

    Empirically tested against ~1,850 real GB results (see project history): neither
    "outsider with good recent form" nor "class drop" showed better value than the
    market price — if anything, both were slightly worse (favourite-longshot bias, and
    the market already pricing in an obvious class drop). The one signal that held up
    was first-time headgear (A/E ~0.99 vs ~0.87 for no change), used here as a
    qualitative confidence boost. None of this amounts to a proven positive edge — the
    market is largely efficient — so MIN_EV_PCT_TO_BET and MAX_ODDS_TO_BET exist to
    keep the generator selective rather than betting on noise.
    """

    # Any EV > 0% used to qualify, which let pure model noise (a fraction of a percent) trigger
    # bets. Real markets charge a takeout/vig, so a signal needs enough margin to survive being
    # slightly wrong. The real-data-trained model's output is coarse-grained (bin-calibrated,
    # shallow trees) and currently tops out around 3% EV for sanely-priced runners in typical
    # data — so 2.0% is selective without colliding with that ceiling.
    MIN_EV_PCT_TO_BET = 2.0

    # EV = p * odds - 1 is multiplicative: at long odds, a small, ordinary A/E miscalibration
    # (the model is only ever accurate to within some margin) turns into a huge apparent EV%
    # purely from the odds multiplier, not genuine value — and the well-documented
    # favourite-longshot bias says longshots are structurally OVER-priced by the market, not
    # under-priced, so apparent "value" way out in the odds is the least trustworthy kind.
    # Runners priced longer than this are excluded from consideration entirely.
    MAX_ODDS_TO_BET = 20.0

    @classmethod
    def _qualitative_confidence(cls, runner: Dict[str, Any]) -> float:
        """Deterministic proxy for the qualitative factors a form/ground/connections read
        would weigh: recent form trend, A/E divergence from the market, going affinity, and
        first-time headgear (the one equipment/intent signal that held up empirically)."""
        ae_ratio = safe_float(runner.get("ae_ratio"), default=1.0)
        form = str(runner.get("form", ""))
        moisture_fit = safe_float(runner.get("track_moisture_fit"), default=0.85)

        score = 50.0
        score += max(-20.0, min(20.0, (ae_ratio - 1.0) * 100.0))
        score += 10.0 if "1" in form else (-10.0 if ("0" in form or "9" in form) else 0.0)
        score += max(-10.0, min(10.0, (moisture_fit - 0.85) * 100.0))
        score += 15.0 if runner.get("first_time_headgear") else 0.0
        return max(0.0, min(100.0, score))

    @classmethod
    def generate_bet(cls, racecard: Dict[str, Any], qual_confidence_override: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Returns a recommended Gagnant bet {bet_type, runners, runner_names, confidence_pct,
        top_ev_pct, rationale}, or None if the race offers no qualifying opportunity."""
        assets = [a for a in racecard.get("equity_assets", []) if isinstance(a, dict)]
        if len(assets) < 2:
            return None

        # Exclude longshots from consideration entirely (see MAX_ODDS_TO_BET) before ranking.
        sane_pool = [a for a in assets if safe_float(a.get("decimal_odds"), default=999.0) <= cls.MAX_ODDS_TO_BET]
        if not sane_pool:
            return None

        ranked = sorted(
            sane_pool,
            key=lambda a: safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), default=-99.0),
            reverse=True
        )
        top1 = ranked[0]
        ev1 = safe_float(top1.get("expected_value_pct") or (safe_float(top1.get("expected_value")) * 100.0), default=-99.0)

        if ev1 <= cls.MIN_EV_PCT_TO_BET:
            return None

        qual_confidence = qual_confidence_override if qual_confidence_override is not None else cls._qualitative_confidence(top1)

        gear_note = " First-time headgear adds a genuine (if modest) real-data-backed edge." if top1.get("first_time_headgear") else ""
        rationale = (f"{top1.get('horse')} is the model's top sanely-priced pick (odds ≤ {cls.MAX_ODDS_TO_BET:.0f}-1, "
                     f"EV {ev1:+.1f}%, confidence {qual_confidence:.0f}/100).{gear_note}")

        return {
            "bet_type": "GAGNANT",
            "runners": [top1.get("ticker")],
            "runner_names": [top1.get("horse", "Runner")],
            "confidence_pct": round(qual_confidence, 1),
            "top_ev_pct": round(ev1, 1),
            "rationale": rationale
        }
