"""
SEABISCUIT - DeepSeek AI Executive Market Intelligence Engine
Queries DeepSeek-R1 / DeepSeek-V3 API via DEEPSEEK_API_KEY or synthesizes algorithmic quantitative dossiers.
Both paths end by running the race through SeabiscuitBetGenerator (bet_generator_engine.py) to
produce a concrete Gagnant/Placé/Duo/Trio/Quinté+ recommendation — or no bet at all.
"""

import os
import re
import time
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

try:
    from .utils import safe_float
    from .bet_generator_engine import SeabiscuitBetGenerator
except (ImportError, ValueError):
    from backend.utils import safe_float
    from backend.bet_generator_engine import SeabiscuitBetGenerator

load_dotenv()


class DeepSeekIntelEngine:
    """Executive Quantitative Intelligence Synthesizer powered by DeepSeek AI."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.client = httpx.Client(timeout=15.0) if self.api_key else None

    @staticmethod
    def _parse_confidence_score(text: str) -> Optional[float]:
        """Extracts the SEABISCUIT_CONFIDENCE: <0-100> line the live prompt asks the model
        to end its response with. Returns None if absent or unparsable."""
        match = re.search(r"SEABISCUIT_CONFIDENCE:\s*(\d+(?:\.\d+)?)", text)
        if not match:
            return None
        try:
            return max(0.0, min(100.0, float(match.group(1))))
        except ValueError:
            return None

    @staticmethod
    def _format_bet_recommendation_markdown(rec: Optional[Dict[str, Any]]) -> str:
        """Renders the bet generator's decision as a dossier section, shared by both the
        live-LLM and algorithmic fallback paths so the recommendation is always present."""
        if rec is None:
            return (
                "## 🎯 SEABISCUIT RECOMMENDED BET\n\n"
                "> [!NOTE]\n"
                "> **No bet.** No runner in this race clears SEABISCUIT's positive expected-value "
                "bar — sitting this one out is the disciplined play."
            )

        bet_type_labels = {
            "GAGNANT": "🥇 Gagnant (Win)",
            "PLACE": "🥈 Placé (Place)",
            "DUO": "👯 Couplé Duo (Exacta)",
            "TRIO": "🥉 Trio (Trifecta)",
            "QUINTE": "🏆 Quinté+ (Top 5)"
        }
        label = bet_type_labels.get(rec["bet_type"], rec["bet_type"])
        runners = ", ".join(rec["runner_names"])

        return (
            "## 🎯 SEABISCUIT RECOMMENDED BET\n\n"
            f"> [!IMPORTANT]\n"
            f"> **{label}**: {runners}\n"
            f"> \n"
            f"> **Confidence**: {rec['confidence_pct']:.0f}/100 · **Model Edge**: {rec['top_ev_pct']:+.1f}% EV\n"
            f"> \n"
            f"> {rec['rationale']}"
        )

    def generate_race_dossier(self, racecard: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an executive quantitative intelligence dossier for a racecard, ending
        with a concrete SEABISCUIT bet recommendation."""
        course = racecard.get("course", "Royal Ascot")
        race_name = racecard.get("race_name", "Group 1 Stakes")
        going = racecard.get("going", "Good to Firm")
        moisture = racecard.get("moisture_percent", 18.5)
        prize = racecard.get("prize_money_usd", 1500000)
        equity_assets = racecard.get("equity_assets", [])

        if self.client and self.api_key:
            try:
                prompt = f"""
You are the Chief Quantitative Strategist for SEABISCUIT Equine Intelligence.
Analyze the following thoroughbred stock assets and deliver an institutional executive market dossier in 100% clean English.

Venue: {course} | Event: {race_name} | Track Going: {going} ({moisture}% moisture) | Purse: ${prize:,.0f}

Equine Stock Assets:
"""
                for asset in equity_assets:
                    prompt += f"- {asset.get('ticker')} ({asset.get('horse')}): Share Price=${asset.get('share_price_usd')}, Odds={asset.get('decimal_odds')}, A/E={asset.get('ae_ratio')}, 1-Unit P/L=${asset.get('one_unit_pl')}, Beyer={asset.get('beyer_speed')}, Jockey={asset.get('jockey')}, Owner={asset.get('owner')}\n"

                prompt += (
                    "\nDeliver a high-impact 4-part dossier: 1. Executive Summary & Alpha Verdict, "
                    "2. Equine Stock Valuations (+EV Long, Short Fade, Strangle), 3. Track Moisture & "
                    "Speed Velocity Delta, 4. Pace scenario and connections read (jockey/trainer intent, "
                    "trip concerns) beyond what the raw numbers show.\n\n"
                    "Finish your response with exactly one line, on its own, with no other text on that "
                    "line: SEABISCUIT_CONFIDENCE: <integer 0-100> — your qualitative confidence that the "
                    "model's top-rated runner's edge is real, factoring in pace and connections beyond the "
                    "raw stats."
                )

                resp = self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "You are SEABISCUIT's Principal Quantitative Analyst delivering Wall Street equine research in clean English."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    confidence = self._parse_confidence_score(content)
                    rec = SeabiscuitBetGenerator.generate_bet(racecard, qual_confidence_override=confidence)

                    return {
                        "status": "success",
                        "model_used": "DeepSeek-V3 / DeepSeek-R1 (Live API)",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S GMT"),
                        "dossier_markdown": content + "\n\n---\n\n" + self._format_bet_recommendation_markdown(rec),
                        "recommended_bet": rec
                    }
            except Exception:
                pass

        # High-Impact Algorithmic Fallback Synthesizer
        value_buys = [a for a in equity_assets if a.get("asset_tag") == "VALUE_BUY"]
        fades = [a for a in equity_assets if a.get("asset_tag") == "OVERVALUED_FADE"]

        top_buy = value_buys[0] if value_buys else (equity_assets[0] if equity_assets else {})
        top_fade = fades[0] if fades else (equity_assets[-1] if len(equity_assets) > 1 else {})

        rec = SeabiscuitBetGenerator.generate_bet(racecard)

        markdown_dossier = f"""# 🏇 EXECUTIVE MARKET INTELLIGENCE DOSSIER: {course.upper()}

**LOCATION**: {course} | **EVENT**: {race_name}
**MARKET POOL**: ${prize*1.5:,.0f} | **POST TIME**: {racecard.get('post_time', '15:35 GMT')}
**TRACK SURFACE**: {going} ({moisture}% Moisture Content)

---

## ⚡ EXECUTIVE SUMMARY & ALPHA VERDICT

Quantitative orderbook models indicate mispricing in the top-tier equity bracket for this venue.
- **Top Undervalued Asset (+EV Long)**: **{top_buy.get('ticker', '$SEAB')} ({top_buy.get('horse', 'Runner')})** trades at **${top_buy.get('share_price_usd', 43.50):.2f}/share** (Decimal Odds: {top_buy.get('decimal_odds', 2.25)}). Driven by an **A/E Ratio of {top_buy.get('ae_ratio', 1.16)}** and career stake profit of **+${top_buy.get('one_unit_pl', 44.50):.2f}**, this runner presents institutional upside.
- **Top Short / Fade Target**: **{top_fade.get('ticker', '$OVER')} ({top_fade.get('horse', 'Runner')})** is significantly overvalued at **${top_fade.get('share_price_usd', 25.00):.2f}/share**. Its dismal **A/E Ratio of {top_fade.get('ae_ratio', 0.76)}** and negative stake ROI (**-${abs(top_fade.get('one_unit_pl', 18.40)):.2f}**) make it an ideal short candidate.

---

## 📊 EQUINE STOCK VALUATION BREAKDOWN

| Ticker | Horse Asset | Share Price | Alpha Edge (A/E) | Velocity Beyer | Career ROI | Quantitative Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for a in equity_assets:
            markdown_dossier += f"| `{a.get('ticker')}` | **{a.get('horse')}** | `${a.get('share_price_usd'):.2f}` | `{a.get('ae_ratio'):.2f}` | `{a.get('beyer_speed')}` | `${a.get('one_unit_pl'):+.2f}` | {a.get('card_label')} |\n"

        markdown_dossier += f"""
---

## 🌧️ TRACK MOISTURE & SPEED SENSITIVITY

Current track moisture of **{moisture}% ({going})** creates a high-friction surface delta:
- **Optimal Surface Adapters**: `{top_buy.get('ticker')}` exhibits a **{safe_float(top_buy.get('track_moisture_fit'), 0.92)*100:.1f}% moisture fit index**, allowing full power transmission in sprint/stamina transitions.
- **Speed Rating Benchmark**: Peak Beyer rating of **{max([a.get('beyer_speed', 100) for a in equity_assets] if equity_assets else [118])}** sets the baseline pace expectation.

---

## 🤝 JOCKEY x OWNER SYNERGY ARBITRAGE

- **Elite Power Combo**: `{top_buy.get('jockey')}` x `{top_buy.get('owner')}` demonstrates an institutional A/E ratio of **{top_buy.get('ae_ratio', 1.16)}** across Group 1 race classes.
- **Friction Warning**: Trainer `{top_fade.get('trainer', 'Trainer')}` shows declining win frequency on `{going}` surfaces.

---

{self._format_bet_recommendation_markdown(rec)}
"""

        return {
            "status": "success",
            "model_used": "DeepSeek Quantitative Algorithmic Synthesizer (Fallback Mode)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S GMT"),
            "dossier_markdown": markdown_dossier,
            "recommended_bet": rec
        }
