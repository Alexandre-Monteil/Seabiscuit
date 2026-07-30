"""
SEABISCUIT - Interactive Bet Generator Backtest UI Component
Renders cumulative bankroll growth, win rate %, ROI %, Sharpe Ratio, Max Drawdown, bet-type
breakdown, and trade history for the SEABISCUIT Bet Generator strategy.
"""

from typing import List, Dict, Any
import streamlit as st

from backend.backtest_engine import EquineBacktestEngine
from backend.visualization_3d import EquineVisualization3D
from frontend.html_utils import compact_html


def render_backtest_view(all_racecards: List[Dict[str, Any]]):
    """Renders the Seabiscuit Bet Generator Backtest & P/L Tracker Dashboard."""
    if not all_racecards:
        st.info("No racecard data available for backtesting.")
        return

    st.markdown(compact_html("""
    <div class="glass-card" style="border-top: 4px solid var(--accent-emerald, #10B981); padding: 18px 24px; margin-bottom: 20px; animation: fadeIn 0.5s ease;">
        <h3 style="color: #047857; margin-top: 0; font-weight: 900; font-family: 'Outfit', sans-serif;">📈 SEABISCUIT BET GENERATOR BACKTEST & P/L TRACKER</h3>
        <p style="color: var(--text-muted, #475569); font-size: 0.92rem; margin-bottom: 0; font-weight: 600;">Simulates the SEABISCUIT Bet Generator's actual picks — a flat-stake Gagnant bet on the top sanely-priced runner (≤20-1) when it clears the EV bar, or no bet at all — not just backing whichever runner has the highest nominal EV%.</p>
    </div>
    """), unsafe_allow_html=True)

    st.warning(
        "⚠️ **The numbers below are from data the model was also trained on** (recent races, "
        "same rolling window used to fit the A/E model) — they will look better than reality. "
        "When we split the data properly (trained on 8 months, tested on the following 4 months "
        "the model never saw), it found **zero qualifying bets across ~3,700 real races** — no "
        "validated edge survived. Treat this backtest as an illustration of how the generator "
        "behaves, not evidence it's profitable."
    )

    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    b_col1, b_col2 = st.columns([1, 3])
    with b_col1:
        initial_capital = st.number_input("Initial Capital ($):", min_value=100.0, max_value=10000.0, value=1000.0, step=100.0, key="bt_capital")
        unit_stake = st.number_input("Fixed Stake per Bet ($):", min_value=1.0, max_value=500.0, value=10.0, step=1.0, key="bt_stake",
                                      help="Same flat stake for the strategy and the favorite-backing baseline, for simplicity. Betting stops once the bankroll can't cover the stake — it can shrink but never go negative.")

    res = EquineBacktestEngine.run_ev_strategy_backtest(all_racecards, initial_bankroll_usd=initial_capital, unit_bet_usd=unit_stake)

    if res["total_bets"] == 0:
        st.info("No sanely-priced (≤20-1) positive-EV opportunities found across the available races — the generator recommended no bets on any of them.")
        return

    # Key Backtest KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Final Bankroll", f"${res['final_bankroll_usd']:,.2f}", delta=f"${res['total_profit_usd']:+,.2f}")
    k2.metric("Cumulative ROI", f"{res['roi_pct']:+.1f}%")
    k3.metric("Win Rate %", f"{res['win_rate_pct']:.1f}%", delta=f"{res['winning_bets']}/{res['total_bets']} Wins")
    k4.metric("Sharpe Ratio", f"{res['sharpe_ratio']:.2f}")
    k5.metric("Max Drawdown", f"-{res['max_drawdown_pct']:.1f}%")

    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    vs_delta = round(res['roi_pct'] - res.get('baseline_roi_pct', 0.0), 1)
    st.caption(
        f"⚪ **Baseline (always back the favorite)**: "
        f"${res.get('baseline_final_bankroll_usd', 0):,.2f} final bankroll, "
        f"{res.get('baseline_roi_pct', 0):+.1f}% ROI over {res.get('baseline_bets', 0)} races "
        f"— the Bet Generator is **{vs_delta:+.1f}pp** ROI {'ahead' if vs_delta >= 0 else 'behind'} of naive favorite-backing. "
        f"It bet on {res['total_bets']} of {res.get('races_considered', res['total_bets'])} races, "
        f"sitting out {res.get('races_skipped', 0)} with no edge."
    )

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Plot Equity Curve
    fig_eq = EquineVisualization3D.build_backtest_equity_curve_chart(res)
    st.plotly_chart(fig_eq, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Trade Execution History Table
    st.markdown("<h5 style='color: var(--text-primary, #0F172A); font-weight: 800; animation: fadeIn 0.4s ease;'>📋 QUANTITATIVE TRADE EXECUTION LOG</h5>", unsafe_allow_html=True)
    if res.get("bets_history"):
        st.dataframe(
            [
                {
                    "Trade #": b["trade_id"],
                    "Date": b["date"],
                    "Course": b["course"],
                    "Bet Type": b["bet_type"],
                    "Runner(s)": b["runners"],
                    "Confidence": f"{b['confidence_pct']:.0f}/100",
                    "Odds": f"{b['odds']:.2f}",
                    "Stake": f"${b['stake_usd']:.2f}",
                    "Outcome": b["outcome"],
                    "Net P/L": f"${b['net_pl_usd']:+,.2f}",
                    "Cumulative Bankroll": f"${b['bankroll_usd']:,.2f}"
                }
                for b in res["bets_history"]
            ],
            width="stretch",
            hide_index=True
        )
