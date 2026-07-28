"""
SEABISCUIT - Interactive Quantitative Bet & Combination Simulator UI Component (Hero Feature Edition)
Renders high-impact interactive Pari-Mutuel & Quantitative Bet Simulators for Gagnant, Placé, Couplé Duo, Trio, and Quinté+.
"""

from typing import List, Dict, Any
import streamlit as st

try:
    from backend.bet_simulator_engine import QuantBetSimulatorEngine
    from backend.utils import safe_float, safe_int
except (ImportError, ValueError):
    from backend.bet_simulator_engine import QuantBetSimulatorEngine
    from backend.utils import safe_float, safe_int


def render_bet_simulator_view(racecard: Dict[str, Any]):
    """Renders the Prominent Hero Bet Simulator & Combination Engine."""
    if not isinstance(racecard, dict):
        st.info("No active racecard available for bet simulation.")
        return

    runners = racecard.get("equity_assets", [])
    if not runners:
        runners = racecard.get("runners", [])

    if not runners:
        st.info("No runners available for bet simulation.")
        return

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border-radius: 14px; padding: 20px 26px; color: #FFFFFF; box-shadow: 0 8px 24px rgba(49, 46, 129, 0.25); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="color: #F59E0B; margin: 0; font-weight: 900; letter-spacing: 0.5px;">🎰 SEABISCUIT PARI-MUTUEL BET & COMBINATION SIMULATOR</h3>
                <p style="color: #CBD5E1; margin: 4px 0 0 0; font-size: 0.95rem;">Select your bet type, runner combinations, and stake to compute Harville joint probabilities and expected payouts.</p>
            </div>
            <div style="background: #10B981; color: #FFFFFF; font-weight: 900; padding: 6px 14px; border-radius: 8px; font-size: 0.9rem;">
                🟢 QUANT ENGINE READY
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sim_tab1, sim_tab2, sim_tab3, sim_tab4 = st.tabs([
        "🥇 GAGNANT / PLACÉ (SINGLE)",
        "👯 COUPLE DUO (TOP 2)",
        "🥉 TRIO (TOP 3)",
        "🏆 QUINTÉ+ (TOP 5 JACKPOT)"
    ])

    # ---------------------------------------------------------
    # TAB 1: GAGNANT / PLACÉ
    # ---------------------------------------------------------
    with sim_tab1:
        c1, c2 = st.columns([2, 1])
        runner_names = [f"#{idx+1} {r.get('horse', 'Runner')} (Odds: {safe_float(r.get('decimal_odds'), 4.0):.2f})" for idx, r in enumerate(runners)]
        
        with c1:
            sel_runner_idx = st.selectbox("Select Target Runner:", range(len(runner_names)), format_func=lambda i: runner_names[i], key="sim_gagnant_runner")
            target_runner = runners[sel_runner_idx]
        with c2:
            stake_usd = st.slider("Select Stake ($):", min_value=5.0, max_value=500.0, value=25.0, step=5.0, key="sim_gagnant_stake")

        res = QuantBetSimulatorEngine.simulate_gagnant_place(target_runner, stake_usd=stake_usd)
        w_data = res["win"]
        p_data = res["place"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Win Payout", f"${w_data['payout_usd']:,.2f}", delta=f"${w_data['net_profit_usd']:+,.2f} Net Profit")
        m2.metric("📈 Win EV Edge", f"{w_data['ev_pct']:+.1f}%", delta="🟢 +EV" if w_data['ev_pct'] > 0 else "🔴 -EV")
        m3.metric("🥈 Place Payout", f"${p_data['payout_usd']:,.2f}", delta=f"${p_data['net_profit_usd']:+,.2f} Net Profit")
        m4.metric("⚖️ Kelly Stake Size", f"{target_runner.get('kelly_stake_pct', 2.5):.1f}% of Bankroll")

    # ---------------------------------------------------------
    # TAB 2: COUPLE DUO
    # ---------------------------------------------------------
    with sim_tab2:
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1:
            r1_idx = st.selectbox("1st Horse Choice:", range(len(runner_names)), format_func=lambda i: runner_names[i], key="sim_duo_r1")
        with c2:
            r2_options = [i for i in range(len(runner_names)) if i != r1_idx]
            r2_idx = st.selectbox("2nd Horse Choice:", r2_options, format_func=lambda i: runner_names[i], key="sim_duo_r2")
        with c3:
            duo_stake = st.slider("Stake ($):", min_value=5.0, max_value=250.0, value=25.0, step=5.0, key="sim_duo_stake")

        res_duo = QuantBetSimulatorEngine.simulate_couple_duo(runners[r1_idx], runners[r2_idx], stake_usd=duo_stake)
        d_g = res_duo["couple_gagnant"]

        k1, k2, k3 = st.columns(3)
        k1.metric("👯 Duo Payout", f"${d_g['payout_usd']:,.2f}", delta=f"${d_g['net_profit_usd']:+,.2f} Net Profit")
        k2.metric("📊 Harville Joint Prob", f"{d_g['joint_prob_pct']:.2f}%")
        k3.metric("📈 Expected Return (EV)", f"{d_g['ev_pct']:+.1f}%")

    # ---------------------------------------------------------
    # TAB 3: TRIO
    # ---------------------------------------------------------
    with sim_tab3:
        st.markdown("<p style='color: #475569; font-weight: 700;'>Select 3 runners for Trifecta combination payout simulation.</p>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.columns([1, 1, 1, 1])
        with t1:
            tr1 = st.selectbox("1st:", range(len(runner_names)), format_func=lambda i: runner_names[i], key="sim_trio_1")
        with t2:
            tr2_opts = [i for i in range(len(runner_names)) if i != tr1]
            tr2 = st.selectbox("2nd:", tr2_opts, format_func=lambda i: runner_names[i], key="sim_trio_2")
        with t3:
            tr3_opts = [i for i in range(len(runner_names)) if i not in [tr1, tr2]]
            tr3 = st.selectbox("3rd:", tr3_opts, format_func=lambda i: runner_names[i], key="sim_trio_3")
        with t4:
            trio_stake = st.number_input("Stake ($):", min_value=2.0, max_value=500.0, value=10.0, step=2.0, key="sim_trio_stake")

        res_trio = QuantBetSimulatorEngine.simulate_trio(runners[tr1], runners[tr2], runners[tr3], stake_usd=trio_stake)
        p1, p2, p3 = st.columns(3)
        p1.metric("🥉 Trio Payout", f"${res_trio['payout_usd']:,.2f}", delta=f"${res_trio['net_profit_usd']:+,.2f} Net Profit")
        p2.metric("📊 Harville Trio Prob", f"{res_trio['joint_prob_pct']:.3f}%")
        p3.metric("📈 Trio EV Edge", f"{res_trio['ev_pct']:+.1f}%")

    # ---------------------------------------------------------
    # TAB 4: QUINTÉ+ TOP 5
    # ---------------------------------------------------------
    with sim_tab4:
        st.markdown("<p style='color: #475569; font-weight: 700;'>Select top 5 runners for Quinté+ Jackpot simulation.</p>", unsafe_allow_html=True)
        if len(runners) >= 5:
            q_selected = st.multiselect("Select 5 Runners for Quinté+ Combination:", runner_names, default=runner_names[:5], key="sim_quinte_select")
            if len(q_selected) == 5:
                indices = [runner_names.index(s) for s in q_selected]
                q_runners = [runners[i] for i in indices]
                q_res = QuantBetSimulatorEngine.simulate_quinte_plus(q_runners, stake_usd=10.0)
                
                q1, q2, q3 = st.columns(3)
                q1.metric("🏆 Quinté+ Dividend", f"${q_res['projected_jackpot_usd']:,.2f}")
                q2.metric("📊 Combination Prob", f"{q_res['joint_prob_pct']:.4f}%")
                q3.metric("📈 Quinté+ EV %", f"{q_res['ev_pct']:+.1f}%")
            else:
                st.warning("Please select exactly 5 runners for Quinté+ simulation.")
        else:
            st.info("Quinté+ simulation requires at least 5 runners in the racecard.")
