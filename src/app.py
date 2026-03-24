import streamlit as st
 
# Page config must come first
st.set_page_config(
    page_title="Portfolio Risk Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
from data.fetcher import fetch_prices, get_available_tickers
from data.validator import validate_portfolio
from model.gbm import gbm_simulation
from ui.portfolio import render_portfolio
from ui.sidebar import render_sidebar
from model.simulation import render_simulation_section
from ui.styles import inject_css


# Global CSS
inject_css()
 
# Session state initialisation
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
 
if "mc_result" not in st.session_state:
    st.session_state.mc_result      = None
    st.session_state.mc_horizon_lbl = None
 
# Sidebar
sidebar = render_sidebar()
 
# Page header
st.title("Portfolio Risk Engine")
st.caption("Multivariate GBM · Monte Carlo simulation · Correlated assets")

# Validate portfolio
valid, err_msg = validate_portfolio(st.session_state.portfolio)
if not valid:
    st.info("👈  Use the sidebar to build your portfolio, then click **▶ Run simulation**.")
    if err_msg:
        st.warning(err_msg)
    st.stop()
 

tickers = [e["ticker"] for e in st.session_state.portfolio]
shares  = {e["ticker"]: e["shares"] for e in st.session_state.portfolio}

# Fetch prices
with st.spinner("Fetching market data…"):
    try:
        prices = fetch_prices(tickers, years=sidebar.hist_years)
    except Exception as exc:
        st.error(f"Failed to fetch market data: {exc}")
        st.stop()
 
# Handle tickers that returned no data
available, missing = get_available_tickers(tickers, prices)
if missing:
    st.warning(f"No data for: {', '.join(missing)}. Excluding from analysis.")
    tickers = available
    shares  = {t: shares[t] for t in available}
 
if not tickers:
    st.error("None of your selected tickers returned data. Please try different assets.")
    st.stop()
 
prices = prices[tickers].dropna()

# Portfolio & history section
render_portfolio(prices, shares, tickers)

if sidebar.run_clicked:
    with st.spinner(f"Running {sidebar.n_sims:,} GBM paths…"):
        result = gbm_simulation(
            prices       = prices,
            shares       = shares,
            horizon_days = sidebar.horizon_days,
            n_sims       = sidebar.n_sims,
        )
    st.session_state.mc_result      = result
    st.session_state.mc_horizon_lbl = sidebar.horizon_label
 
if st.session_state.mc_result is not None:
    render_simulation_section(
        result        = st.session_state.mc_result,
        prices        = prices,
        shares        = shares,
        horizon_label = st.session_state.mc_horizon_lbl,
    )
else:
    st.info("Configure settings in the sidebar and click **▶ Run simulation** to start.")