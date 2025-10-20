import streamlit as st
from typing import List, Tuple
import pandas as pd
try:
    import yfinance as yf
except Exception as e:
    # Raise a clear error so Streamlit shows an actionable message
    raise RuntimeError(
        "Missing dependency 'yfinance'. Make sure it's installed (requirements.txt) or run: pip install yfinance"
    ) from e

# Defaults used across pages
DEFAULT_TICKERS = ["EQNR.OL", "DNB.OL", "AKRBP.OL", "ORK.OL", "MOWI.OL"]
DEFAULT_START = "2020-10-15"
DEFAULT_END = "2025-10-15"


@st.cache_data(show_spinner="Downloading market data...", ttl=60 * 60 * 6)
def load_market_data(
    tickers: List[str] = DEFAULT_TICKERS,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
