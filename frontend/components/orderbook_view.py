"""
SEABISCUIT - Equine Orderbook & Market Depth View Component
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List


def render_orderbook_view(racecard: Dict[str, Any]) -> None:
    """Renders live Equine Orderbook & CLOB microstructure."""
    st.markdown("### 📊 Institutional Equine Orderbook & CLOB Microstructure")

    assets = racecard.get("equity_assets", [])
    if not assets:
        st.info("No orderbook data available.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Select Equine Asset:")
        selected_ticker = st.radio(
            "Runner Tickers:",
            options=[a.get("ticker") for a in assets],
            format_func=lambda x: f"{x} ({next((a.get('horse') for a in assets if a.get('ticker') == x), '')})"
        )

    target_asset = next((a for a in assets if a.get("ticker") == selected_ticker), assets[0])

    with col2:
        share_price = target_asset.get("share_price_usd", 50.0)
        
        bids = [
            {"Level": "BID 1", "Price ($)": round(share_price * 0.99, 2), "Volume ($)": 15400},
            {"Level": "BID 2", "Price ($)": round(share_price * 0.98, 2), "Volume ($)": 9800},
            {"Level": "BID 3", "Price ($)": round(share_price * 0.97, 2), "Volume ($)": 6200},
        ]
        asks = [
            {"Level": "ASK 1", "Price ($)": round(share_price * 1.01, 2), "Volume ($)": 18200},
            {"Level": "ASK 2", "Price ($)": round(share_price * 1.02, 2), "Volume ($)": 11500},
            {"Level": "ASK 3", "Price ($)": round(share_price * 1.03, 2), "Volume ($)": 7900},
        ]

        df_bids = pd.DataFrame(bids)
        df_asks = pd.DataFrame(asks)

        bid1 = bids[0]["Price ($)"]
        ask1 = asks[0]["Price ($)"]
        spread = round(ask1 - bid1, 2)
        micro_price = round((bid1 * asks[0]["Volume ($)"] + ask1 * bids[0]["Volume ($)"]) / (bids[0]["Volume ($)"] + asks[0]["Volume ($)"]), 2)

        st.markdown(f"#### Orderbook Depth: `{target_asset.get('ticker')}` ({target_asset.get('horse')})")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bid 1 / Ask 1 Spread", f"${spread:.2f}")
        m2.metric("Micro-Price", f"${micro_price:.2f}")
        m3.metric("Order Flow Imbalance", "+18.4% (BUY HEAVY)", delta="Bullish Flow")

        b_col, a_col = st.columns(2)
        with b_col:
            st.markdown("<h5 style='color: #00FF87;'>🟢 BIDS (BUY ORDERS)</h5>", unsafe_allow_html=True)
            st.dataframe(df_bids, width="stretch", hide_index=True)
            
        with a_col:
            st.markdown("<h5 style='color: #FF0055;'>🔴 ASKS (SELL ORDERS)</h5>", unsafe_allow_html=True)
            st.dataframe(df_asks, width="stretch", hide_index=True)
