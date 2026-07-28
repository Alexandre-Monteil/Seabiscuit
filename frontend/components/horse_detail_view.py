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
        <h3 style="color: #0F172A; font-weight: 900; margin: 0;">
            🏇 {asset.get('horse')} <span style="color: #4338CA; font-family: 'JetBrains Mono';">({asset.get('ticker')})</span>
        </h3>
        <p style="color: #475569; font-size: 0.9rem; margin-top: 4px;">
            Pedigree: <b>{asset.get('sire')}</b> x <b>{asset.get('dam')}</b> | Age: <b>{asset.get('age')}yo {asset.get('sex')}</b> | Form: <b>{asset.get('form')}</b>
        </p>
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
