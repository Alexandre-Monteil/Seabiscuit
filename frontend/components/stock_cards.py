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
        beyer_speed = safe_int(asset.get("beyer_speed"), default=110)
        one_unit_pl = safe_float(asset.get("one_unit_pl"), default=0.0)
        kelly_stake = safe_float(asset.get("kelly_stake_pct"), default=0.0)

        # Premium CSS Gradient & Shadows
        if ev_pct > 4.0:
            card_border = "#10B981"
            card_bg = "linear-gradient(145deg, #FFFFFF 0%, #F0FDF4 100%)"
            badge_bg = "linear-gradient(90deg, #059669 0%, #10B981 100%)"
            badge_text = "🟢 🚀 TOP VALUE BET (+EV)"
            ev_color = "#047857"
        elif ev_pct < -5.0:
            card_border = "#F43F5E"
            card_bg = "linear-gradient(145deg, #FFFFFF 0%, #FFF1F2 100%)"
            badge_bg = "linear-gradient(90deg, #E11D48 0%, #F43F5E 100%)"
            badge_text = "🔴 ⚠️ OVERPRICED TRAP (-EV)"
            ev_color = "#BE123C"
        else:
            card_border = "#F59E0B"
            card_bg = "linear-gradient(145deg, #FFFFFF 0%, #FFFBEB 100%)"
            badge_bg = "linear-gradient(90deg, #D97706 0%, #F59E0B 100%)"
            badge_text = "🟡 ⚡ FAIR VALUE HEDGE"
            ev_color = "#B45309"

        pl_color = "#059669" if one_unit_pl > 0 else "#E11D48"
        beyer_pct = min(100, max(0, (beyer_speed - 50) / 80 * 100))  # Normalize beyer 50-130 to 0-100%
        kelly_pct_capped = min(100, max(0, kelly_stake * 5))  # Cap for progress bar visualization
        anim_delay = f"{idx * 0.08:.2f}s"

        card_html = f"""
<div class="glass-card" style="background: {card_bg}; border: 1.5px solid {card_border}; border-top: 5px solid {card_border}; border-radius: 12px; padding: 18px; margin-bottom: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.06); animation: fadeIn 0.5s ease {anim_delay} both;">
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 900; color: #1E1B4B; letter-spacing: -0.5px;">#{idx+1} {ticker}</span>
        <span style="background: {badge_bg}; color: #FFFFFF; font-weight: 900; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">{badge_text}</span>
    </div>
    
    <div style="font-size: 1.35rem; font-weight: 900; color: #0F172A; line-height: 1.1; margin-bottom: 4px; letter-spacing: -0.5px;">{horse_name}</div>
    <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 14px; font-weight: 600;">{sire} × {dam}</div>

    <!-- Price & Odds Header Banner -->
    <div style="background: rgba(255,255,255,0.7); border: 1px solid rgba(226,232,240,0.8); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(4px);">
        <div>
            <div style="font-size: 0.70rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Implied Price / $100</div>
            <div style="font-size: 1.45rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono', monospace;">${share_price:.2f}</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.70rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Market Odds</div>
            <div style="font-size: 1.45rem; font-weight: 900; color: #0284C7; font-family: 'JetBrains Mono', monospace;">{decimal_odds:.2f}</div>
        </div>
    </div>

    <!-- 4 Actionable Metrics Grid -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px;">
        <!-- EV Panel -->
        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="font-size: 0.70rem; color: #475569; font-weight: 800; margin-bottom: 4px;">💰 EXPECTED PROFIT (EV)</div>
            <div style="font-size: 1.25rem; font-weight: 900; color: {ev_color}; font-family: 'JetBrains Mono', monospace;">{ev_pct:+.1f}%</div>
        </div>

        <!-- PL Panel -->
        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="font-size: 0.70rem; color: #475569; font-weight: 800; margin-bottom: 4px;">💵 PROJ. NET GAIN / $25</div>
            <div style="font-size: 1.25rem; font-weight: 900; color: {pl_color}; font-family: 'JetBrains Mono', monospace;">${one_unit_pl:+,.2f}</div>
        </div>
        
        <!-- Speed Power Panel w/ Progress Bar -->
        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                <span style="font-size: 0.70rem; color: #475569; font-weight: 800;">⚡ SPEED RTG</span>
                <span style="font-size: 1.05rem; font-weight: 900; color: #4338CA; font-family: 'JetBrains Mono', monospace;">{beyer_speed}</span>
            </div>
            <div style="width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 3px; overflow: hidden;">
                <div style="width: {beyer_pct}%; height: 100%; background: linear-gradient(90deg, #818CF8 0%, #4338CA 100%); transition: width 0.6s ease;"></div>
            </div>
        </div>

        <!-- Kelly Stake Panel w/ Progress Bar -->
        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                <span style="font-size: 0.70rem; color: #475569; font-weight: 800;">⚖️ REC. STAKE</span>
                <span style="font-size: 1.05rem; font-weight: 900; color: #047857; font-family: 'JetBrains Mono', monospace;">{kelly_stake:.1f}%</span>
            </div>
            <div style="width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 3px; overflow: hidden;">
                <div style="width: {kelly_pct_capped}%; height: 100%; background: linear-gradient(90deg, #34D399 0%, #047857 100%); transition: width 0.6s ease;"></div>
            </div>
        </div>
    </div>

    <!-- Footer Details -->
    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748B; font-weight: 600; padding-top: 8px; border-top: 1px dashed #CBD5E1;">
        <div>👤 J: <span style="color:#0F172A;">{jockey}</span></div>
        <div>👔 T: <span style="color:#0F172A;">{trainer}</span></div>
    </div>
</div>
"""

        with col:
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"🔍 Open Full Quant Analysis ({ticker})", key=f"btn_inspect_{ticker}_{idx}", use_container_width=True):
                st.session_state["selected_horse_ticker"] = ticker
                st.rerun()
