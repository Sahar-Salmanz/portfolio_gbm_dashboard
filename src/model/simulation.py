
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 
from utils.config import PALETTE, PLOT_LAYOUT
from model.gbm import SimulationResult
from model.metrics import build_decision_table, compute_multi_horizon_summary
from data.formatting import fmt_delta_pct, fmt_dollars, risk_badge_html
 
 
def render_simulation_section(
    result: SimulationResult,
    prices: pd.DataFrame,
    shares: dict[str, int | float],
    horizon_label: str,
) -> None:
    st.divider()
    st.subheader("Monte Carlo simulation")
    st.caption(
        f"Multivariate GBM · Cholesky decomposition · "
        f"{result.n_sims:,} simulations · {horizon_label} horizon"
    )
 
    _render_key_metrics(result)
    _render_fan_chart(result)
    _render_distribution_row(result)
    _render_correlation(result)
    _render_decision_table(result)
    _render_multi_horizon(prices, shares, result.horizon_days)
 
 
#  Metrics 
def _render_key_metrics(result: SimulationResult) -> None:
    st.write("**Key risk metrics**")
 
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric(
        "P50 final value",
        fmt_dollars(result.p50),
        delta=fmt_delta_pct(result.p50, result.initial_value),
    )
    m2.metric(
        "P5 (downside)",
        fmt_dollars(result.p5),
        delta=fmt_delta_pct(result.p5, result.initial_value),
    )
    m3.metric(
        "P95 (upside)",
        fmt_dollars(result.p95),
        delta=fmt_delta_pct(result.p95, result.initial_value),
    )
    m4.metric("95% VaR (loss)",  fmt_dollars(result.var_95))
    m5.metric("95% CVaR",        fmt_dollars(result.cvar_95))
    m6.metric("Prob. of loss",   f"{result.prob_loss * 100:.1f}%")
 
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("CAGR @ median",  f"{result.cagr_p50 * 100:.1f}%")
    col_b.metric("Sharpe (sim.)",  f"{result.sharpe:.2f}")
    col_c.metric("Prob. of 2×",    f"{result.prob_2x * 100:.1f}%")
    col_d.markdown(
        f"**Risk level**&nbsp;&nbsp;{risk_badge_html(result.prob_loss)}",
        unsafe_allow_html=True,
    )
 
 
def _render_fan_chart(result: SimulationResult) -> None:
    st.write("**Simulation paths & percentile bands**")
    st.plotly_chart(_fig_mc_fan(result), use_container_width=True)
 
 
def _render_distribution_row(result: SimulationResult) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Final value distribution**")
        st.plotly_chart(_fig_final_distribution(result), use_container_width=True)
    with c2:
        st.write("**Max drawdown distribution**")
        st.plotly_chart(_fig_drawdown_dist(result), use_container_width=True)
 
 
def _render_correlation(result: SimulationResult) -> None:
    st.write("**Asset return correlations**")
    if len(result.tickers) > 1:
        st.plotly_chart(_fig_correlation(result.corr_matrix), use_container_width=True)
    else:
        st.info("Correlation matrix requires 2 or more assets.")
 
 
def _render_decision_table(result: SimulationResult) -> None:
    st.write("**Scenario decision guide**")
    st.dataframe(build_decision_table(result), use_container_width=True, hide_index=True)
 
 
def _render_multi_horizon(
    prices: pd.DataFrame,
    shares: dict[str, int | float],
    horizon_days: int,
) -> None:
    st.write("**Multi-horizon summary**")
    df = compute_multi_horizon_summary(prices, shares, horizon_days)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
 
 
#  Private figure builders 
def _fig_mc_fan(result: SimulationResult) -> go.Figure:
    """Monte Carlo fan chart with percentile bands and sample paths."""
    paths  = result.paths
    n_sims, T1 = paths.shape
    t_axis = np.arange(T1)
 
    # Sample a subset of paths to keep rendering fast
    rng        = np.random.default_rng(0)
    sample_idx = rng.choice(n_sims, size=min(150, n_sims), replace=False)
 
    fig = go.Figure()
 
    # Background sample paths (thin, semi-transparent)
    for i in sample_idx:
        fig.add_trace(go.Scatter(
            x=t_axis, y=paths[i],
            mode="lines",
            line=dict(color="rgba(100,100,120,0.06)", width=1),
            showlegend=False, hoverinfo="skip",
        ))
 
    # Percentile bands
    p5  = np.percentile(paths, 5,  axis=0)
    p25 = np.percentile(paths, 25, axis=0)
    p50 = np.percentile(paths, 50, axis=0)
    p75 = np.percentile(paths, 75, axis=0)
    p95 = np.percentile(paths, 95, axis=0)
 
    # P5–P95 outer band
    fig.add_trace(go.Scatter(
        x=np.concatenate([t_axis, t_axis[::-1]]),
        y=np.concatenate([p95, p5[::-1]]),
        fill="toself", fillcolor="rgba(37,99,235,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    # P25–P75 inner band
    fig.add_trace(go.Scatter(
        x=np.concatenate([t_axis, t_axis[::-1]]),
        y=np.concatenate([p75, p25[::-1]]),
        fill="toself", fillcolor="rgba(37,99,235,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
 
    # Percentile lines
    for pct, vals, color, dash, label in [
        (5,  p5,  PALETTE["red"],   "dash",  "P5"),
        (25, p25, PALETTE["amber"], "dot",   "P25"),
        (50, p50, PALETTE["dark"],  "solid", "P50 (median)"),
        (75, p75, PALETTE["green"], "dot",   "P75"),
        (95, p95, PALETTE["accent"],"dash",  "P95"),
    ]:
        fig.add_trace(go.Scatter(
            x=t_axis, y=vals,
            mode="lines", name=label,
            line=dict(color=color, width=1.8, dash=dash),
            hovertemplate=f"{label}: $%{{y:,.0f}}<extra></extra>",
        ))
 
    # Initial value reference line
    fig.add_hline(
        y=result.initial_value,
        line_dash="dot", line_color=PALETTE["mid"], line_width=1,
        annotation_text="Initial value",
        annotation_position="right",
        annotation_font_size=10,
    )
 
    fig.update_layout(
        PLOT_LAYOUT,
        height=420,
        xaxis_title=f"Trading days (horizon = {result.horizon_days} days)",
        yaxis_title="Portfolio value ($)",
        yaxis_tickprefix="$", yaxis_tickformat=",.0f",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
 
 
def _fig_final_distribution(result: SimulationResult) -> go.Figure:
    """Histogram of final portfolio values with percentile + initial-value overlays."""
    fv  = result.final_values
    fig = go.Figure()
 
    fig.add_trace(go.Histogram(
        x=fv, nbinsx=60,
        marker_color=PALETTE["accent"],
        marker_line_width=0,
        opacity=0.75,
        name="Simulated outcomes",
        hovertemplate="Value: $%{x:,.0f}<br>Count: %{y}<extra></extra>",
    ))
 
    for val, color, label in [
        (result.p5,  PALETTE["red"],   "P5"),
        (result.p50, PALETTE["dark"],  "P50"),
        (result.p95, PALETTE["green"], "P95"),
    ]:
        fig.add_vline(
            x=val, line_color=color, line_width=1.8, line_dash="dash",
            annotation_text=f"  {label}: ${val:,.0f}",
            annotation_font_size=10, annotation_font_color=color,
            annotation_position="top right",
        )
 
    fig.add_vline(
        x=result.initial_value,
        line_color=PALETTE["mid"], line_width=1.2, line_dash="dot",
        annotation_text="  Initial",
        annotation_font_size=10,
        annotation_position="top right",
    )
 
    fig.update_layout(
        PLOT_LAYOUT,
        height=350,
        xaxis_title="Final portfolio value ($)",
        yaxis_title="Number of simulations",
        xaxis_tickprefix="$", xaxis_tickformat=",.0f",
        showlegend=False,
        bargap=0.02,
    )
    return fig
 
 
def _fig_drawdown_dist(result: SimulationResult) -> go.Figure:
    """Histogram of maximum drawdown values across simulated paths."""
    mdd_pct = result.max_dds * 100
 
    fig = go.Figure(go.Histogram(
        x=mdd_pct, nbinsx=40,
        marker_color=PALETTE["red"],
        marker_line_width=0,
        opacity=0.75,
    ))
 
    p50_dd = float(np.median(mdd_pct))
    p95_dd = float(np.percentile(mdd_pct, 95))
 
    fig.add_vline(
        x=p50_dd, line_color=PALETTE["dark"], line_dash="dash", line_width=1.5,
        annotation_text=f"  Median: {p50_dd:.1f}%", annotation_font_size=10,
    )
    fig.add_vline(
        x=p95_dd, line_color=PALETTE["red"], line_dash="dash", line_width=1.5,
        annotation_text=f"  P95: {p95_dd:.1f}%", annotation_font_size=10,
    )
 
    fig.update_layout(
        PLOT_LAYOUT,
        height=300,
        xaxis_title="Max drawdown (%)",
        yaxis_title="Frequency",
        showlegend=False,
        bargap=0.02,
    )
    return fig
 
 
def _fig_correlation(corr: pd.DataFrame) -> go.Figure:
    """Correlation heatmap of daily log-returns."""
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[
            [0.0, "#dc2626"],
            [0.5, "#f9fafb"],
            [1.0, "#2563eb"],
        ],
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont_size=11,
        hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        PLOT_LAYOUT,
        height=320,
        margin=dict(l=60, r=30, t=30, b=60),
        xaxis=dict(side="bottom"),
    )
    return fig