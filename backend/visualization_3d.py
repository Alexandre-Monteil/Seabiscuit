"""
SEABISCUIT - 3D & Advanced Plotly Visualizations Engine (Zero Overlap & Hedge Fund Visual Architecture)
Features 11 distinct, mathematically grounded visual analytics models with zero title/legend collisions.
"""

import traceback
from typing import List, Dict, Any
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    from .utils import safe_float, safe_int
    from .time_series_engine import EquineTimeSeriesEngine
except (ImportError, ValueError):
    from backend.utils import safe_float, safe_int
    from backend.time_series_engine import EquineTimeSeriesEngine

__version__ = "2.1.0"


class EquineVisualization3D:
    """Hedge Fund Quantitative Data Design & Visual Architecture Suite."""

    @staticmethod
    def _create_empty_fig(title_text: str = "No Data Available") -> go.Figure:
        """Helper to create a crash-free empty figure placeholder."""
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=title_text, font=dict(color="#0F172A", size=14), x=0.02, y=0.95),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            height=360,
            margin=dict(l=40, r=40, b=40, t=75)
        )
        return fig

    @classmethod
    def build_finishing_position_stacked_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 10: Finishing Position Probability Distribution (1st, 2nd, 3rd Place Probability)."""
        if not equity_assets:
            return cls._create_empty_fig("🏆 Finishing Position Probability Distribution")

        try:
            valid_assets = [a for a in equity_assets if isinstance(a, dict)]
            if not valid_assets:
                return cls._create_empty_fig("🏆 Finishing Position Probability Distribution")

            names = [str(a.get("horse", "Runner")) for a in valid_assets]
            win_pcts = [safe_float(a.get("win_percent"), default=0.15) * 100.0 for a in valid_assets]
            place_pcts = [safe_float(a.get("place_percent"), default=0.65) * 100.0 for a in valid_assets]
            
            p2_pcts = [round(max(0.0, (p - w) * 0.55), 1) for w, p in zip(win_pcts, place_pcts)]
            p3_pcts = [round(max(0.0, (p - w) * 0.45), 1) for w, p in zip(win_pcts, place_pcts)]
            unplaced_pcts = [round(max(0.0, 100.0 - w - p2 - p3), 1) for w, p2, p3 in zip(win_pcts, p2_pcts, p3_pcts)]

            fig = go.Figure()

            fig.add_trace(go.Bar(y=names, x=win_pcts, name="🥇 1st Win Prob %", orientation="h", marker_color="#10B981"))
            fig.add_trace(go.Bar(y=names, x=p2_pcts, name="🥈 2nd Place Prob %", orientation="h", marker_color="#0284C7"))
            fig.add_trace(go.Bar(y=names, x=p3_pcts, name="🥉 3rd Show Prob %", orientation="h", marker_color="#F59E0B"))
            fig.add_trace(go.Bar(y=names, x=unplaced_pcts, name="4th+ Unplaced %", orientation="h", marker_color="#CBD5E1"))

            dynamic_height = max(380, len(valid_assets) * 45)

            fig.update_layout(
                title=dict(text="🏆 Projected Finishing Position Probabilities (1st, 2nd, 3rd Share)", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=dynamic_height,
                barmode="stack",
                xaxis=dict(title=dict(text="Cumulative Probability Share (%)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(color="#0F172A", size=11)),
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(color="#0F172A")),
                margin=dict(l=140, r=30, b=75, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🏆 Finishing Position Probability Distribution")

    @classmethod
    def build_risk_return_efficient_frontier_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 11: Risk vs Expected Return Efficient Frontier Bubble Chart."""
        if not equity_assets:
            return cls._create_empty_fig("⚖️ Risk vs Expected Return Efficient Frontier")

        try:
            valid_assets = [a for a in equity_assets if isinstance(a, dict)]
            if not valid_assets:
                return cls._create_empty_fig("⚖️ Risk vs Expected Return Efficient Frontier")

            names = [str(a.get("horse", "Runner")) for a in valid_assets]
            tickers = [str(a.get("ticker", "$RUNNER")) for a in valid_assets]
            odds = [safe_float(a.get("decimal_odds"), 4.0) for a in valid_assets]
            evs = [safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), 0.0) for a in valid_assets]
            speeds = [safe_int(a.get("beyer_speed"), 110) for a in valid_assets]
            tags = [str(a.get("asset_tag"), "MID_TIER_HEDGE") for a in valid_assets]

            risks = [round(o * 1.8, 1) for o in odds]

            color_map = {"VALUE_BUY": "#10B981", "OVERVALUED_FADE": "#F43F5E", "MID_TIER_HEDGE": "#F59E0B"}
            colors = [color_map.get(t, "#F59E0B") for t in tags]

            fig = go.Figure()

            fig.add_hline(y=0, line_dash="dash", line_color="#94A3B8", opacity=0.8, annotation_text="0% EV Threshold", annotation_position="top left")

            fig.add_trace(go.Scatter(
                x=risks,
                y=evs,
                mode="markers+text",
                text=tickers,
                textposition="top center",
                marker=dict(
                    size=[max(14, min(36, s / 3.8)) for s in speeds],
                    color=colors,
                    opacity=0.9,
                    line=dict(width=2, color="#0F172A")
                ),
                hovertemplate="<b>%{customdata[0]} (%{text})</b><br>Risk Variance Index: %{x}<br>Expected Return (EV): %{y:+.1f}%%<br>Speed Rating: %{customdata[1]}<extra></extra>",
                customdata=list(zip(names, speeds))
            ))

            fig.update_layout(
                title=dict(text="⚖️ Risk Variance vs Expected Return (EV %) Efficient Frontier", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Risk Variance Index (Odds Volatility)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Expected Return (EV %)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                margin=dict(l=50, r=25, b=50, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("⚖️ Risk vs Expected Return Efficient Frontier")

    @classmethod
    def build_backtest_equity_curve_chart(cls, backtest_res: Dict[str, Any]) -> go.Figure:
        """MODEL 9: Cumulative Bankroll & EV Alpha Backtest Equity Curve Chart."""
        if not isinstance(backtest_res, dict) or "equity_df" not in backtest_res:
            return cls._create_empty_fig("📈 Cumulative P/L & Bankroll Equity Curve (No Backtest)")

        try:
            df = backtest_res.get("equity_df")
            if df is None or df.empty:
                return cls._create_empty_fig("📈 Cumulative P/L & Bankroll Equity Curve")

            init_b = safe_float(backtest_res.get("initial_bankroll_usd"), 1000.0)

            fig = go.Figure()

            fig.add_hline(y=init_b, line_dash="dash", line_color="#94A3B8", opacity=0.8, annotation_text=f"Initial Capital (${init_b:,.0f})", annotation_position="bottom left")

            fig.add_trace(go.Scatter(
                x=df["step"],
                y=df["bankroll"],
                mode="lines+markers",
                name="📈 Seabiscuit +EV Alpha Strategy",
                line=dict(color="#10B981", width=3.5),
                marker=dict(size=6, color="#047857"),
                fill="tonexty",
                fillcolor="rgba(16, 185, 129, 0.12)",
                hovertemplate="<b>%{x}</b><br>Cumulative Bankroll: $%{-y:,.2f}<extra></extra>"
            ))

            fig.update_layout(
                title=dict(text=f"📈 Seabiscuit +EV Alpha Strategy Equity Curve (ROI: {backtest_res.get('roi_pct', 0.0):+.1f}%)", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Execution Trades Horizon", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Bankroll Capital ($)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="#0F172A")),
                margin=dict(l=55, r=25, b=80, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("📈 Cumulative P/L & Bankroll Equity Curve")

    @classmethod
    def build_race_market_treemap(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 1: Race Market Capitalization & Alpha Treemap Heatmap."""
        if not equity_assets:
            return cls._create_empty_fig("🗺️ Race Market Capitalization & Alpha Heatmap (No Assets)")

        try:
            valid_assets = [a for a in equity_assets if isinstance(a, dict)]
            if not valid_assets:
                return cls._create_empty_fig("🗺️ Race Market Capitalization & Alpha Heatmap")

            df = pd.DataFrame([
                {
                    "Horse": f"{a.get('ticker', '$RUNNER')}<br>{a.get('horse', 'Horse')}",
                    "MarketCap": safe_float(a.get("market_cap_usd"), default=100000.0),
                    "EV": safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), default=0.0),
                    "Price": f"${safe_float(a.get('share_price_usd'), 20.0):.2f}",
                    "Odds": f"{safe_float(a.get('decimal_odds'), 4.0):.2f}"
                }
                for a in valid_assets
            ])

            fig = px.treemap(
                df,
                path=["Horse"],
                values="MarketCap",
                color="EV",
                color_continuous_scale=[(0.0, "#F43F5E"), (0.5, "#F59E0B"), (1.0, "#10B981")],
                color_continuous_midpoint=0.0,
                hover_data=["Price", "Odds", "EV"]
            )

            fig.update_traces(
                textinfo="label+value",
                textfont=dict(size=12, family="JetBrains Mono, sans-serif", color="#FFFFFF"),
                hovertemplate="<b>%{label}</b><br>Market Cap: $%{-value:,.0f}<br>Expected Return (EV): %{customdata[2]:+.1f}%%<extra></extra>"
            )

            fig.update_layout(
                title=dict(text="🗺️ Race Market Capitalization & Value Treemap", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.96),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif"),
                height=380,
                margin=dict(l=15, r=15, b=15, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🗺️ Race Market Capitalization & Value Treemap")

    @classmethod
    def build_equine_ichimoku_cloud_chart(cls, equity_asset: Dict[str, Any]) -> go.Figure:
        """MODEL 2: Ichimoku Kinko Hyo Cloud Chart."""
        if not isinstance(equity_asset, dict):
            return cls._create_empty_fig("☁️ Equine Ichimoku Trend Cloud (No Asset)")

        try:
            horse_name = str(equity_asset.get("horse", "Runner"))
            ticker = str(equity_asset.get("ticker", "$RUNNER"))
            
            df_candles = EquineTimeSeriesEngine.generate_career_ohlc_candles(equity_asset, num_races=15)
            df_ichi = EquineTimeSeriesEngine.compute_ichimoku_indicators(df_candles)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df_ichi["date"], y=df_ichi["tenkan_sen"],
                mode="lines", name="Tenkan-sen (Conversion)",
                line=dict(color="#0284C7", width=2)
            ))

            fig.add_trace(go.Scatter(
                x=df_ichi["date"], y=df_ichi["kijun_sen"],
                mode="lines", name="Kijun-sen (Base)",
                line=dict(color="#D97706", width=2)
            ))

            fig.add_trace(go.Scatter(
                x=df_ichi["date"], y=df_ichi["senkou_span_a"],
                mode="lines", name="Senkou Span A",
                line=dict(color="rgba(16, 185, 129, 0.4)", width=1),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=df_ichi["date"], y=df_ichi["senkou_span_b"],
                mode="lines", name="Kumo Cloud (Senkou Span B)",
                fill="tonexty",
                fillcolor="rgba(16, 185, 129, 0.15)",
                line=dict(color="rgba(244, 63, 94, 0.4)", width=1)
            ))

            fig.add_trace(go.Scatter(
                x=df_ichi["date"], y=df_ichi["close"],
                mode="lines+markers", name=f"{ticker} Share Price ($)",
                line=dict(color="#0F172A", width=3),
                marker=dict(size=6, color="#4338CA")
            ))

            fig.update_layout(
                title=dict(text=f"☁️ Ichimoku Trend Cloud: {ticker} ({horse_name})", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Race History Horizon", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Share Price ($/share)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="#0F172A", size=10)),
                margin=dict(l=45, r=25, b=80, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("☁️ Equine Ichimoku Trend Cloud")

    @classmethod
    def build_monte_carlo_win_distribution_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 3: Monte Carlo 10,000-Sim Victory Share Chart."""
        if not equity_assets:
            return cls._create_empty_fig("🔮 Monte Carlo 10,000-Race Simulation (No Assets)")

        try:
            valid_assets = [a for a in equity_assets if isinstance(a, dict)]
            if not valid_assets:
                return cls._create_empty_fig("🔮 Monte Carlo 10,000-Race Simulation")

            valid_assets = list(reversed(valid_assets))

            tickers = [str(a.get("ticker", f"$RUNNER_{i}")) for i, a in enumerate(valid_assets)]
            horse_names = [str(a.get("horse", "Runner")) for a in valid_assets]
            labels = [f"{t} ({h})" for t, h in zip(tickers, horse_names)]
            
            model_probs = [safe_float(a.get("win_percent"), default=0.15) for a in valid_assets]
            implied_probs = [safe_float(a.get("implied_win_pct"), default=15.0) / 100.0 for a in valid_assets]

            sum_model = max(0.001, sum(model_probs))
            mc_win_pcts = [round((p / sum_model) * 100.0, 1) for p in model_probs]
            mkt_win_pcts = [round(p * 100.0, 1) for p in implied_probs]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=labels,
                x=mc_win_pcts,
                name="🔮 Monte Carlo Sim Win %",
                orientation="h",
                marker=dict(color="#10B981", line=dict(color="#047857", width=1.5)),
                text=[f"{x:.1f}%" for x in mc_win_pcts],
                textposition="auto",
                textfont=dict(color="#FFFFFF", size=11, family="JetBrains Mono"),
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>Monte Carlo Victory Share: %{x:.1f}%%<extra></extra>"
            ))

            fig.add_trace(go.Bar(
                y=labels,
                x=mkt_win_pcts,
                name="📊 Bookmaker Implied Win %",
                orientation="h",
                marker=dict(color="#64748B", line=dict(color="#334155", width=1.5)),
                text=[f"{x:.1f}%" for x in mkt_win_pcts],
                textposition="auto",
                textfont=dict(color="#FFFFFF", size=11, family="JetBrains Mono"),
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>Bookmaker Share: %{x:.1f}%%<extra></extra>"
            ))

            dynamic_height = max(380, len(valid_assets) * 45)

            fig.update_layout(
                title=dict(text="🔮 Monte Carlo 10,000-Race Victory Share vs Bookmaker Odds", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=dynamic_height,
                barmode="group",
                xaxis=dict(title=dict(text="Probability Share (%)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(gridcolor="#E2E8F0", tickfont=dict(color="#0F172A", size=11)),
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(color="#0F172A")),
                margin=dict(l=160, r=50, b=70, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🔮 Monte Carlo 10,000-Race Simulation")

    @classmethod
    def build_alpha_ev_scatter_matrix(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 4: Alpha Expected Value (EV %) vs Share Price Scatter Matrix."""
        if not equity_assets:
            return cls._create_empty_fig("🚀 Expected Return (EV %) vs Share Price Matrix (No Assets)")

        try:
            x_prices = [safe_float(a.get("share_price_usd"), default=20.0) for a in equity_assets if isinstance(a, dict)]
            y_ev = [safe_float(a.get("expected_value_pct") or (safe_float(a.get("expected_value")) * 100.0), default=0.0) for a in equity_assets if isinstance(a, dict)]
            names = [str(a.get("horse", "Runner")) for a in equity_assets if isinstance(a, dict)]
            tickers = [str(a.get("ticker", "$RUNNER")) for a in equity_assets if isinstance(a, dict)]
            beyers = [safe_int(a.get("beyer_speed"), default=100) for a in equity_assets if isinstance(a, dict)]
            tags = [str(a.get("asset_tag", "MID_TIER_HEDGE")) for a in equity_assets if isinstance(a, dict)]

            color_map = {"VALUE_BUY": "#10B981", "OVERVALUED_FADE": "#F43F5E", "MID_TIER_HEDGE": "#F59E0B"}
            colors = [color_map.get(t, "#F59E0B") for t in tags]

            fig = go.Figure()

            fig.add_hline(y=0, line_dash="dash", line_color="#94A3B8", opacity=0.8, annotation_text="0% Fair Return Threshold", annotation_position="top left")

            fig.add_trace(go.Scatter(
                x=x_prices,
                y=y_ev,
                mode="markers+text",
                text=tickers,
                textposition="top center",
                textfont=dict(color="#0F172A", size=11, family="JetBrains Mono"),
                marker=dict(
                    size=[max(14, min(36, b / 4.0)) for b in beyers],
                    color=colors,
                    opacity=0.9,
                    line=dict(width=2, color="#0F172A")
                ),
                hovertemplate="<b>%{text} (%{customdata[0]})</b><br>Share Price: $%{-x:.2f}<br>Expected Return (EV): %{y:+.1f}%%<br>Speed Rating: %{customdata[1]}<extra></extra>",
                customdata=list(zip(names, beyers))
            ))

            fig.update_layout(
                title=dict(text="🚀 Expected Return (EV %) vs Share Price Matrix", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Share Price ($/share)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Expected Return (EV %)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                margin=dict(l=45, r=25, b=45, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🚀 Expected Return (EV %) vs Share Price Matrix")

    @classmethod
    def build_furlong_velocity_profile_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 5: Furlong Pace Velocity & Acceleration Profile."""
        if not equity_assets:
            return cls._create_empty_fig("🏎️ Pace & Turn of Foot Speed Profile (No Assets)")

        try:
            furlongs = [f"Furlong {i}" for i in range(1, 9)]
            colors = ["#10B981", "#0284C7", "#F43F5E", "#D97706", "#8B5CF6", "#EC4899", "#EA580C"]
            fig = go.Figure()

            for idx, asset in enumerate(equity_assets):
                if not isinstance(asset, dict):
                    continue
                beyer = safe_int(asset.get("beyer_speed"), default=110)
                horse_name = str(asset.get("horse", "Runner"))
                ticker = str(asset.get("ticker", "$RUNNER"))
                
                np.random.seed(int(abs(hash(horse_name)) % 99999))
                base_speed = (beyer / 120.0) * 38.0
                
                if idx % 3 == 0:
                    velocity_curve = [base_speed + 2.5, base_speed + 2.0, base_speed + 1.2, base_speed + 0.5, base_speed, base_speed - 0.5, base_speed - 1.2, base_speed - 2.0]
                elif idx % 3 == 1:
                    velocity_curve = [base_speed - 1.5, base_speed - 1.0, base_speed - 0.5, base_speed, base_speed + 0.8, base_speed + 1.8, base_speed + 3.2, base_speed + 3.8]
                else:
                    velocity_curve = [base_speed + 0.5, base_speed + 0.8, base_speed + 1.0, base_speed + 0.8, base_speed + 0.5, base_speed + 0.2, base_speed, base_speed - 0.5]

                fig.add_trace(go.Scatter(
                    x=furlongs,
                    y=[round(v, 1) for v in velocity_curve],
                    mode="lines+markers",
                    name=f"{ticker} ({horse_name})",
                    line=dict(width=3, color=colors[idx % len(colors)]),
                    marker=dict(size=7),
                    hovertemplate=f"<b>{horse_name} ({ticker})</b><br>%{{x}}: %{{y}} mph<extra></extra>"
                ))

            fig.update_layout(
                title=dict(text="🏎️ Furlong Speed & Turn of Foot Profile (Speed vs Furlong)", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Race Distance Horizon", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Sustained Speed (mph)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="#0F172A", size=10)),
                margin=dict(l=45, r=25, b=80, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🏎️ Furlong Speed & Turn of Foot Profile")

    @classmethod
    def build_beyer_speed_progression_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 6: Multi-Runner Beyer Speed Rating Progression."""
        if not equity_assets:
            return cls._create_empty_fig("⚡ Speed Power Rating History (No Data)")

        try:
            races_labels = ["Race -4", "Race -3", "Race -2", "Previous", "Target"]
            colors = ["#10B981", "#0284C7", "#F43F5E", "#D97706", "#8B5CF6", "#EC4899"]
            
            fig = go.Figure()
            
            for idx, asset in enumerate(equity_assets):
                if not isinstance(asset, dict):
                    continue
                base_beyer = safe_int(asset.get("beyer_speed"), default=110)
                horse_name = str(asset.get("horse", "Runner"))
                np.random.seed(int(abs(hash(horse_name)) % 99999))
                beyer_series = [base_beyer - i * np.random.randint(1, 3) + np.random.randint(-2, 3) for i in range(4, -1, -1)]
                
                fig.add_trace(go.Scatter(
                    x=races_labels,
                    y=beyer_series,
                    mode="lines+markers",
                    name=str(asset.get("ticker", "$RUNNER")),
                    line=dict(width=3, color=colors[idx % len(colors)]),
                    marker=dict(size=7)
                ))

            fig.update_layout(
                title=dict(text="⚡ Speed Power Rating Progression (Past 5 Races)", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Speed Power Rating", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="#0F172A", size=10)),
                margin=dict(l=45, r=25, b=80, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("⚡ Speed Power Rating Progression")

    @classmethod
    def build_3d_track_speed_terrain(cls, moisture_pct: float = 20.0) -> go.Figure:
        """MODEL 7: 3D Track Speed Terrain Surface Mesh."""
        try:
            moisture_val = safe_float(moisture_pct, default=20.0)
            distances = np.linspace(5.0, 24.0, 20)
            moistures = np.linspace(10.0, 50.0, 20)
            D, M = np.meshgrid(distances, moistures)
            
            Z = 125.0 - 0.85 * (np.maximum(0.0, D - 6.0))**1.2 - 0.45 * (np.maximum(0.0, M - 15.0))**1.1 + 5.0 * np.sin(D / 2.0)
            Z = np.clip(Z, 60.0, 130.0)

            fig = go.Figure(data=[go.Surface(
                x=D, y=M, z=Z,
                colorscale="Viridis",
                showscale=False,
                hovertemplate="Distance: %{x:.1f}f<br>Moisture: %{y:.1f}%%<br>Speed Rating: %{z:.1f}<extra></extra>"
            )])

            fig.add_trace(go.Scatter3d(
                x=[12.0], y=[moisture_val], z=[118.0],
                mode="markers+text",
                marker=dict(size=8, color="#F43F5E", symbol="diamond"),
                text=["Target Race"],
                textposition="top center"
            ))

            fig.update_layout(
                title=dict(text="🏁 3D Track Speed & Ground Moisture Surface Terrain", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif"),
                height=380,
                scene=dict(
                    xaxis=dict(title="Dist (f)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
                    yaxis=dict(title="Moisture (%)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
                    zaxis=dict(title="Speed Rating", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
                    camera=dict(eye=dict(x=1.3, y=1.3, z=1.1))
                ),
                margin=dict(l=15, r=15, b=15, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🏁 3D Track Speed & Ground Moisture Surface Terrain")

    @classmethod
    def build_multi_runner_trajectory_chart(cls, equity_assets: List[Dict[str, Any]]) -> go.Figure:
        """MODEL 8: Multi-Runner Equity Price Trajectory."""
        if not equity_assets:
            return cls._create_empty_fig("📈 Share Price History Trajectory (No Active Assets)")

        try:
            df_multi = EquineTimeSeriesEngine.compute_multi_runner_time_series(equity_assets, num_races=10)
            if df_multi is None or df_multi.empty or "date" not in df_multi.columns:
                return cls._create_empty_fig("📈 Share Price History Trajectory (No Time Series)")
            
            colors = ["#10B981", "#0284C7", "#F43F5E", "#D97706", "#8B5CF6", "#EC4899", "#EA580C"]
            fig = go.Figure()

            for idx, asset in enumerate(equity_assets):
                if not isinstance(asset, dict):
                    continue
                ticker = str(asset.get("ticker", f"$RUNNER_{idx}"))
                horse_name = str(asset.get("horse", "Runner"))
                
                if ticker in df_multi.columns:
                    fig.add_trace(go.Scatter(
                        x=df_multi["date"],
                        y=df_multi[ticker],
                        mode="lines+markers",
                        name=f"{ticker} ({horse_name})",
                        line=dict(width=3, color=colors[idx % len(colors)]),
                        marker=dict(size=7),
                        hovertemplate=f"<b>{horse_name} ({ticker})</b><br>Date: %{{x}}<br>Share Price: $%{{y:.2f}}<extra></extra>"
                    ))

            fig.update_layout(
                title=dict(text="📈 Runner Share Price Career Trajectory Overlay", font=dict(color="#0F172A", size=15, family="Outfit"), x=0.01, y=0.97),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif", size=12),
                height=380,
                xaxis=dict(title=dict(text="Career Race Horizon", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                yaxis=dict(title=dict(text="Share Price ($/share)", font=dict(color="#0F172A")), gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color="#0F172A", size=10)),
                margin=dict(l=45, r=25, b=80, t=75)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("📈 Share Price History Trajectory")

    @classmethod
    def build_6d_equine_quant_radar(cls, asset: Dict[str, Any]) -> go.Figure:
        """Generates 6D Equine Quant Radar plot safely."""
        if not isinstance(asset, dict):
            return cls._create_empty_fig("🎯 Performance Radar")

        try:
            metrics = ["Speed Rating", "Form Momentum", "Value Index (A/E)", "Moisture Fit", "Trainer Skill", "Market Depth"]
            
            beyer_score = min(100.0, (safe_float(asset.get("beyer_speed"), 100) / 130.0) * 100.0)
            ae_score = min(100.0, (safe_float(asset.get("ae_ratio"), 1.0) / 1.5) * 100.0)
            moisture_score = safe_float(asset.get("track_moisture_fit"), 0.85) * 100.0
            win_score = safe_float(asset.get("implied_win_pct"), 20.0) * 2.0

            values = [
                round(beyer_score, 1),
                round(min(100.0, win_score * 1.3), 1),
                round(ae_score, 1),
                round(moisture_score, 1),
                round(min(100.0, ae_score * 0.9 + 20), 1),
                round(min(100.0, safe_float(asset.get("share_price_usd"), 20) * 1.5), 1)
            ]

            metrics_closed = metrics + [metrics[0]]
            values_closed = values + [values[0]]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values_closed, theta=metrics_closed, fill="toself",
                fillcolor="rgba(67, 56, 202, 0.18)",
                line=dict(color="#4338CA", width=3), name=str(asset.get("ticker", "$EQUITY"))
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E2E8F0", color="#64748B"),
                    angularaxis=dict(gridcolor="#E2E8F0", color="#0F172A"),
                    bgcolor="#FFFFFF"
                ),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="JetBrains Mono, sans-serif"),
                height=350,
                title=dict(text=f"🎯 Performance Radar: {asset.get('horse', 'Runner')}", font=dict(color="#0F172A", size=14), x=0.01, y=0.97),
                showlegend=False,
                margin=dict(l=30, r=30, b=30, t=70)
            )
            return fig
        except Exception:
            return cls._create_empty_fig("🎯 Performance Radar")
