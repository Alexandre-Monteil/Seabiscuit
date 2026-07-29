"""
SEABISCUIT - Pari-Mutuel Bet & Combination Simulator (Production Edition)
Gagnant/Placé, Couplé Duo, Trio, Quinté+ with Harville joint probabilities.
"""

from typing import Dict, Any, Optional
import streamlit as st
from backend.bet_simulator_engine import QuantBetSimulatorEngine
from backend.bet_generator_engine import SeabiscuitBetGenerator
from backend.utils import safe_float
from frontend.html_utils import compact_html


_BET_TYPE_LABELS = {
    "GAGNANT": "🥇 GAGNANT (WIN)",
    "PLACE": "🥈 PLACÉ (PLACE)",
    "DUO": "👯 COUPLÉ DUO (EXACTA)",
    "TRIO": "🥉 TRIO (TRIFECTA)",
    "QUINTE": "🏆 QUINTÉ+ (TOP 5)"
}


def _recommendation_banner(rec: Optional[Dict[str, Any]]) -> str:
    """Renders the SeabiscuitBetGenerator's pick (or no-bet call) as a callout banner."""
    if rec is None:
        return compact_html("""
        <div class="glass-card" style="border-top:4px solid #94A3B8;padding:16px 22px;margin-bottom:14px;animation:fadeIn 0.4s ease;">
            <span style="font-weight:900;color:#475569;">⚪ SEABISCUIT RECOMMENDS: NO BET</span>
            <span style="color:#64748B;font-size:0.85rem;"> — no runner in this race clears the positive-EV bar. Sitting it out is the disciplined play.</span>
        </div>
        """)

    label = _BET_TYPE_LABELS.get(rec["bet_type"], rec["bet_type"])
    runners = ", ".join(rec["runner_names"])
    return compact_html(f"""
    <div class="glass-card" style="border-top:4px solid #10B981;padding:16px 22px;margin-bottom:14px;animation:fadeIn 0.4s ease;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div>
                <span style="font-weight:900;color:#047857;">🎯 SEABISCUIT RECOMMENDS: {label}</span>
                <span style="color:#0F172A;font-weight:700;"> — {runners}</span>
            </div>
            <span style="background:#ECFDF5;color:#047857;border:1px solid #A7F3D0;font-weight:800;padding:3px 10px;border-radius:8px;font-size:0.78rem;">Confidence {rec['confidence_pct']:.0f}/100 · EV {rec['top_ev_pct']:+.1f}%</span>
        </div>
        <div style="color:#64748B;font-size:0.82rem;margin-top:4px;">{rec['rationale']}</div>
    </div>
    """)


def _bet_slip_card(label: str, accent: str, payout: float, profit: float,
                   ev_pct: float, extra_rows: list = None) -> str:
    """Generates a single bet slip card HTML. No HTML comments to avoid Streamlit rendering bugs."""
    ev_color = "#10B981" if ev_pct > 0 else "#F43F5E"
    profit_sign = "+" if profit > 0 else ""
    accent_bg = f"rgba({int(accent[1:3],16)},{int(accent[3:5],16)},{int(accent[5:7],16)},0.1)"

    extra_html = ""
    if extra_rows:
        grid_items = ""
        for row_label, row_value in extra_rows:
            grid_items += f"""
                <div style="background:#F1F5F9;border-radius:8px;padding:10px;text-align:center;">
                    <div style="font-size:0.72rem;color:#475569;font-weight:800;margin-bottom:3px;">{row_label}</div>
                    <div style="font-size:1.15rem;font-weight:900;color:#0F172A;font-family:'JetBrains Mono',monospace;">{row_value}</div>
                </div>"""
        extra_html = f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;">{grid_items}</div>'

    return compact_html(f"""
    <div class="glass-card" style="border-top:5px solid {accent};padding:20px;position:relative;animation:fadeIn 0.5s ease;">
        <div style="position:absolute;top:10px;right:10px;background:{accent_bg};color:{accent};padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:800;">{label}</div>
        <div style="font-size:0.72rem;color:#64748B;font-weight:800;text-transform:uppercase;letter-spacing:0.4px;">Projected Payout</div>
        <div style="font-size:2.4rem;font-weight:900;color:#0F172A;font-family:'JetBrains Mono',monospace;margin:4px 0;">${payout:,.2f}</div>
        <div style="font-size:0.92rem;color:{ev_color};font-weight:800;margin-bottom:12px;">{profit_sign}${profit:,.2f} Net Profit</div>
        <div style="background:#F1F5F9;border-radius:6px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.72rem;color:#475569;font-weight:700;">EV EDGE</span>
            <span style="font-size:0.95rem;font-weight:900;color:{ev_color};font-family:'JetBrains Mono',monospace;">{ev_pct:+.1f}%</span>
        </div>
        {extra_html}
    </div>""")


def _quinte_slip(payout: float, profit: float, ev_pct: float,
                 prob_pct: float) -> str:
    """Dark-theme Quinté+ jackpot card."""
    ev_color = "#10B981" if ev_pct > 0 else "#F43F5E"
    return compact_html(f"""
    <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);border-top:6px solid #EAB308;border-radius:14px;padding:28px;box-shadow:0 12px 30px rgba(0,0,0,0.2);margin-top:12px;text-align:center;animation:fadeIn 0.5s ease;">
        <div style="font-size:0.78rem;color:#94A3B8;font-weight:800;text-transform:uppercase;letter-spacing:0.6px;">Projected Quinté+ Jackpot</div>
        <div style="font-size:3.8rem;font-weight:900;color:#FDE047;font-family:'JetBrains Mono',monospace;margin:8px 0;text-shadow:0 0 24px rgba(234,179,8,0.35);">${payout:,.2f}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:400px;margin:20px auto 0;">
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:12px;">
                <div style="font-size:0.72rem;color:#94A3B8;font-weight:800;margin-bottom:3px;">COMBINATION PROB</div>
                <div style="font-size:1.15rem;font-weight:900;color:#F8FAFC;font-family:'JetBrains Mono',monospace;">{prob_pct:.4f}%</div>
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:12px;">
                <div style="font-size:0.72rem;color:#94A3B8;font-weight:800;margin-bottom:3px;">EXPECTED RETURN (EV)</div>
                <div style="font-size:1.15rem;font-weight:900;color:{ev_color};font-family:'JetBrains Mono',monospace;">{ev_pct:+.1f}%</div>
            </div>
        </div>
    </div>""")


def render_bet_simulator_view(racecard: Dict[str, Any]):
    """Renders the Bet Simulator with 4 tabs: Gagnant/Placé, Duo, Trio, Quinté+."""
    if not isinstance(racecard, dict):
        return

    runners = racecard.get("equity_assets") or racecard.get("runners") or []
    if not runners:
        st.info("No runners available for bet simulation.")
        return

    # Hero header
    st.markdown(compact_html("""
    <div class="glass-card" style="border-top:4px solid #0EA5E9;padding:18px 24px;margin-bottom:18px;animation:slideInLeft 0.4s ease;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
            <div>
                <h3 style="color:#0EA5E9;margin:0;font-weight:900;font-family:'Outfit',sans-serif;letter-spacing:0.3px;">
                    🎰 SEABISCUIT PARI-MUTUEL BET &amp; COMBINATION SIMULATOR
                </h3>
                <p style="color:var(--text-muted,#64748B);margin:4px 0 0;font-size:0.88rem;font-weight:600;">
                    Select bet type, runner combinations, and stake to compute Harville joint probabilities.
                </p>
            </div>
            <div class="live-pulse" style="background:var(--accent-emerald,#10B981);color:#FFF;font-weight:900;padding:6px 14px;border-radius:8px;font-size:0.82rem;">
                🟢 ENGINE READY
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    rec = SeabiscuitBetGenerator.generate_bet(racecard)
    st.markdown(_recommendation_banner(rec), unsafe_allow_html=True)

    runner_labels = [
        f"#{i+1} {r.get('horse','Runner')} (Odds: {safe_float(r.get('decimal_odds'),4.0):.2f})"
        for i, r in enumerate(runners)
    ]

    tab1, tab2, tab3, tab4 = st.tabs([
        "🥇 GAGNANT / PLACÉ",
        "👯 COUPLÉ DUO",
        "🥉 TRIO",
        "🏆 QUINTÉ+"
    ])

    # ── TAB 1: GAGNANT / PLACÉ ──
    with tab1:
        c1, c2 = st.columns([2.5, 1])
        with c1:
            sel_idx = st.selectbox("Select Target Runner:", range(len(runner_labels)),
                                   format_func=lambda i: runner_labels[i], key="sim_gagnant_runner")
        with c2:
            stake = st.slider("Stake ($):", 5.0, 500.0, 25.0, 5.0, key="sim_gagnant_stake")

        res = QuantBetSimulatorEngine.simulate_gagnant_place(runners[sel_idx], stake_usd=stake)
        w, p = res["win"], res["place"]

        col_w, col_p = st.columns(2)
        with col_w:
            st.markdown(_bet_slip_card("🥇 GAGNANT (WIN)", "#6366F1",
                                        w["payout_usd"], w["profit_usd"], w["ev_pct"]),
                        unsafe_allow_html=True)
        with col_p:
            st.markdown(_bet_slip_card("🥈 PLACÉ (PLACE)", "#0284C7",
                                        p["payout_usd"], p["profit_usd"], p["ev_pct"]),
                        unsafe_allow_html=True)

    # ── TAB 2: COUPLÉ DUO ──
    with tab2:
        if len(runners) < 2:
            st.info("Couplé Duo requires at least 2 runners.")
        else:
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            with c1:
                r1 = st.selectbox("1st Horse:", range(len(runner_labels)),
                                  format_func=lambda i: runner_labels[i], key="sim_duo_r1")
            with c2:
                r2_opts = [i for i in range(len(runner_labels)) if i != r1]
                r2 = st.selectbox("2nd Horse:", r2_opts,
                                  format_func=lambda i: runner_labels[i], key="sim_duo_r2")
            with c3:
                duo_stake = st.slider("Stake ($):", 5.0, 250.0, 25.0, 5.0, key="sim_duo_stake")

            d = QuantBetSimulatorEngine.simulate_duo_couple(runners[r1], runners[r2], runners, stake_usd=duo_stake)

            st.markdown(_bet_slip_card(
                "👯 COUPLÉ DUO (EXACTA)", "#D97706",
                d.get("payout_usd", 0), d.get("profit_usd", 0), d.get("ev_pct", 0),
                extra_rows=[
                    ("MONTE CARLO PROB (10K SIMS)", f"{d.get('joint_prob_pct',0):.2f}%"),
                    ("MODEL FAIR DIVIDEND", f"{d.get('estimated_odds',0):.2f}"),
                ]
            ), unsafe_allow_html=True)
            st.caption("💡 Compare the **Model Fair Dividend** above to the live PMU/bookmaker payout on the tote board — if the real payout is higher, you have an edge.")

    # ── TAB 3: TRIO ──
    with tab3:
        if len(runners) < 3:
            st.info("Trio requires at least 3 runners.")
        else:
            t1, t2, t3, t4 = st.columns(4)
            with t1:
                tr1 = st.selectbox("1st:", range(len(runner_labels)),
                                   format_func=lambda i: runner_labels[i], key="sim_trio_1")
            with t2:
                tr2 = st.selectbox("2nd:", [i for i in range(len(runner_labels)) if i != tr1],
                                   format_func=lambda i: runner_labels[i], key="sim_trio_2")
            with t3:
                tr3 = st.selectbox("3rd:", [i for i in range(len(runner_labels)) if i not in (tr1, tr2)],
                                   format_func=lambda i: runner_labels[i], key="sim_trio_3")
            with t4:
                trio_stake = st.number_input("Stake ($):", 2.0, 500.0, 10.0, 2.0, key="sim_trio_stake")

            trio_res = QuantBetSimulatorEngine.simulate_trio(
                [runners[tr1], runners[tr2], runners[tr3]], runners, stake_usd=trio_stake
            )

            st.markdown(_bet_slip_card(
                "🥉 TRIO (TRIFECTA)", "#8B5CF6",
                trio_res.get("payout_usd", 0), trio_res.get("profit_usd", 0), trio_res.get("ev_pct", 0),
                extra_rows=[
                    ("MONTE CARLO PROB (10K SIMS)", f"{trio_res.get('joint_prob_pct',0):.3f}%"),
                    ("MODEL FAIR DIVIDEND", f"{trio_res.get('estimated_odds',0):.2f}"),
                ]
            ), unsafe_allow_html=True)
            st.caption("💡 Compare the **Model Fair Dividend** above to the live PMU/bookmaker payout on the tote board — if the real payout is higher, you have an edge.")

    # ── TAB 4: QUINTÉ+ ──
    with tab4:
        if len(runners) >= 5:
            q_sel = st.multiselect("Select 5 Runners:", runner_labels,
                                   default=runner_labels[:5], key="sim_quinte_select")
            if len(q_sel) == 5:
                q_indices = [runner_labels.index(s) for s in q_sel]
                q_runners = [runners[i] for i in q_indices]
                q = QuantBetSimulatorEngine.simulate_quinte(q_runners, runners, stake_usd=10.0)
                st.markdown(_quinte_slip(
                    q.get("payout_usd", 0), q.get("profit_usd", 0),
                    q.get("ev_pct", 0), q.get("joint_prob_pct", 0)
                ), unsafe_allow_html=True)
            else:
                st.warning("Select exactly 5 runners for Quinté+ simulation.")
        else:
            st.info("Quinté+ requires at least 5 runners.")
