"""
SEABISCUIT - Ultra-Compact Top Bar Navigation (Premium High-Clarity Light Theme)
"""

import streamlit as st
from frontend.html_utils import compact_html


def render_top_nav() -> None:
    """Renders a slim, compact top toolbar with exact requested header wording."""
    st.markdown(compact_html("""
    <div class="glass-card" style="padding: 12px 22px; margin-bottom: 18px; border-bottom: 3px solid #6366F1; animation: slideInLeft 0.4s ease;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="font-size: 1.45rem; font-weight: 900; color: var(--text-primary, #0F172A); letter-spacing: -0.5px; font-family: 'Outfit', sans-serif;">
                    🏇 SEABISCUIT <span style="color: #6366F1; font-size: 1.05rem; font-weight: 800;">// EQUINE ANALYTICS &amp; INTELLIGENCE</span>
                </span>
                <span class="live-pulse" style="background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 0.75rem;">
                    🟢 LIVE API
                </span>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted, #475569); font-weight: 800; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;">
                HORSE RACING ANALYTICS TERMINAL
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)
