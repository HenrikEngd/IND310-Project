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
    # Use robust options; if 'repair' isn't supported in older yfinance, it will be ignored
    data = yf.download(
        tickers,
        start=start,
        end=end,
        progress=False,
        group_by="ticker",
        auto_adjust=True,
        actions=False,
        threads=True,
    )

    # Prepare close prices and returns
    # yfinance may return columns grouped by ticker (level 0=ticker, level 1=field)
    # or grouped by field (level 0=field, level 1=ticker). Handle both.
    close_df: pd.DataFrame
    if isinstance(data.columns, pd.MultiIndex):
        lvl0 = data.columns.get_level_values(0)
        lvl1 = data.columns.get_level_values(1)
        if "Close" in lvl0:
            close_df = data["Close"].copy()
        elif "Close" in lvl1:
            close_df = data.xs("Close", axis=1, level=1).copy()
        elif "Adj Close" in lvl0:
            close_df = data["Adj Close"].copy()
        elif "Adj Close" in lvl1:
            close_df = data.xs("Adj Close", axis=1, level=1).copy()
        else:
            raise RuntimeError(
                "Downloaded data missing Close/Adj Close columns; unexpected format from Yahoo Finance."
            )
    else:
        # Single-ticker or unexpected shape; try to extract Close directly
        if "Close" in data.columns:
            close_df = data[["Close"]].copy()
            # Name the column with the ticker if only one ticker requested
            if len(tickers) == 1:
                close_df.columns = [tickers[0]]
        elif "Adj Close" in data.columns:
            close_df = data[["Adj Close"]].copy()
            if len(tickers) == 1:
                close_df.columns = [tickers[0]]
        else:
            raise RuntimeError(
                "Downloaded data missing Close/Adj Close columns; unexpected format from Yahoo Finance."
            )
    # Some rows (e.g., weekends) can be all NaN when merging multiple tickers
    close_df = close_df.dropna(how="all")
    # Reorder to requested ticker order where available; keep only available cols
    available_cols = [t for t in tickers if t in close_df.columns]
    if available_cols:
        close_df = close_df[available_cols]
    # Compute returns and drop all-NaN rows caused by leading NaNs per-column
    returns_df = close_df.pct_change().dropna(how="all")

    return data, close_df, returns_df
