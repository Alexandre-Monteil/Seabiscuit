"""
SEABISCUIT - Single-Page Mega Bloomberg Terminal Dashboard (Hero Bet Simulator & Full Metric Weather Edition)
Features top prominent bet simulator, weather infobar with full metric distances (m & yds), EV-sorted cards, and all 12 Plotly models.
"""

import os
import sys
from datetime import datetime
import streamlit as st

# Path-safety setup
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.utils import safe_float, safe_int, parse_race_datetime, format_race_distance, get_race_weather_info
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

# ─── PREMIUM DESIGN SYSTEM: LIGHT / TRADING / PROFESSIONNEL / TECHNIQUE ───
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&family=Outfit:wght@400;600;700;800;900&display=swap');

:root {
  --bg-primary: #F8FAFC;
  --bg-secondary: #EFF3F8;
  --bg-card: rgba(255,255,255,0.72);
  --text-primary: #0F172A;
  --text-secondary: #334155;
  --text-muted: #64748B;
  --accent-emerald: #10B981;
  --accent-cyan: #0284C7;
  --accent-amber: #F59E0B;
  --accent-violet: #6366F1;
  --accent-gold: #EAB308;
  --accent-rose: #F43F5E;
  --card-border: rgba(203,213,225,0.6);
  --card-shadow: 0 4px 20px rgba(15,23,42,0.06);
  --card-shadow-hover: 0 12px 32px rgba(15,23,42,0.12);
  --radius-lg: 14px;
  --radius-md: 10px;
  --radius-sm: 6px;
}

/* ── Base ── */
.stApp { background: var(--bg-primary) !important; font-family: 'Inter', 'Outfit', -apple-system, sans-serif !important; }
h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', 'Inter', sans-serif !important; letter-spacing: -0.3px; }

/* ── Glass Card ── */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(16px) saturate(1.4);
  -webkit-backdrop-filter: blur(16px) saturate(1.4);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  transition: transform 0.28s cubic-bezier(.4,0,.2,1), box-shadow 0.28s cubic-bezier(.4,0,.2,1);
}
.glass-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

/* ── Animations ── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-18px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.25); }
  50%      { box-shadow: 0 0 12px 4px rgba(16,185,129,0.15); }
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ── Table Enhancements ── */
table { font-family: 'Inter', sans-serif !important; }
table thead tr { position: sticky; top: 0; z-index: 1; }
table tbody tr { transition: background-color 0.18s ease; }
table tbody tr:hover { background-color: rgba(99,102,241,0.04) !important; }

/* ── Metric Cards ── */
[data-testid="stMetric"] {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 14px 16px !important;
  box-shadow: var(--card-shadow);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}
[data-testid="stMetricLabel"] { font-weight: 800 !important; text-transform: uppercase; font-size: 0.72rem !important; letter-spacing: 0.4px; color: var(--text-muted) !important; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; font-weight: 900 !important; color: var(--text-primary) !important; }

/* ── Buttons ── */
.stButton > button {
  background: var(--bg-primary) !important;
  color: var(--accent-cyan) !important;
  border: 2px solid var(--accent-cyan) !important;
  font-weight: 800 !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Inter', sans-serif !important;
  letter-spacing: 0.3px;
  transition: all 0.22s cubic-bezier(.4,0,.2,1) !important;
}
.stButton > button:hover {
  background: var(--accent-cyan) !important;
  color: #FFFFFF !important;
  box-shadow: 0 6px 18px rgba(2,132,199,0.28) !important;
  transform: translateY(-1px);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  transition: background 0.2s ease, color 0.2s ease !important;
}

/* ── Expander ── */
.streamlit-expanderHeader { font-weight: 800 !important; font-size: 0.95rem !important; letter-spacing: -0.2px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ── DataFrames ── */
.stDataFrame { border-radius: var(--radius-md) !important; overflow: hidden; box-shadow: var(--card-shadow); }

/* ── Live badge pulse ── */
.live-pulse { animation: pulseGlow 2s ease-in-out infinite; }
</style>""", unsafe_allow_html=True)


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
        show_pepites_only = st.checkbox("🟢 +EV Value Bets Only", value=False)

    # WEATHER & FULL METRIC DISTANCE INFOBAR
    course_name = str(current_racecard.get('course', 'Ascot')).upper()
    dist_full = format_race_distance(current_racecard.get('distance_display') or current_racecard.get('distance_furlongs'), current_racecard.get('distance_furlongs'))
    going_name = str(current_racecard.get('going', 'Good'))
    post_time = str(current_racecard.get('post_time', '15:35'))
    date_str = str(current_racecard.get('race_date_display', 'Today'))
    weather_info = get_race_weather_info(current_racecard)
    
    current_dt = parse_race_datetime(current_racecard)
    is_live = current_dt >= now
    live_cls = "live-pulse" if is_live else ""
    status_badge = f"<span class='{live_cls}' style='background: #10B981; color: #FFFFFF; font-weight: 900; padding: 4px 12px; border-radius: 6px; font-size: 0.8rem;'>🟢 LIVE UPCOMING</span>" if is_live else "<span style='background: #64748B; color: #FFFFFF; font-weight: 900; padding: 4px 12px; border-radius: 6px; font-size: 0.8rem;'>🏁 COMPLETED EVENT</span>"

    st.markdown(f"""
    <div class="glass-card" style="padding: 16px 22px; margin-bottom: 18px; animation: slideInLeft 0.5s ease;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; font-size: 0.92rem; color: var(--text-primary);">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                {status_badge}
                <span style="color: var(--card-border);">│</span>
                📍 <b style="color: var(--accent-violet); font-size: 1.05rem;">{course_name}</b>
                <span style="color: var(--card-border);">│</span>
                📅 <b style="color: var(--accent-cyan);">{date_str}</b>
                <span style="color: var(--card-border);">│</span>
                ⏱️ <b style="color: var(--accent-emerald);">{post_time} GMT</b>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--text-secondary);">
                📏 <b>{dist_full}</b>
                <span style="color: var(--card-border);">│</span>
                {weather_info}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    equity_assets = current_racecard.get("equity_assets", [])
    if show_pepites_only:
        equity_assets = [a for a in equity_assets if isinstance(a, dict) and a.get("asset_tag") == "VALUE_BUY"]

    # ---------------------------------------------------------
    # PROMINENT HERO FEATURE 1: BET & COMBINATION SIMULATOR
    # ---------------------------------------------------------
    render_bet_simulator_view(current_racecard)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # PROMINENT HERO FEATURE 2: TOP RACE EXECUTIVE SUMMARY TABLE
    # ---------------------------------------------------------
    st.markdown("<h4 style='color: var(--text-primary); font-weight: 900; margin-bottom: 10px; animation: fadeIn 0.4s ease;'>📋 RACE RUNNERS EXECUTIVE SUMMARY TABLE</h4>", unsafe_allow_html=True)
    
    sorted_for_table = sorted(
        equity_assets,
        key=lambda a: safe_float(a.get("expected_value_pct") if isinstance(a, dict) else 0.0, default=0.0),
        reverse=True
    )

    table_html = """
    <div class="glass-card" style="overflow-x: auto; margin-bottom: 18px; animation: fadeIn 0.5s ease;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', 'Outfit', sans-serif;">
        <thead>
            <tr style="background: linear-gradient(90deg, #F1F5F9 0%, #E8ECF2 100%); border-bottom: 2px solid #CBD5E1; text-align: left; color: #475569; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.4px;">
                <th style="padding: 14px 16px; font-weight: 800;">Rank</th>
                <th style="padding: 14px 16px; font-weight: 800;">Runner (Ticker)</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: right;">Odds</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: right;">Exp. Profit (EV %)</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: center;">Value Index</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: center;">Speed Rtg</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: center;">Rec. Stake</th>
                <th style="padding: 14px 16px; font-weight: 800; text-align: center;">Seabiscuit Status</th>
            </tr>
        </thead>
        <tbody>
    """

    for idx, a in enumerate(sorted_for_table):
        if not isinstance(a, dict):
            continue
        ev_p = safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), 0.0)
        
        if ev_p > 4.0:
            status_html = "<span style='background: #10B981; color: #FFFFFF; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.75rem;'>🟢 TOP VALUE (+EV)</span>"
            ev_bg = "background: rgba(16, 185, 129, 0.1);"
            ev_color = "#059669"
        elif ev_p < -5.0:
            status_html = "<span style='background: #F43F5E; color: #FFFFFF; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.75rem;'>🔴 OVERPRICED (-EV)</span>"
            ev_bg = "background: rgba(244, 63, 94, 0.1);"
            ev_color = "#E11D48"
        else:
            status_html = "<span style='background: #F59E0B; color: #FFFFFF; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.75rem;'>🟡 VALUE HEDGE</span>"
            ev_bg = ""
            ev_color = "#0F172A"

        row_bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
        
        table_html += f"""
            <tr style="background-color: {row_bg}; border-bottom: 1px solid #E2E8F0; transition: background-color 0.2s ease;">
                <td style="padding: 14px 16px; font-weight: 900; color: #94A3B8;">#{idx+1}</td>
                <td style="padding: 14px 16px;">
                    <div style="font-weight: 800; color: #0F172A; font-size: 1.05rem;">{a.get('horse', 'Runner')}</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #64748B;">{a.get('ticker', '$RUNNER')}</div>
                </td>
                <td style="padding: 14px 16px; font-weight: 800; color: #0284C7; font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; text-align: right;">{safe_float(a.get('decimal_odds'), 4.0):.2f}</td>
                <td style="padding: 14px 16px; font-weight: 900; color: {ev_color}; {ev_bg} text-align: right; font-family: 'JetBrains Mono', monospace;">{ev_p:+.1f}%</td>
                <td style="padding: 14px 16px; font-weight: 700; text-align: center; font-family: 'JetBrains Mono', monospace;">{safe_float(a.get('ae_ratio'), 1.0):.2f}</td>
                <td style="padding: 14px 16px; font-weight: 900; color: #4338CA; text-align: center;">{safe_int(a.get('beyer_speed'), 110)}</td>
                <td style="padding: 14px 16px; font-weight: 800; color: #047857; text-align: center;">{safe_float(a.get('kelly_stake_pct'), 0.0):.1f}%</td>
                <td style="padding: 14px 16px; text-align: center;">{status_html}</td>
            </tr>
        """
        
    table_html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SECTION 3: RUNNER ASSET CARDS SORTED BY EV % DESCENDING
    # ---------------------------------------------------------
    selected_ticker = st.session_state.get("selected_horse_ticker")
    selected_asset = next((a for a in equity_assets if isinstance(a, dict) and a.get("ticker") == selected_ticker), None)
    if selected_asset:
        render_horse_detail_view(selected_asset, current_racecard)
        st.markdown("---")

    render_stock_asset_cards(equity_assets)

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 4: STRATEGY BACKTEST EQUITIES & P/L TRACKER
    # ---------------------------------------------------------
    with st.expander("📈 SEABISCUIT +EV STRATEGY BACKTEST & CUMULATIVE P/L TRACKER", expanded=False):
        render_backtest_view(all_racecards)

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 5: COMPLETE 12-MODEL QUANT VISUAL ANALYTICS SUITE
    # ---------------------------------------------------------
    st.markdown("<h4 style='color: var(--text-primary); font-weight: 900; margin-bottom: 14px; animation: fadeIn 0.4s ease;'>📊 COMPLETE QUANTITATIVE VISUAL ANALYTICS SUITE (ALL 12 MODELS)</h4>", unsafe_allow_html=True)

    # Row 1: Treemap & Finishing Position Probabilities (Model 1 & 10)
    col1, col2 = st.columns(2)
    with col1:
        fig_tree = EquineVisualization3D.build_race_market_treemap(equity_assets)
        st.plotly_chart(fig_tree, width="stretch", config={"responsive": True, "displayModeBar": False})
    with col2:
        fig_pos = EquineVisualization3D.build_finishing_position_stacked_chart(equity_assets)
        st.plotly_chart(fig_pos, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Row 2: Monte Carlo 10,000 Sim & Risk/Return Efficient Frontier (Model 3 & 11)
    col3, col4 = st.columns(2)
    with col3:
        fig_mc = EquineVisualization3D.build_monte_carlo_win_distribution_chart(equity_assets)
        st.plotly_chart(fig_mc, width="stretch", config={"responsive": True, "displayModeBar": False})
    with col4:
        fig_rr = EquineVisualization3D.build_risk_return_efficient_frontier_chart(equity_assets)
        st.plotly_chart(fig_rr, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Row 3: EV Scatter Matrix & Furlong Velocity Profile (Model 4 & 5)
    col5, col6 = st.columns(2)
    with col5:
        fig_ev = EquineVisualization3D.build_alpha_ev_scatter_matrix(equity_assets)
        st.plotly_chart(fig_ev, width="stretch", config={"responsive": True, "displayModeBar": False})
    with col6:
        fig_vel = EquineVisualization3D.build_furlong_velocity_profile_chart(equity_assets)
        st.plotly_chart(fig_vel, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Row 4: Furlong Speed Burst Acceleration Heatmap & Beyer Speed Rating Progression (Model 12 & 6)
    col7, col8 = st.columns(2)
    with col7:
        fig_heat = EquineVisualization3D.build_furlong_acceleration_heatmap(equity_assets)
        st.plotly_chart(fig_heat, width="stretch", config={"responsive": True, "displayModeBar": False})
    with col8:
        fig_beyer = EquineVisualization3D.build_beyer_speed_progression_chart(equity_assets)
        st.plotly_chart(fig_beyer, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # Row 5: 3D Speed Terrain Surface & Multi-Runner Price Trajectory Overlay (Model 7 & 8)
    col9, col10 = st.columns(2)
    with col9:
        moisture_val = safe_float(current_racecard.get("moisture_percent"), default=20.0)
        fig_3d = EquineVisualization3D.build_3d_track_speed_terrain(moisture_val)
        st.plotly_chart(fig_3d, width="stretch", config={"responsive": True, "displayModeBar": False})
    with col10:
        fig_traj = EquineVisualization3D.build_multi_runner_trajectory_chart(equity_assets)
        st.plotly_chart(fig_traj, width="stretch", config={"responsive": True, "displayModeBar": False})

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 6: DEEPSEEK AI MARKET DOSSIER & STABLE SYNERGY
    # ---------------------------------------------------------
    st.markdown("<h4 style='color: #0F172A; font-weight: 900;'>🤖 DEEPSEEK AI EXECUTIVE DOSSIER & STABLE SYNERGY</h4>", unsafe_allow_html=True)
    
    intel_col1, intel_col2 = st.columns(2)
    
    with intel_col1:
        st.markdown("<h5 style='color: #4338CA; font-weight: 800;'>🤝 JOCKEY x OWNER SYNERGY BREAKDOWN</h5>", unsafe_allow_html=True)
        try:
            client = TheRacingAPIClient()
            jockey_data = client.get_jockey_owner_analysis()
            owners = jockey_data.get("owners", [])
            
            st.dataframe(
                [{"Owner / Stable": o.get("owner", "Owner"), "Rides": safe_int(o.get("rides")), "Wins": safe_int(o.get("1st")), "Win Rate": f"{safe_float(o.get('win_%'))*100:.0f}%", "Value Index (A/E)": safe_float(o.get("a/e")), "1-Unit P/L": f"${safe_float(o.get('1_pl')):+,.2f}"} for o in owners if isinstance(o, dict)],
                width="stretch",
                hide_index=True
            )
        except Exception:
            st.info("Jockey & owner synergy data loading.")

    with intel_col2:
        with st.expander("🤖 GENERATE DEEPSEEK AI EXECUTIVE INTEL DOSSIER", expanded=True):
            render_intel_dossier_modal(current_racecard)

    st.markdown("---")
    st.caption("⚡ **SEABISCUIT SINGLE-PAGE MEGA BLOOMBERG TERMINAL** | Live Racing API Analytics & AI Intelligence.")


if __name__ == "__main__":
    main()
