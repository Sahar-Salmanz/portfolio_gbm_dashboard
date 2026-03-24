import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.config import ASSET_COLORS, PALETTE, PLOT_LAYOUT
from data.formatting import fmt_dollars, fmt_pct
from model.metrics import HistoricalMetrics, compute_historical_metrics


def render_portfolio(prices, shares, tickers):
    st.subheader("Portfolio")

    latest_prices = prices.iloc[-1]
    rows = []
    total_value = 0.0
    for t in tickers:
        price = float(latest_prices[t])
        val = price * shares[t]
        total_value += val
        rows.append({
            "Ticker": t,
            "Shares": shares[t],
            "Price": fmt_dollars(price, decimals=2),
            "Value": fmt_dollars(val, decimals=2),
            "_raw_val": val # for weight calculation, not displayed
        })
    for row in rows:
        row["Weight"] = f"{row['_raw_val'] / total_value * 100:.1f}%"
        del row["_raw_val"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Assets", len(tickers))
    col2.metric("Total value", fmt_dollars(total_value, decimals=2))
    col3.metric("Data range", f"{prices.index[0].strftime('%b %Y')} - {prices.index[-1].strftime('%b %Y')}")

    st.dataframe(
        pd.DataFrame(rows).set_index("Ticker"),
        use_container_width=True,
    )

    st.subheader("Historical portfolio value")
    st.plotly_chart(
        _fig_historical(prices, shares, tickers),
        use_container_width=True
    )

    hist_metrics = compute_historical_metrics(prices, shares, tickers)
    _render_hist_metrics(hist_metrics)




# Private function to plot historical value
def _fig_historical(prices, shares, tickers):
    px_ = prices[tickers].dropna()
    share_arr = np.array([shares[t] for t in tickers])
    port_val = (px_ * share_arr).sum(axis=1)

    fig = make_subplots(
        rows=2, 
        cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.35], 
        vertical_spacing=0.06,
        subplot_titles=["Portfolio value", "Asset contributions (%)"],
    )

    # Total value
    fig.add_trace(
        go.Scatter(
            x=port_val.index, 
            y=port_val.values,
            mode="lines", name="Total",
            line=dict(color=PALETTE["dark"], width=2.5),
            fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.06)",
        ),
        row=1,
        col=1,
    )

    pct_df = (
        (px_ * share_arr) / (px_ * share_arr).sum(axis=1).values[:, None] * 100
    )

    for i, t in enumerate(tickers):
        fig.add_trace(
            go.Scatter(
                x=pct_df.index, 
                y=pct_df[t],
                name=t,
                mode="lines",
                line=dict(width=0),
                stackgroup="one",
                fillcolor=ASSET_COLORS[i % len(ASSET_COLORS)],
                hovertemplate=f"{t}: %{{y:.1f}}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

    fig.update_layout(**PLOT_LAYOUT, height=500, showlegend=True, title=None)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", row=1)
    fig.update_yaxes(ticksuffix="%", row=2)

    return fig

def _render_hist_metrics(m: HistoricalMetrics) -> None:
    """Display four historical metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ann. return (hist.)", fmt_pct(m.ann_return))
    col2.metric("Ann. volatility",     fmt_pct(m.ann_vol))
    col3.metric("Sharpe ratio",        f"{m.sharpe:.2f}")
    col4.metric("Max drawdown",        f"{m.max_drawdown * 100:.1f}%")
