"""
SEABISCUIT - Interactive Quantitative Bet Simulator UI Component
Simulates Gagnant, Placé, Duo (Couplé), Trio, and Quinté+ pari-mutuel combinations live.
"""

from typing import Dict, List, Any
import streamlit as st

try:
    from backend.bet_simulator_engine import QuantBetSimulatorEngine
    from backend.utils import safe_float
except (ImportError, ValueError):
    from backend.bet_simulator_engine import QuantBetSimulatorEngine
    from backend.utils import safe_float


def render_bet_simulator_view(current_racecard: Dict[str, Any]):
    """Renders the interactive Quantitative Bet Simulator dashboard."""
    if not isinstance(current_racecard, dict):
        st.info("Select a valid racecard to launch the Bet Simulator.")
        return

    equity_assets = current_racecard.get("equity_assets", [])
    if not equity_assets:
        st.info("No active runners available in this racecard.")
        return

    st.markdown("""
    <div style="background: #FFFFFF; border: 2px solid #4338CA; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(67, 56, 202, 0.12);">
        <h3 style="color: #4338CA; margin-top: 0; font-weight: 900;">🎰 QUANTITATIVE BET SIMULATOR & COMBINATION ENGINE</h3>
        <p style="color: #475569; font-size: 0.95rem; margin-bottom: 0;">Simulate Gagnant/Placé, Couplé Duo, Trio, and Quinté+ combinations using Wall Street Harville probability models.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_gagnant, tab_duo, tab_trio, tab_quinte = st.tabs([
        "🥇 Gagnant / Placé",
        "👯 Duo (Couplé)",
        "🥉 Trio (Trifecta)",
        "🏆 Quinté+ (Top 5)"
    ])

    runner_names = [f"{a.get('ticker', '$RUNNER')} ({a.get('horse', 'Runner')}) — Odds: {safe_float(a.get('decimal_odds'), 4.0):.2f}" for a in equity_assets if isinstance(a, dict)]
    runner_map = {runner_names[i]: equity_assets[i] for i in range(min(len(runner_names), len(equity_assets)))}

    # ---------------------------------------------------------
    # TAB 1: GAGNANT / PLACÉ (SINGLE RUNNER)
    # ---------------------------------------------------------
    with tab_gagnant:
        col_sel, col_stake = st.columns([3, 1])
        with col_sel:
            selected_runner_lbl = st.selectbox("Select Target Runner:", runner_names, key="sim_gagnant_runner")
        with col_stake:
            stake_usd = st.number_input("Stake ($):", min_value=1.0, max_value=1000.0, value=25.0, step=5.0, key="sim_gagnant_stake")

        target_asset = runner_map.get(selected_runner_lbl)
        if target_asset:
            res = QuantBetSimulatorEngine.simulate_gagnant_place(target_asset, stake_usd)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🥇 Gagnant Payout", f"${res['win']['payout_usd']:,.2f}", delta=f"+${res['win']['profit_usd']:,.2f} Profit")
            c2.metric("🥇 Gagnant EV %", f"{res['win']['ev_pct']:+.1f}%", delta="🟢 +EV Gold" if res['win']['ev_pct'] > 0 else "🔴 -EV Fade")
            c3.metric("🥈 Placé Payout", f"${res['place']['payout_usd']:,.2f}", delta=f"+${res['place']['profit_usd']:,.2f} Profit")
            c4.metric("⚡ Half-Kelly Rec.", f"${res['win']['half_kelly_usd']:,.2f}")

    # ---------------------------------------------------------
    # TAB 2: DUO (COUPLÉ GAGNANT / PLACÉ)
    # ---------------------------------------------------------
    with tab_duo:
        d_col1, d_col2, d_col3 = st.columns([2, 2, 1])
        with d_col1:
            duo_a_lbl = st.selectbox("1st Runner (A):", runner_names, key="sim_duo_a")
        with d_col2:
            duo_b_lbl = st.selectbox("2nd Runner (B):", [r for r in runner_names if r != duo_a_lbl], key="sim_duo_b")
        with d_col3:
            duo_stake = st.number_input("Stake ($):", min_value=1.0, max_value=500.0, value=10.0, step=5.0, key="sim_duo_stake")

        exact_order = st.checkbox("🎯 Couplé Ordre (Exact 1st & 2nd)", value=False, key="sim_duo_exact")

        asset_a, asset_b = runner_map.get(duo_a_lbl), runner_map.get(duo_b_lbl)
        if asset_a and asset_b:
            res_duo = QuantBetSimulatorEngine.simulate_duo_couple(asset_a, asset_b, duo_stake, exact_order)
            
            dc1, dc2, dc3, dc4 = st.columns(4)
            dc1.metric("👯 Joint Win Prob", f"{res_duo.get('joint_prob_pct', 0.0):.1f}%")
            dc2.metric("📊 Est. Dividend Odds", f"{res_duo.get('estimated_odds', 0.0):.2f}")
            dc3.metric("💵 Projected Payout", f"${res_duo.get('payout_usd', 0.0):,.2f}", delta=f"+${res_duo.get('profit_usd', 0.0):,.2f}")
            dc4.metric("🚀 Couplé EV %", f"{res_duo.get('ev_pct', 0.0):+.1f}%", delta="🟢 +EV Combination" if res_duo.get('ev_pct', 0) > 0 else "🔴 -EV")

    # ---------------------------------------------------------
    # TAB 3: TRIO (TRIFECTA TOP 3)
    # ---------------------------------------------------------
    with tab_trio:
        st.markdown("##### 🥉 Select 3 Runners for Trio Combination:")
        selected_trio_lbls = st.multiselect("Choose 3 Runners:", runner_names, default=runner_names[:min(3, len(runner_names))], key="sim_trio_select")
        trio_stake = st.number_input("Stake ($):", min_value=1.0, max_value=500.0, value=10.0, step=5.0, key="sim_trio_stake")
        trio_exact = st.checkbox("🎯 Trio Ordre (Exact 1st, 2nd, 3rd)", value=False, key="sim_trio_exact")

        if len(selected_trio_lbls) >= 3:
            trio_assets = [runner_map[lbl] for lbl in selected_trio_lbls[:3] if lbl in runner_map]
            res_trio = QuantBetSimulatorEngine.simulate_trio(trio_assets, trio_stake, trio_exact)
            
            tc1, tc2, tc3, tc4 = st.columns(4)
            tc1.metric("🥉 Joint Trio Prob", f"{res_trio.get('joint_prob_pct', 0.0):.2f}%")
            tc2.metric("📊 Est. Trio Dividend", f"{res_trio.get('estimated_odds', 0.0):.2f}")
            tc3.metric("💵 Projected Payout", f"${res_trio.get('payout_usd', 0.0):,.2f}", delta=f"+${res_trio.get('profit_usd', 0.0):,.2f}")
            tc4.metric("🚀 Trio EV %", f"{res_trio.get('ev_pct', 0.0):+.1f}%", delta="🟢 +EV Trio" if res_trio.get('ev_pct', 0) > 0 else "🔴 -EV")
        else:
            st.warning("Please select at least 3 runners to simulate Trio.")

    # ---------------------------------------------------------
    # TAB 4: QUINTÉ+ (TOP 5 JACKPOT)
    # ---------------------------------------------------------
    with tab_quinte:
        st.markdown("##### 🏆 Select 5 Runners for Quinté+ Combination:")
        selected_quinte_lbls = st.multiselect("Choose 5 Runners for Quinté+:", runner_names, default=runner_names[:min(5, len(runner_names))], key="sim_quinte_select")
        quinte_stake = st.number_input("Ticket Base ($):", min_value=1.0, max_value=100.0, value=2.0, step=1.0, key="sim_quinte_stake")

        if len(selected_quinte_lbls) >= 5:
            quinte_assets = [runner_map[lbl] for lbl in selected_quinte_lbls[:5] if lbl in runner_map]
            res_q = QuantBetSimulatorEngine.simulate_quinte(quinte_assets, quinte_stake)
            
            qc1, qc2, qc3, qc4 = st.columns(4)
            qc1.metric("🏆 Quinté+ Probability", f"{res_q.get('joint_prob_pct', 0.0):.4f}%")
            qc2.metric("💰 Est. Jackpot Dividend", f"${res_q.get('estimated_dividend_odds', 0.0):,.2f}")
            qc3.metric("💵 Potential Payout", f"${res_q.get('payout_usd', 0.0):,.2f}", delta=f"+${res_q.get('profit_usd', 0.0):,.2f}")
            qc4.metric("🚀 Quinté+ EV %", f"{res_q.get('ev_pct', 0.0):+.1f}%", delta="🟢 High Alpha" if res_q.get('ev_pct', 0) > 0 else "🔴 Low Odds")
        else:
            st.warning("Please select at least 5 runners to simulate Quinté+.")
