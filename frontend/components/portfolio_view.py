"""
SEABISCUIT - Equine Stock Portfolio & Backtesting View Component (100% English)
"""

import streamlit as st
from typing import List, Dict, Any
from backend.portfolio_engine import EquinePortfolioEngine


def render_portfolio_view(current_assets: List[Dict[str, Any]]) -> None:
    """Renders the equine trading portfolio and backtesting simulator."""
    st.markdown("## 💼 MY HORSE STOCK TRADING PORTFOLIO")
    
    if "portfolio_engine" not in st.session_state:
        st.session_state["portfolio_engine"] = EquinePortfolioEngine(initial_cash_usd=100000.0)

    engine: EquinePortfolioEngine = st.session_state["portfolio_engine"]
    summary = engine.get_portfolio_summary(current_assets)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Equity ($)", f"${summary['total_portfolio_val_usd']:,.2f}")
    c2.metric("Cash Balance ($)", f"${summary['cash_balance_usd']:,.2f}")
    c3.metric("Unrealized P&L ($)", f"${summary['unrealized_pnl_usd']:+,.2f}")
    c4.metric("Sharpe Ratio", summary["sharpe_ratio"])

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Active Market Positions & Holdings")
    
    holdings = summary.get("active_holdings", [])
    if holdings:
        st.dataframe(holdings, width="stretch", hide_index=True)
    else:
        st.info("No open positions. Browse the Turbo Terminal to buy (+EV Long) or short (Fade) horse equities!")


render_portfolio_simulator = render_portfolio_view
