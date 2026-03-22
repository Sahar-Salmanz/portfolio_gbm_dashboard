from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(tickers: list[str], years: int=3) -> pd.DataFrame:
    """
    Download closing prices for chosen tickers over the indicated past years.

    :param tickers: a list of chosen tickers
    :param years: to calculate the start date
    :return: Date-indexed DataFrame with one column per ticker
    """
    end = datetime.today()
    start = end - timedelta(days=365 * years)

    raw = yf.download(tickers, start, end, auto_adjust=True, progress=False, threads=True)

    # yfinance returns a MultiIndex when multiple tickers are requested
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]

    else:
        # Single ticker — raw columns are OHLCV
        if "Close" in raw.columns:
            prices = raw[["Close"]]
            prices.columns = tickers

        else:
            prices = raw

    if prices.empty:
        raise ValueError("No price data returned. check your tickers and data range.")
    
    prices = prices.dropna(how="all") # rows with all NAN values are droped
    prices = prices.ffill().bfill() # fill minor gaps, individual NaNs are forward-filled.

    # Ensure column order matches the requested tickers
    available = [t for t in tickers if t in prices.column]
    return prices[available]


def get_available_tickers(tickers, prices):
    """
    Split tickers into those present in prices and those missing.
    """
    available = [t for t in tickers if t in prices.columns]
    missing = [t for t in tickers if t not in prices.columns]
    return available, missing