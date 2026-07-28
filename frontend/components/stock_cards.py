"""
SEABISCUIT - Ultra-Compact Horse Asset Cards Component (No Text Overlap & High Clarity)
"""

import streamlit as st
import textwrap
from typing import List, Dict, Any

try:
    from backend.utils import safe_float, safe_int
except (ImportError, ValueError):
    from utils import safe_float, safe_int


def render_stock_asset_cards(assets: List[Dict[str, Any]]) -> None:
    """Renders high-density equine analytics cards with zero text overlap."""
    st.markdown("<h5 style='color: #0F172A; font-weight: 900; margin-bottom: 14px;'>🏇 RUNNER EQUITIES & QUANTITATIVE ALPHAS</h5>", unsafe_allow_html=True)

    if not assets:
        st.info("No active runner equities found for this racecard.")
        return

    cols = st.columns(2)

    for idx, asset in enumerate(assets):
        if not isinstance(asset, dict):
            continue

        col = cols[idx % 2]
        
        tag = asset.get("asset_tag", "MID_TIER_HEDGE")
        if tag == "VALUE_BUY":
            card_class = "gaming-card-green"
            badge_html = '<span class="badge-pepite">🟢 🚀 +EV GOLDEN NUGGET</span>'
        elif tag == "OVERVALUED_FADE":
            card_class = "gaming-card-red"
            badge_html = '<span class="badge-piege">🔴 💣 OVERPRICED FADE</span>'
        else:
            card_class = "gaming-card-gold"
            badge_html = '<span class="badge-outsider">🟡 🛡️ VALUE HEDGE</span>'

        share_price = safe_float(asset.get("share_price_usd"), default=25.0)
        decimal_odds = safe_float(asset.get("decimal_odds"), default=4.0)
        win_percent = safe_float(asset.get("win_percent"), default=0.25)
        kelly_stake = safe_float(asset.get("kelly_stake_pct"), default=0.0)
        ae_ratio = safe_float(asset.get("ae_ratio"), default=1.0)
        expected_val = safe_float(asset.get("expected_value"), default=0.0) * 100.0
        beyer_speed = safe_int(asset.get("beyer_speed"), default=100)
        one_unit_pl = safe_float(asset.get("one_unit_pl"), default=0.0)
        dividend_yield = safe_float(asset.get("dividend_yield_pct"), default=0.0)

        one_unit_col = "#059669" if one_unit_pl > 0 else "#E11D48"
        tag_expl = str(asset.get("tag_expl", "Quantitative asset metrics calculated."))

        ticker = str(asset.get("ticker", "$RUNNER"))
        horse_name = str(asset.get("horse", "Runner"))
        sire = str(asset.get("sire", "Sire"))
        dam = str(asset.get("dam", "Dam"))
        jockey = str(asset.get("jockey", "Jockey"))
        trainer = str(asset.get("trainer", "Trainer"))

        card_html = textwrap.dedent(f"""
<div class="{card_class}" style="padding: 16px; margin-bottom: 14px; display: flex; flex-direction: column; justify-content: space-between;">
<div>

<!-- TOP HEADER ROW -->
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
<div style="max-width: 65%;">
<span style="color: #4338CA; font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 1.1rem; word-break: break-all;">{ticker}</span>
<span style="font-weight: 900; font-size: 1.25rem; color: #0F172A; margin-left: 6px; display: inline-block;">{horse_name}</span>
<div style="font-size: 0.8rem; color: #64748B; margin-top: 2px;">({sire} x {dam})</div>
</div>
<div style="text-align: right; font-family: 'JetBrains Mono', monospace; min-width: 100px;">
<div style="font-size: 1.5rem; font-weight: 900; color: #0F172A; line-height: 1.1;">${share_price:.2f}</div>
<div style="font-size: 0.82rem; color: #475569; margin-top: 2px;">Odds: <b style="color: #4338CA;">{decimal_odds:.2f}</b></div>
</div>
</div>

<!-- BADGE & KELLY ROW -->
<div style="margin: 10px 0; display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; padding: 6px 12px; border-radius: 6px; border: 1px solid #E2E8F0; flex-wrap: wrap; gap: 6px;">
{badge_html}
<span style="font-family: 'JetBrains Mono', monospace; color: #0369A1; font-size: 0.82rem; font-weight: 800; background: #E0F2FE; padding: 3px 8px; border-radius: 4px; white-space: nowrap;">
⚡ HALF-KELLY: {kelly_stake:.1f}%
</span>
</div>

<!-- QUANT INSIGHT ROW -->
<div style="font-size: 0.85rem; color: #334155; margin-bottom: 10px; background: #F1F5F9; padding: 8px 10px; border-radius: 6px; border-left: 3px solid #4338CA; line-height: 1.4;">
💡 <b>Quant Insight</b>: EV: <b style="color: {'#059669' if expected_val > 0 else '#E11D48'};">{expected_val:+.1f}%</b> | A/E Ratio: <b>{ae_ratio:.2f}</b>. {tag_expl}
</div>

<!-- 4 STAT PILLS GRID -->
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 6px;">
<div class="quant-pill" style="padding: 6px 4px;">
<div style="color: #64748B; font-size: 0.65rem; font-weight: 800;">A/E EDGE</div>
<div style="color: #0F172A; font-weight: 900; font-size: 1.0rem;">{ae_ratio:.2f}</div>
</div>
<div class="quant-pill" style="padding: 6px 4px;">
<div style="color: #64748B; font-size: 0.65rem; font-weight: 800;">BEYER SPEED</div>
<div style="color: #0284C7; font-weight: 900; font-size: 1.0rem;">{beyer_speed}</div>
</div>
<div class="quant-pill" style="padding: 6px 4px;">
<div style="color: #64748B; font-size: 0.65rem; font-weight: 800;">1-UNIT P/L</div>
<div style="color: {one_unit_col}; font-weight: 900; font-size: 1.0rem;">${one_unit_pl:+.2f}</div>
</div>
<div class="quant-pill" style="padding: 6px 4px;">
<div style="color: #64748B; font-size: 0.65rem; font-weight: 800;">EXPECTED VAL</div>
<div style="color: {'#059669' if expected_val > 0 else '#E11D48'}; font-weight: 900; font-size: 1.0rem;">{expected_val:+.1f}%</div>
</div>
</div>
</div>

<!-- FOOTER ROW -->
<div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #E2E8F0; font-size: 0.82rem; color: #475569; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 4px;">
<span>👤 Jockey: <b style="color: #0F172A;">{jockey}</b></span>
<span>👔 Trainer: <b style="color: #0F172A;">{trainer}</b></span>
</div>
</div>
""").strip()

        with col:
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"🔍 INSPECT {ticker}", key=f"btn_inspect_{ticker}_{idx}", width="stretch"):
                st.session_state["selected_horse_ticker"] = ticker
                st.rerun()
