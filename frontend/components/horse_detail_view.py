"""
SEABISCUIT - Horse Equine Asset Detail View (Ichimoku Cloud & Technical Analytics Overlay)
"""

import streamlit as st
from typing import Dict, Any
from backend.visualization_3d import EquineVisualization3D


def render_horse_detail_view(asset: Dict[str, Any], racecard: Dict[str, Any]) -> None:
    """Renders deep technical equity dossier overlay with Ichimoku Cloud & 6D Radar."""
    st.markdown("""
    <div class="glass-card" style="border-top: 4px solid #6366F1; padding: 20px; margin-bottom: 20px; animation: fadeIn 0.5s ease;">
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([3, 1])

    with d_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(248,250,252,0.9) 0%, rgba(238,242,255,0.9) 100%); padding: 14px 18px; border-radius: 10px; border-left: 4px solid #6366F1; margin-bottom: 8px; backdrop-filter: blur(6px);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px; flex-wrap: wrap;">
                <h3 style="color: var(--text-primary, #0F172A); font-weight: 900; margin: 0; font-size: 1.6rem; letter-spacing: -0.5px; font-family: 'Outfit', sans-serif;">
                    🏇 {asset.get('horse')}
                </h3>
                <span style="background: #6366F1; color: #FFFFFF; font-family: 'JetBrains Mono'; font-weight: 800; padding: 3px 10px; border-radius: 6px; font-size: 0.85rem;">{asset.get('ticker')}</span>
                <span style="background: #F1F5F9; color: #475569; font-weight: 800; border: 1px solid #CBD5E1; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase;">{asset.get('age')}yo {asset.get('sex')}</span>
                <span style="background: #ECFDF5; color: #047857; font-weight: 800; border: 1px solid #A7F3D0; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase;">Form: {asset.get('form')}</span>
            </div>
            <div style="color: var(--text-muted, #64748B); font-size: 0.85rem; font-weight: 600;">
                Pedigree: <span style="color: var(--text-secondary, #334155); font-weight: 800;">{asset.get('sire')}</span> × <span style="color: var(--text-secondary, #334155); font-weight: 800;">{asset.get('dam')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d_col2:
        if st.button("❌ CLOSE DOSSIER", key="btn_close_dossier", use_container_width=True):
            st.session_state["selected_horse_ticker"] = None
            st.rerun()

    # Technical Charts Row: Ichimoku Cloud & 6D Quant Radar
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_ichi = EquineVisualization3D.build_equine_ichimoku_cloud_chart(asset)
        st.plotly_chart(fig_ichi, width="stretch", config={"responsive": True, "displayModeBar": False})

    with chart_col2:
        fig_radar = EquineVisualization3D.build_6d_equine_quant_radar(asset)
        st.plotly_chart(fig_radar, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("</div>", unsafe_allow_html=True)
