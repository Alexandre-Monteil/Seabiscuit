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

        w_ev_color = "#10B981" if w_data['ev_pct'] > 0 else "#F43F5E"
        p_ev_color = "#10B981" if p_data['ev_pct'] > 0 else "#F43F5E"
        
        slip_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px;">
            <!-- WIN BET SLIP -->
            <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 2px dashed #CBD5E1; border-top: 6px solid #4338CA; border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); position: relative;">
                <div style="position: absolute; top: 10px; right: 10px; background: rgba(67,56,202,0.1); color: #4338CA; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 800;">🥇 GAGNANT (WIN)</div>
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 800; text-transform: uppercase;">Projected Win Payout</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">${w_data['payout_usd']:,.2f}</div>
                <div style="font-size: 0.9rem; color: {w_ev_color}; font-weight: 800; margin-bottom: 12px;">{'+' if w_data['profit_usd'] > 0 else ''}${w_data['profit_usd']:,.2f} Net Profit</div>
                <div style="background: #F1F5F9; border-radius: 6px; padding: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.75rem; color: #475569; font-weight: 700;">EV EDGE</span>
                    <span style="font-size: 0.95rem; font-weight: 900; color: {w_ev_color}; font-family: 'JetBrains Mono';">{w_data['ev_pct']:+.1f}%</span>
                </div>
            </div>

            <!-- PLACE BET SLIP -->
            <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 2px dashed #CBD5E1; border-top: 6px solid #0284C7; border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); position: relative;">
                <div style="position: absolute; top: 10px; right: 10px; background: rgba(2,132,199,0.1); color: #0284C7; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 800;">🥈 PLACÉ (PLACE)</div>
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 800; text-transform: uppercase;">Projected Place Payout</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 4px 0;">${p_data['payout_usd']:,.2f}</div>
                <div style="font-size: 0.9rem; color: {p_ev_color}; font-weight: 800; margin-bottom: 12px;">{'+' if p_data['profit_usd'] > 0 else ''}${p_data['profit_usd']:,.2f} Net Profit</div>
                <div style="background: #F1F5F9; border-radius: 6px; padding: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.75rem; color: #475569; font-weight: 700;">EV EDGE</span>
                    <span style="font-size: 0.95rem; font-weight: 900; color: {p_ev_color}; font-family: 'JetBrains Mono';">{p_data['ev_pct']:+.1f}%</span>
                </div>
            </div>
        </div>
        """
        st.markdown(slip_html, unsafe_allow_html=True)

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

        res_duo = QuantBetSimulatorEngine.simulate_duo_couple(runners[r1_idx], runners[r2_idx], stake_usd=duo_stake)
        d_g = res_duo
        ev_color = "#10B981" if d_g.get('ev_pct', 0) > 0 else "#F43F5E"

        slip_html = f"""
        <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 2px dashed #CBD5E1; border-top: 6px solid #D97706; border-radius: 12px; padding: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); margin-top: 10px; position: relative; text-align: center;">
            <div style="position: absolute; top: 12px; right: 12px; background: rgba(217,119,6,0.1); color: #D97706; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 900;">👯 COUPLÉ DUO (EXACTA)</div>
            <div style="font-size: 0.85rem; color: #64748B; font-weight: 800; text-transform: uppercase;">Projected Duo Payout</div>
            <div style="font-size: 3.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 8px 0;">${d_g.get('payout_usd', 0):,.2f}</div>
            <div style="font-size: 1.1rem; color: {ev_color}; font-weight: 900; margin-bottom: 20px;">{'+' if d_g.get('profit_usd', 0) > 0 else ''}${d_g.get('profit_usd', 0):,.2f} Net Profit</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 400px; margin: 0 auto;">
                <div style="background: #F1F5F9; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 800; margin-bottom: 4px;">HARVILLE JOINT PROB</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono';">{d_g.get('joint_prob_pct', 0):.2f}%</div>
                </div>
                <div style="background: #F1F5F9; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 800; margin-bottom: 4px;">EXPECTED RETURN (EV)</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: {ev_color}; font-family: 'JetBrains Mono';">{d_g.get('ev_pct', 0):+.1f}%</div>
                </div>
            </div>
        </div>
        """
        st.markdown(slip_html, unsafe_allow_html=True)

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
        ev_color = "#10B981" if res_trio.get('ev_pct', 0) > 0 else "#F43F5E"

        slip_html = f"""
        <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 2px dashed #CBD5E1; border-top: 6px solid #8B5CF6; border-radius: 12px; padding: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); margin-top: 10px; position: relative; text-align: center;">
            <div style="position: absolute; top: 12px; right: 12px; background: rgba(139,92,246,0.1); color: #8B5CF6; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 900;">🥉 TRIO (TRIFECTA)</div>
            <div style="font-size: 0.85rem; color: #64748B; font-weight: 800; text-transform: uppercase;">Projected Trio Payout</div>
            <div style="font-size: 3.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono', monospace; margin: 8px 0;">${res_trio.get('payout_usd', 0):,.2f}</div>
            <div style="font-size: 1.1rem; color: {ev_color}; font-weight: 900; margin-bottom: 20px;">{'+' if res_trio.get('profit_usd', 0) > 0 else ''}${res_trio.get('profit_usd', 0):,.2f} Net Profit</div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 400px; margin: 0 auto;">
                <div style="background: #F1F5F9; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 800; margin-bottom: 4px;">HARVILLE TRIO PROB</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: #0F172A; font-family: 'JetBrains Mono';">{res_trio.get('joint_prob_pct', 0):.3f}%</div>
                </div>
                <div style="background: #F1F5F9; border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 800; margin-bottom: 4px;">EXPECTED RETURN (EV)</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: {ev_color}; font-family: 'JetBrains Mono';">{res_trio.get('ev_pct', 0):+.1f}%</div>
                </div>
            </div>
        </div>
        """
        st.markdown(slip_html, unsafe_allow_html=True)

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
                q_res = QuantBetSimulatorEngine.simulate_quinte(q_runners, stake_usd=10.0)
                ev_color = "#10B981" if q_res.get('ev_pct', 0) > 0 else "#F43F5E"
                
                slip_html = f"""
                <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 2px dashed #475569; border-top: 6px solid #EAB308; border-radius: 12px; padding: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.2); margin-top: 10px; position: relative; text-align: center;">
                    <div style="position: absolute; top: 12px; right: 12px; background: rgba(234,179,8,0.2); color: #FDE047; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 900;">🏆 QUINTÉ+ (JACKPOT)</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 800; text-transform: uppercase;">Projected Jackpot Dividend</div>
                    <div style="font-size: 4rem; font-weight: 900; color: #FDE047; font-family: 'JetBrains Mono', monospace; margin: 8px 0; text-shadow: 0 0 20px rgba(234,179,8,0.4);">${q_res.get('payout_usd', 0):,.2f}</div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 400px; margin: 20px auto 0 auto;">
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px;">
                            <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 800; margin-bottom: 4px;">COMBINATION PROB</div>
                            <div style="font-size: 1.2rem; font-weight: 900; color: #F8FAFC; font-family: 'JetBrains Mono';">{q_res.get('joint_prob_pct', 0):.4f}%</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px;">
                            <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 800; margin-bottom: 4px;">EXPECTED RETURN (EV)</div>
                            <div style="font-size: 1.2rem; font-weight: 900; color: {ev_color}; font-family: 'JetBrains Mono';">{q_res.get('ev_pct', 0):+.1f}%</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(slip_html, unsafe_allow_html=True)
            else:
                st.warning("Please select exactly 5 runners for Quinté+ simulation.")
        else:
            st.info("Quinté+ simulation requires at least 5 runners in the racecard.")
