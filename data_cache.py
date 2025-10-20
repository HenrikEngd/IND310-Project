import streamlit as st
import yfinance as yf
import pandas as pd

# Defaults used across pages
DEFAULT_TICKERS = ["EQNR.OL", "DNB.OL", "AKRBP.OL", "ORK.OL", "MOWI.OL"]
DEFAULT_START = "2020-10-15"
DEFAULT_END = "2025-10-15"


@st.cache_data(show_spinner="Downloading market data...", ttl=60 * 60 * 6)
def load_market_data(
    tickers: list[str] = DEFAULT_TICKERS,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
):
    """
    Download and cache market data for the given tickers and date range.

    Returns a tuple of (raw, close_df, returns_df):
    - raw: original yfinance DataFrame (multi-index columns)
    - close_df: DataFrame of Close prices with columns equal to tickers
    - returns_df: Daily percentage returns based on close_df
    """
    data = yf.download(tickers, start=start, end=end, progress=False)

    # Prepare close prices and returns
    close_df = data["Close"].copy()
    # Ensure columns are plain tickers
    close_df.columns = tickers
    returns_df = close_df.pct_change().dropna()

    return data, close_df, returns_df
