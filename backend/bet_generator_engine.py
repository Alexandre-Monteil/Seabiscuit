"""
SEABISCUIT - Bet Generator Engine
Decides WHICH bet type (Gagnant, Duo, or Quinté+) to place on a race, or whether to skip it
entirely — instead of always backing whichever single runner has the highest EV%.
"""

from typing import Dict, Any, Optional

try:
    from .utils import safe_float
except (ImportError, ValueError):
    from backend.utils import safe_float


class SeabiscuitBetGenerator:
    """
    Blends quantitative signals (EV%, Monte Carlo win-share gap between the top runners) with
    a qualitative confidence read (recent form, A/E divergence from the market, ground fit —
    the same categories a handicapper or an AI dossier would weigh) to pick a bet type and
    target runner(s) for a race, or to recommend no bet at all when there's no edge.

    The qualitative confidence is computed by a deterministic proxy by default, so this runs
    fast and reproducibly over hundreds of backtest races with no network calls. When a live
    DeepSeek dossier is available (see deepseek_intel_engine.py), its own confidence read can
    be passed in via `qual_confidence_override` to drive the same decision tree with genuine
    LLM judgment instead of the heuristic proxy.
    """

    MIN_EV_PCT_TO_BET = 0.0
    DOMINANT_WIN_GAP_PCT = 15.0

    @classmethod
    def _qualitative_confidence(cls, runner: Dict[str, Any]) -> float:
        """Deterministic proxy for the qualitative factors a form/ground/connections read
        would weigh: recent form trend, A/E divergence from the market, and going affinity."""
        ae_ratio = safe_float(runner.get("ae_ratio"), default=1.0)
        form = str(runner.get("form", ""))
        moisture_fit = safe_float(runner.get("track_moisture_fit"), default=0.85)

        score = 50.0
        score += max(-20.0, min(20.0, (ae_ratio - 1.0) * 100.0))
        score += 10.0 if "1" in form else (-10.0 if ("0" in form or "9" in form) else 0.0)
        score += max(-10.0, min(10.0, (moisture_fit - 0.85) * 100.0))
        return max(0.0, min(100.0, score))

    @classmethod
    def generate_bet(cls, racecard: Dict[str, Any], qual_confidence_override: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Returns a recommended bet {bet_type, runners, runner_names, confidence_pct,
        top_ev_pct, rationale}, or None if the race offers no positive-EV opportunity."""
        assets = [a for a in racecard.get("equity_assets", []) if isinstance(a, dict)]
        if len(assets) < 2:
            return None

        ranked = sorted(
            assets,
            key=lambda a: safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), default=-99.0),
            reverse=True
        )
        top1 = ranked[0]
        ev1 = safe_float(top1.get("expected_value_pct") or (safe_float(top1.get("expected_value")) * 100.0), default=-99.0)

        if ev1 <= cls.MIN_EV_PCT_TO_BET:
            return None

        n = len(ranked)
        qual_confidence = qual_confidence_override if qual_confidence_override is not None else cls._qualitative_confidence(top1)

        win1 = safe_float(top1.get("mc_win_pct"), default=safe_float(top1.get("win_percent"), 0.0) * 100.0)
        win2 = safe_float(ranked[1].get("mc_win_pct"), default=safe_float(ranked[1].get("win_percent"), 0.0) * 100.0)
        win_gap = win1 - win2

        positive_ev_count = sum(
            1 for a in ranked
            if safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), 0.0) > cls.MIN_EV_PCT_TO_BET
        )

        # Dominant favorite: bet the single runner to win. Checked first — spreading a
        # near-certain favorite's edge across a combo bet would waste it. If the qualitative
        # read disagrees with a supposedly dominant favorite, that disagreement itself is a
        # reason to sit out rather than downgrade to a weaker bet type.
        if win_gap >= cls.DOMINANT_WIN_GAP_PCT:
            if qual_confidence < 40.0:
                return None
            bet_type = "GAGNANT"
            runners = [top1]
            rationale = (f"{top1.get('horse')} dominates the field (model win share {win1:.1f}% vs "
                         f"{win2:.1f}% for 2nd) with quant/qualitative agreement ({qual_confidence:.0f}/100).")
        # Open race (no dominant favorite): scope the bet to how many runners actually show
        # an edge — a deep, competitive field with several positive-EV runners suits a
        # Quinté+, a narrower edge suits a Duo, and a single standout without a big enough
        # gap to call "dominant" still just backs that runner to win.
        elif n >= 8 and positive_ev_count >= 3 and qual_confidence >= 55.0:
            bet_type = "QUINTE"
            runners = ranked[:5]
            rationale = (f"Large, competitive field ({n} runners) with {positive_ev_count} runners showing "
                         f"edge and reasonable model confidence ({qual_confidence:.0f}/100) — Quinté+ on the top 5.")
        elif n >= 3 and positive_ev_count >= 2:
            bet_type = "DUO"
            runners = ranked[:2]
            rationale = (f"{top1.get('horse')} and {ranked[1].get('horse')} are close in model win share "
                         f"({win1:.1f}% vs {win2:.1f}%) — a Duo captures the uncertainty between them.")
        else:
            bet_type = "GAGNANT"
            runners = [top1]
            rationale = f"{top1.get('horse')} is the model's only standout pick in this race — a straight Gagnant."

        return {
            "bet_type": bet_type,
            "runners": [r.get("ticker") for r in runners],
            "runner_names": [r.get("horse", "Runner") for r in runners],
            "confidence_pct": round(qual_confidence, 1),
            "top_ev_pct": round(ev1, 1),
            "rationale": rationale
        }
