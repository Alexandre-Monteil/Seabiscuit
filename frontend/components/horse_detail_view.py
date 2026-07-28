"""
SEABISCUIT - Horse Equine Asset Detail View (Ichimoku Cloud & Technical Analytics Overlay)
"""

import streamlit as st
from typing import Dict, Any
from backend.utils import safe_float, safe_int
from backend.visualization_3d import EquineVisualization3D


def render_horse_detail_view(asset: Dict[str, Any], racecard: Dict[str, Any]) -> None:
    """Renders deep technical equity dossier overlay with Ichimoku Cloud & 6D Radar."""
    st.markdown("""
    <div style="background: #FFFFFF; border: 2px solid #4338CA; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(67, 56, 202, 0.15);">
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([3, 1])

    with d_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #F8FAFC 0%, #EEF2FF 100%); padding: 12px 16px; border-radius: 8px; border-left: 4px solid #4338CA; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                <h3 style="color: #0F172A; font-weight: 900; margin: 0; font-size: 1.6rem; letter-spacing: -0.5px;">
                    🏇 {asset.get('horse')}
                </h3>
                <span style="background: #4338CA; color: #FFFFFF; font-family: 'JetBrains Mono'; font-weight: 800; padding: 2px 8px; border-radius: 6px; font-size: 0.85rem;">{asset.get('ticker')}</span>
                <span style="background: #F1F5F9; color: #475569; font-weight: 800; border: 1px solid #CBD5E1; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase;">{asset.get('age')}yo {asset.get('sex')}</span>
                <span style="background: #ECFDF5; color: #047857; font-weight: 800; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase;">Form: {asset.get('form')}</span>
            </div>
            <div style="color: #64748B; font-size: 0.85rem; font-weight: 600;">
                Pedigree: <span style="color: #334155; font-weight: 800;">{asset.get('sire')}</span> × <span style="color: #334155; font-weight: 800;">{asset.get('dam')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d_col2:
        if st.button("❌ CLOSE DOSSIER", key="btn_close_dossier", width="stretch"):
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
