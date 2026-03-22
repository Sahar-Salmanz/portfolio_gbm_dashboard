import streamlit as st
 
# ── Page config must come first ──
st.set_page_config(
    page_title="Portfolio Risk Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
from data.fetcher import fetch_prices, get_available_tickers
from data.validator import validate_portfolio
#from models.gbm import run_gbm_simulation
#from ui.portfolio import render_portfolio_section
from ui.sidebar import render_sidebar
#from ui.simulation import render_simulation_section
from ui.styles import inject_css


# ── Global CSS ──
inject_css()
 
# ── Session state initialisation ──
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
 
if "mc_result" not in st.session_state:
    st.session_state.mc_result      = None
    st.session_state.mc_horizon_lbl = None
 
# ── Sidebar ──
sidebar = render_sidebar()
 
# ── Page header ──
st.title("Portfolio Risk Engine")
st.caption("Multivariate GBM · Monte Carlo simulation · Correlated assets")