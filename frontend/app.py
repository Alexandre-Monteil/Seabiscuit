"""
SEABISCUIT - Single-Page Mega Bloomberg Terminal Dashboard (World-Class Data Design & Structured Tabs Edition)
Organizes quantitative data, analytics, simulators, backtesting, and AI dossiers into 4 sleek institutional tabs.
"""

import os
import sys
from datetime import datetime
import streamlit as st

# Path-safety setup
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.utils import safe_float, safe_int, parse_race_datetime
from backend.theracingapi_client import TheRacingAPIClient
from backend.equine_stock_engine import EquineStockEngine
from backend.visualization_3d import EquineVisualization3D
from frontend.components.top_nav import render_top_nav
from frontend.components.stock_cards import render_stock_asset_cards
from frontend.components.horse_detail_view import render_horse_detail_view
from frontend.components.intel_modal import render_intel_dossier_modal
from frontend.components.bet_simulator_view import render_bet_simulator_view
from frontend.components.backtest_view import render_backtest_view

# Streamlit Page Setup
st.set_page_config(
    page_title="SEABISCUIT // Equine Quant Terminal 🏇⚡",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# DRASTIC ULTRA-CLARITY HIGH-CONTRAST LIGHT & CRISP CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    .stApp {
        background: #F8FAFC !important;
    }

    .gaming-card-green {
        background: #FFFFFF !important;
        border: 2px solid #10B981 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.12) !important;
        border-radius: 12px;
    }
    
    .gaming-card-red {
        background: #FFFFFF !important;
        border: 2px solid #F43F5E !important;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.12) !important;
        border-radius: 12px;
    }

    .gaming-card-gold {
        background: #FFFFFF !important;
        border: 2px solid #F59E0B !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.12) !important;
        border-radius: 12px;
    }

    .badge-pepite {
        background: #10B981 !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.5px !important;
    }
    
    .badge-piege {
        background: #F43F5E !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.5px !important;
    }

    .badge-outsider {
        background: #F59E0B !important;
        color: #000000 !important;
        font-weight: 900 !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.5px !important;
    }

    .quant-pill {
        background: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
        text-align: center !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        color: #0F172A !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 800 !important;
        color: #475569 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
        font-weight: 700 !important;
    }

    /* Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #FFFFFF;
        border-radius: 8px;
        color: #475569;
        font-weight: 800;
        font-size: 0.95rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4338CA !important;
        color: #FFFFFF !important;
    }

    .stButton > button {
        background: #FFFFFF !important;
        color: #4338CA !important;
        border: 2px solid #4338CA !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background: #4338CA !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(67, 56, 202, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=15, show_spinner=False)
def fetch_race_data():
    """Fetches live racecard data across 15-day J-7 to J+7 horizon from The Racing API safely."""
    try:
        client = TheRacingAPIClient()
        raw_racecards = client.get_upcoming_racecards(past_days=7, future_days=7)
        if not raw_racecards:
            return []
        processed = [EquineStockEngine.process_racecard(rc) for rc in raw_racecards if isinstance(rc, dict)]
        
        now = datetime.now()
        upcoming = [rc for rc in processed if parse_race_datetime(rc) >= now]
        past = [rc for rc in processed if parse_race_datetime(rc) < now]
        
        upcoming_sorted = sorted(upcoming, key=parse_race_datetime)
        past_sorted = sorted(past, key=parse_race_datetime, reverse=True)
        
        return upcoming_sorted + past_sorted
    except Exception:
        return []


def main():
    render_top_nav()

    all_racecards = fetch_race_data()
    if not all_racecards:
        st.error("⚠️ Failed to load live racecards from The Racing API. Check credentials or network connectivity.")
        return

    now = datetime.now()

    # MULTI-DAY J-7 TO J+7 DATE FILTER BAR
    dates_map = {}
    for rc in all_racecards:
        d_key = str(rc.get("race_date", "2026-07-28"))
        d_lbl = str(rc.get("race_date_display", d_key))
        dates_map[d_lbl] = d_key

    date_options = ["📅 All Horizon Dates (J-7 to J+7)"] + list(dates_map.keys())
    
    date_col, race_col, filter_col = st.columns([1.5, 3.5, 1])
    
    with date_col:
        selected_date_lbl = st.selectbox("Date Filter:", date_options, label_visibility="collapsed")
        
    if selected_date_lbl != "📅 All Horizon Dates (J-7 to J+7)":
        target_date = dates_map.get(selected_date_lbl)
        active_racecards = [rc for rc in all_racecards if str(rc.get("race_date")) == target_date]
        if not active_racecards:
            active_racecards = all_racecards
    else:
        active_racecards = all_racecards

    # Build Race Selector Labels
    race_options = []
    for rc in active_racecards:
        rc_dt = parse_race_datetime(rc)
        is_upcoming = rc_dt >= now
        status_tag = "🟢 NEXT DEPARTURE" if is_upcoming else "🏁 FINISHED"
        race_options.append(f"{status_tag} | {rc.get('course', 'Track')} — {rc.get('race_name', 'Stakes')} ({rc.get('race_date_display', '')} @ {rc.get('post_time', '15:00')})")

    with race_col:
        selected_idx = st.selectbox(
            "Race Event Selector:",
            range(len(race_options)),
            index=0,
            format_func=lambda i: race_options[i],
            label_visibility="collapsed"
        )
        if selected_idx >= len(active_racecards):
            selected_idx = 0
        current_racecard = active_racecards[selected_idx]

    with filter_col:
        show_pepites_only = st.checkbox("🟢 +EV Nuggets Only", value=False)

    # INFOBAR DETAILS
    course_name = str(current_racecard.get('course', 'Ascot')).upper()
    dist_full = str(current_racecard.get('distance_display', '7f (7 Furlongs — 1,400m / 1,540 yds)'))
    going_name = str(current_racecard.get('going', 'Good'))
    post_time = str(current_racecard.get('post_time', '15:35'))
    date_str = str(current_racecard.get('race_date_display', 'Today'))
    
    current_dt = parse_race_datetime(current_racecard)
    is_live = current_dt >= now
    status_badge = "<span style='background: #10B981; color: #FFFFFF; font-weight: 900; padding: 3px 10px; border-radius: 4px;'>🟢 LIVE UPCOMING</span>" if is_live else "<span style='background: #64748B; color: #FFFFFF; font-weight: 900; padding: 3px 10px; border-radius: 4px;'>🏁 COMPLETED EVENT</span>"

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px 18px; border-radius: 10px; font-size: 0.95rem; color: #0F172A; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px;">
        {status_badge} &nbsp;|&nbsp; 📍 <b style="color: #4338CA; font-size: 1.05rem;">{course_name}</b> &nbsp;|&nbsp; 📅 <b style="color: #0284C7;">{date_str}</b> &nbsp;|&nbsp; ⏱️ <b style="color: #059669;">{post_time} GMT</b> &nbsp;|&nbsp; 📏 <b>{dist_full}</b> &nbsp;|&nbsp; 🌧️ <b>{going_name}</b>
    </div>
    """, unsafe_allow_html=True)

    equity_assets = current_racecard.get("equity_assets", [])
    if show_pepites_only:
        equity_assets = [a for a in equity_assets if isinstance(a, dict) and a.get("asset_tag") == "VALUE_BUY"]

    # Key KPIs Row
    k1, k2, k3, k4, k5 = st.columns(5)
    value_count = sum(1 for a in equity_assets if isinstance(a, dict) and a.get("asset_tag") == "VALUE_BUY")
    fade_count = sum(1 for a in equity_assets if isinstance(a, dict) and a.get("asset_tag") == "OVERVALUED_FADE")
    
    total_beyer = sum(safe_int(a.get("beyer_speed"), 100) for a in equity_assets if isinstance(a, dict))
    avg_beyer = int(total_beyer / max(1, len(equity_assets)))

    k1.metric("Runners Pool", len(equity_assets))
    k2.metric("🟢 +EV Nuggets", value_count)
    k3.metric("🔴 Overpriced Fades", fade_count)
    k4.metric("Avg Beyer Speed", avg_beyer)
    k5.metric("Purse Pool", f"${safe_float(current_racecard.get('prize_money_usd'), 15000.0):,.0f}")

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # MAIN BLOOMBERG TERMINAL STRUCTURED TABS SYSTEM
    # ---------------------------------------------------------
    t_equities, t_visuals, t_simulators, t_intel = st.tabs([
        "🏇 RUNNER EQUITIES & ASSETS",
        "📊 QUANT VISUAL ANALYTICS",
        "🎰 BET SIMULATORS & BACKTEST",
        "🤖 AI DOSSIER & STABLE SYNERGY"
    ])

    # ---------------------------------------------------------
    # TAB 1: RUNNER EQUITIES & ASSETS
    # ---------------------------------------------------------
    with t_equities:
        selected_ticker = st.session_state.get("selected_horse_ticker")
        selected_asset = next((a for a in equity_assets if isinstance(a, dict) and a.get("ticker") == selected_ticker), None)
        if selected_asset:
            render_horse_detail_view(selected_asset, current_racecard)
            st.markdown("---")

        render_stock_asset_cards(equity_assets)

    # ---------------------------------------------------------
    # TAB 2: QUANT VISUAL ANALYTICS (7 CHARTS GRID)
    # ---------------------------------------------------------
    with t_visuals:
        st.markdown("<h4 style='color: #0F172A; font-weight: 900; margin-bottom: 14px;'>📊 ADVANCED QUANT VISUAL ANALYTICS DASHBOARD</h4>", unsafe_allow_html=True)
        
        # Row 1: Treemap & Monte Carlo
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_tree = EquineVisualization3D.build_race_market_treemap(equity_assets)
            st.plotly_chart(fig_tree, width="stretch", config={"responsive": True, "displayModeBar": False})

        with chart_col2:
            fig_mc = EquineVisualization3D.build_monte_carlo_win_distribution_chart(equity_assets)
            st.plotly_chart(fig_mc, width="stretch", config={"responsive": True, "displayModeBar": False})

        st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

        # Row 2: EV Scatter Matrix & Furlong Velocity
        pace_col1, pace_col2 = st.columns(2)
        with pace_col1:
            fig_ev = EquineVisualization3D.build_alpha_ev_scatter_matrix(equity_assets)
            st.plotly_chart(fig_ev, width="stretch", config={"responsive": True, "displayModeBar": False})

        with pace_col2:
            fig_vel = EquineVisualization3D.build_furlong_velocity_profile_chart(equity_assets)
            st.plotly_chart(fig_vel, width="stretch", config={"responsive": True, "displayModeBar": False})

        st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

        # Row 3: 3D Terrain & Beyer Speed Progression
        row4_col1, row4_col2 = st.columns(2)
        with row4_col1:
            moisture_val = safe_float(current_racecard.get("moisture_percent"), default=20.0)
            fig_3d = EquineVisualization3D.build_3d_track_speed_terrain(moisture_val)
            st.plotly_chart(fig_3d, width="stretch", config={"responsive": True, "displayModeBar": False})

        with row4_col2:
            fig_beyer = EquineVisualization3D.build_beyer_speed_progression_chart(equity_assets)
            st.plotly_chart(fig_beyer, width="stretch", config={"responsive": True, "displayModeBar": False})

        st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

        # Row 4: Multi-Runner Trajectory Line
        fig_traj = EquineVisualization3D.build_multi_runner_trajectory_chart(equity_assets)
        st.plotly_chart(fig_traj, width="stretch", config={"responsive": True, "displayModeBar": False})

    # ---------------------------------------------------------
    # TAB 3: BET SIMULATORS & BACKTEST
    # ---------------------------------------------------------
    with t_simulators:
        sim_sub_tab1, sim_sub_tab2 = st.tabs(["🎰 BET COMBINATION SIMULATOR", "📈 SEABISCUIT +EV STRATEGY BACKTEST"])
        with sim_sub_tab1:
            render_bet_simulator_view(current_racecard)
        with sim_sub_tab2:
            render_backtest_view(all_racecards)

    # ---------------------------------------------------------
    # TAB 4: AI MARKET INTEL DOSSIER & JOCKEY SYNERGY
    # ---------------------------------------------------------
    with t_intel:
        st.markdown("<h4 style='color: #0F172A; font-weight: 900;'>🤖 DEEPSEEK AI EXECUTIVE INTEL & STABLE SYNERGY</h4>", unsafe_allow_html=True)
        render_intel_dossier_modal(current_racecard)
        
        st.markdown("---")
        st.markdown("<h4 style='color: #0F172A; font-weight: 900;'>🤝 JOCKEY x OWNER SYNERGY BREAKDOWN</h4>", unsafe_allow_html=True)
        try:
            client = TheRacingAPIClient()
            jockey_data = client.get_jockey_owner_analysis()
            owners = jockey_data.get("owners", [])
            
            st.dataframe(
                [{"Owner / Stable": o.get("owner", "Owner"), "Rides": safe_int(o.get("rides")), "Wins": safe_int(o.get("1st")), "Win Rate": f"{safe_float(o.get('win_%'))*100:.0f}%", "A/E Ratio": safe_float(o.get("a/e")), "1-Unit P/L": f"${safe_float(o.get('1_pl')):+,.2f}"} for o in owners if isinstance(o, dict)],
                width="stretch",
                hide_index=True
            )
        except Exception:
            st.info("Jockey & owner synergy data loading.")

    st.markdown("---")
    st.caption("⚡ **SEABISCUIT SINGLE-PAGE MEGA BLOOMBERG TERMINAL** | Live Racing API Analytics & AI Intelligence.")


if __name__ == "__main__":
    main()
