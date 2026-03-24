from dataclasses import dataclass

import streamlit as st

from utils.config import (
    ASSET_OPTIONS,
    MAX_ASSETS,
    DEFAULT_HIST_YEARS,
    DEFAULT_HORIZON_KEY,
    DEFAULT_SIMULATIONS,
    HORIZON_OPTIONS,
    SIMULATION_OPTIONS,
)
from data.validator import validate_shares


@dataclass
class SidebarState:
    hist_years: int
    horizon_days: int
    horizon_label: str
    n_sims: int
    run_clicked: bool


def render_sidebar() -> SidebarState:
    with st.sidebar:
        st.title("Portfolio Risk Engine")
        st.divider()

        # render asset picker
        st.subheader("Add asset")
        selected_label = st.selectbox(
            "Asset", 
            options=list(ASSET_OPTIONS.keys()), 
            key="asset_select"
        )
        selected_ticker = ASSET_OPTIONS[selected_label]

        n_shares = st.number_input(
            "Number of shares", 
            min_value=1, 
            max_value=1_000_000,
            value=10, 
            step=1,
            key="shares_input",
        )

        if st.button("Add to portfolio", use_container_width=True):
            # Validate and append an asset to st.session_state.portfolio.
            existing_tickers = [e["ticker"] for e in st.session_state.portfolio]

            if selected_ticker in existing_tickers:
                st.warning(f"{selected_ticker} is already in your portfolio. Remove it first to update shares.")
                return

            if len(st.session_state.portfolio) >= MAX_ASSETS:
                st.error(f"Maximum {MAX_ASSETS} assets allowed.")
                return

            if not validate_shares(n_shares)[0]:
                st.error(validate_shares(n_shares)[1])
                return

            st.session_state.portfolio.append({
                "label":  selected_label.strip(),
                "ticker": selected_ticker,
                "shares": n_shares,                
            })

        # Display current portfolio entries with per-row delete buttons.
        if not st.session_state.portfolio:
            return
    
        st.subheader("Current portfolio")
    
        for i, entry in enumerate(st.session_state.portfolio):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{entry['ticker']}** — {entry['shares']} shares")
            if col2.button("✕", key=f"del_{i}", help=f"Remove {entry['ticker']}"):
                st.session_state.portfolio.pop(i)
                st.rerun()
    
        if st.button("Clear all", use_container_width=True):
            st.session_state.portfolio = []
            st.rerun()


        st.divider()
        # Historical data period slider, returns selected years
        st.subheader("Historical data")
        hist_years = st.slider("Years of history", 1, 10, DEFAULT_HIST_YEARS, key="hist_years")

        # Monte Carlo horizon + simulation count controls. Returns (label, days, n_sims).
        st.subheader("Monte Carlo settings")
        horizon_label = st.selectbox(
            "Forecast horizon", 
            options=list(HORIZON_OPTIONS.keys()), 
            index=list(HORIZON_OPTIONS.keys()).index(DEFAULT_HORIZON_KEY), 
            key="horizon_select"
        )
        horizon_days = HORIZON_OPTIONS[horizon_label]
        n_sims = st.select_slider(
            "Simulations",
            options=SIMULATION_OPTIONS,
            value=DEFAULT_SIMULATIONS,
            key="n_sims",
        )

        # run_clicked = run button
        run_clicked   = st.button("Run simulation", use_container_width=True, type="primary")

    return SidebarState(
        hist_years = hist_years, 
        horizon_days = horizon_days, 
        horizon_label = horizon_label, 
        n_sims = n_sims,
        run_clicked = run_clicked
    )