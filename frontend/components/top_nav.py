"""
SEABISCUIT - Ultra-Compact Top Bar Navigation (Premium High-Clarity Light Theme)
"""

import streamlit as st


def render_top_nav() -> None:
    """Renders a slim, compact top toolbar with exact requested header wording."""
    st.markdown("""
    <div style="background: #FFFFFF; border-bottom: 2px solid #4338CA; padding: 10px 20px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <span style="font-size: 1.4rem; font-weight: 900; color: #0F172A; letter-spacing: -0.5px;">
                🏇 SEABISCUIT <span style="color: #4338CA; font-size: 1.05rem; font-weight: 800;">// EQUINE ANALYTICS & INTELLIGENCE</span>
            </span>
            <span style="background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; padding: 3px 10px; border-radius: 12px; font-weight: 800; font-size: 0.75rem;">
                🟢 LIVE API
            </span>
        </div>
        <div style="font-size: 0.85rem; color: #475569; font-weight: 800; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;">
            HORSE RACING QUANT TERMINAL
        </div>
    </div>
    """, unsafe_allow_html=True)
