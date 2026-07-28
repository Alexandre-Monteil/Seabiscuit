"""
SEABISCUIT - Active Horse Asset Cards Grid Component (Plain Language & EV-Sorted Architecture)
Renders high-contrast equity asset cards sorted strictly by Expected Value (EV %) descending with actionable labels.
"""

from typing import List, Dict, Any
import streamlit as st

try:
    from backend.utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int


def render_stock_asset_cards(equity_assets: List[Dict[str, Any]]):
    """Renders runner cards sorted strictly by EV % descending with crystal-clear actionable labels."""
    if not equity_assets:
        st.info("No active runners available for this race.")
        return

    # SORT RUNNERS STRICTLY BY EXPECTED VALUE (EV %) DESCENDING
    sorted_assets = sorted(
        equity_assets,
        key=lambda a: safe_float(a.get("expected_value_pct") if isinstance(a, dict) else 0.0, default=0.0),
        reverse=True
    )

    st.markdown("<h4 style='color: #0F172A; font-weight: 900; margin-bottom: 14px;'>🏇 RUNNERS CLASSIFIED BY EXPECTED VALUE (HIGHEST +EV VALUE FIRST)</h4>", unsafe_allow_html=True)

    cols = st.columns(3)

    for idx, asset in enumerate(sorted_assets):
        if not isinstance(asset, dict):
            continue

        col = cols[idx % 3]

        horse_name = str(asset.get("horse", "Runner"))
        ticker = str(asset.get("ticker", "$RUNNER"))
        sire = str(asset.get("sire", "Thoroughbred"))
        dam = str(asset.get("dam", "Dam"))
        jockey = str(asset.get("jockey", "Jockey"))
        trainer = str(asset.get("trainer", "Trainer"))
        
        decimal_odds = safe_float(asset.get("decimal_odds"), default=4.0)
        share_price = safe_float(asset.get("share_price_usd"), default=25.0)
        ev_pct = safe_float(asset.get("expected_value_pct") or (safe_float(asset.get("expected_value")) * 100.0), default=0.0)
        ae_ratio = safe_float(asset.get("ae_ratio"), default=1.0)
        beyer_speed = safe_int(asset.get("beyer_speed"), default=110)
        one_unit_pl = safe_float(asset.get("one_unit_pl"), default=0.0)
        kelly_stake = safe_float(asset.get("kelly_stake_pct"), default=0.0)

        # Clear Actionable Labels & Colors
        if ev_pct > 4.0:
            card_border = "#10B981"
            badge_bg = "#10B981"
            badge_text = "🟢 🚀 TOP VALUE BET (+EV)"
            badge_sub = "Bookmakers are underestimating this horse!"
        elif ev_pct < -5.0:
            card_border = "#F43F5E"
            badge_bg = "#F43F5E"
            badge_text = "🔴 ⚠️ OVERPRICED TRAP (-EV)"
            badge_sub = "Odds are too low compared to real winning chance!"
        else:
            card_border = "#F59E0B"
            badge_bg = "#F59E0B"
            badge_text = "🟡 ⚡ FAIR VALUE HEDGE"
            badge_sub = "Odds match estimated probability."

        ev_color = "#059669" if ev_pct > 0 else "#E11D48"
        pl_color = "#059669" if one_unit_pl > 0 else "#E11D48"

        card_html = f"""<div style="background: #FFFFFF; border: 2.5px solid {card_border}; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #4338CA;">#{idx+1} {ticker}</span>
<span style="background: {badge_bg}; color: #FFFFFF; font-weight: 900; padding: 3px 8px; border-radius: 6px; font-size: 0.76rem;">{badge_text}</span>
</div>
<div style="font-size: 1.25rem; font-weight: 900; color: #0F172A; line-height: 1.2;">{horse_name}</div>
<div style="font-size: 0.80rem; color: #64748B; margin-bottom: 10px;">({sire} x {dam})</div>

<!-- Price & Odds Header Banner -->
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Equivalent Price / $100</div>
<div style="font-size: 1.35rem; font-weight: 900; color: #0F172A;">${share_price:.2f}</div>
</div>
<div style="text-align: right;">
<div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Bookmaker Odds</div>
<div style="font-size: 1.35rem; font-weight: 900; color: #0284C7;">{decimal_odds:.2f}</div>
</div>
</div>

<!-- 4 Actionable Metrics Grid -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
<div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; text-align: center;">
<div style="font-size: 0.70rem; color: #475569; font-weight: 800;">💰 EXPECTED PROFIT (EV)</div>
<div style="font-size: 1.10rem; font-weight: 900; color: {ev_color};">{ev_pct:+.1f}%</div>
<div style="font-size: 0.65rem; color: #64748B;">Est. long-term edge</div>
</div>

<div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; text-align: center;">
<div style="font-size: 0.70rem; color: #475569; font-weight: 800;">🎯 VALUE INDEX (A/E)</div>
<div style="font-size: 1.10rem; font-weight: 900; color: #0F172A;">{ae_ratio:.2f}</div>
<div style="font-size: 0.65rem; color: #64748B;">{'>1.0 = Underpriced' if ae_ratio >= 1.0 else '<1.0 = Overpriced'}</div>
</div>

<div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; text-align: center;">
<div style="font-size: 0.70rem; color: #475569; font-weight: 800;">⚡ SPEED POWER RATING</div>
<div style="font-size: 1.10rem; font-weight: 900; color: #4338CA;">{beyer_speed}</div>
<div style="font-size: 0.65rem; color: #64748B;">Recent pace score</div>
</div>

<div style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; text-align: center;">
<div style="font-size: 0.70rem; color: #475569; font-weight: 800;">💵 PROJ. NET GAIN / $25</div>
<div style="font-size: 1.10rem; font-weight: 900; color: {pl_color};">${one_unit_pl:+,.2f}</div>
<div style="font-size: 0.65rem; color: #64748B;">Per $25 flat bet</div>
</div>
</div>

<!-- Footer Details -->
<div style="font-size: 0.80rem; color: #475569; margin-bottom: 8px; line-height: 1.4;">
👤 <b>Jockey:</b> {jockey} &nbsp;|&nbsp; 👔 <b>Trainer:</b> {trainer}<br>
⚖️ <b>Recommended Bet Size:</b> <b style="color: #047857;">{kelly_stake:.1f}% of Bankroll</b>
</div>
</div>"""

        with col:
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"🔍 Open Full Quant Analysis ({ticker})", key=f"btn_inspect_{ticker}_{idx}", use_container_width=True):
                st.session_state["selected_horse_ticker"] = ticker
                st.rerun()
