"""
SEABISCUIT - Active Horse Asset Cards Grid Component (Ultra-Clarity High-Contrast Design)
Renders high-contrast stock cards with crisp metric hierarchies and zero text overlap.
"""

from typing import List, Dict, Any
import streamlit as st

try:
    from backend.utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int


def render_stock_asset_cards(equity_assets: List[Dict[str, Any]]):
    """Renders high-contrast equity asset cards grid with maximum readability."""
    if not equity_assets:
        st.info("No active runner equities available for this race.")
        return

    st.markdown("<h4 style='color: #0F172A; font-weight: 900; margin-bottom: 12px;'>🏇 RUNNER EQUITIES & QUANTITATIVE ALPHAS</h4>", unsafe_allow_html=True)

    # 3 Cards per row grid layout for maximum space and legibility
    cols = st.columns(3)

    for idx, asset in enumerate(equity_assets):
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

        card_class = "gaming-card-green" if ev_pct > 5.0 else ("gaming-card-red" if ev_pct < -8.0 else "gaming-card-gold")
        badge_class = "badge-pepite" if ev_pct > 5.0 else ("badge-piege" if ev_pct < -8.0 else "badge-outsider")
        badge_text = "🟢 +EV GOLDEN NUGGET" if ev_pct > 5.0 else ("🔴 OVERPRICED FADE" if ev_pct < -8.0 else "🟡 VALUE HEDGE")

        with col:
            st.markdown(f"""
            <div class="{card_class}" style="padding: 16px; margin-bottom: 16px;">
                <!-- Header: Ticker & Status Badge -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 800; color: #4338CA;">{ticker}</span>
                    <span class="{badge_class}">{badge_text}</span>
                </div>
                
                <!-- Horse Name & Pedigree -->
                <div style="font-size: 1.25rem; font-weight: 900; color: #0F172A; line-height: 1.2;">{horse_name}</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">({sire} x {dam})</div>

                <!-- Main Equity Price & Odds Banner -->
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Share Price</div>
                        <div style="font-size: 1.4rem; font-weight: 900; color: #0F172A;">${share_price:.2f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Decimal Odds</div>
                        <div style="font-size: 1.4rem; font-weight: 900; color: #0284C7;">{decimal_odds:.2f}</div>
                    </div>
                </div>

                <!-- 4 Key Quant Metrics Grid -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                    <div class="quant-pill" style="padding: 6px;">
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 800;">EXPECTED VALUE</div>
                        <div style="font-size: 1.05rem; font-weight: 900; color: {'#059669' if ev_pct > 0 else '#E11D48'};">{ev_pct:+.1f}%</div>
                    </div>
                    <div class="quant-pill" style="padding: 6px;">
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 800;">A/E ALPHA EDGE</div>
                        <div style="font-size: 1.05rem; font-weight: 900; color: #0F172A;">{ae_ratio:.2f}</div>
                    </div>
                    <div class="quant-pill" style="padding: 6px;">
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 800;">BEYER SPEED</div>
                        <div style="font-size: 1.05rem; font-weight: 900; color: #4338CA;">{beyer_speed}</div>
                    </div>
                    <div class="quant-pill" style="padding: 6px;">
                        <div style="font-size: 0.72rem; color: #64748B; font-weight: 800;">1-UNIT P/L</div>
                        <div style="font-size: 1.05rem; font-weight: 900; color: {'#059669' if one_unit_pl > 0 else '#E11D48'};">${one_unit_pl:+,.2f}</div>
                    </div>
                </div>

                <!-- Jockey & Trainer Line -->
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 10px; line-height: 1.4;">
                    👤 <b>Jockey:</b> {jockey} &nbsp;|&nbsp; 👔 <b>Trainer:</b> {trainer}<br>
                    ⚡ <b>Half-Kelly Stake:</b> {kelly_stake:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🔍 Inspect {ticker} Dossier", key=f"btn_inspect_{ticker}_{idx}", use_container_width=True):
                st.session_state["selected_horse_ticker"] = ticker
                st.rerun()
