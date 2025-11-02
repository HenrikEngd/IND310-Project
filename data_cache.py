import streamlit as st
import yfinance as yf
from typing import List
import pandas as pd
import formulas

# Defaults used across pages
DEFAULT_TICKERS = ["EQNR.OL", "DNB.OL", "AKRBP.OL", "ORK.OL", "MOWI.OL"]
DEFAULT_START = "2020-10-15"
DEFAULT_END = "2025-10-15"

@st.cache_data(show_spinner="Downloading market data...", ttl=60 * 60 * 6)
def load_market_data(
    tickers: List[str] = DEFAULT_TICKERS,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END):
    """Download and cache market data including dividends and stock splits."""
    data = {}
    for ticker in tickers:
        ticker_data = yf.Ticker(ticker).history(start=start, end=end, actions=True, auto_adjust=False)
        if not ticker_data.empty:
            ticker_data.index = ticker_data.index.tz_localize(None)
            data[ticker] = ticker_data
    
    if not data:
        raise ValueError("No ticker data could be downloaded")
    
    # Download market index
    market_data = yf.Ticker("OSEBX.OL").history(start=start, end=end)
    market_returns = None
    if not market_data.empty:
        market_data.index = market_data.index.tz_localize(None)
        market_returns = market_data['Close'].pct_change().dropna()
    
    data = pd.concat(data, axis=1)
    close_data = data.xs('Close', level=1, axis=1)
    dividends_data = data.xs('Dividends', level=1, axis=1)
    splits_data = data.xs('Stock Splits', level=1, axis=1)
    
    adj_close_data = formulas.adjusted_close_price(close_data, dividends_data, splits_data)
    returns = formulas.returns(adj_close_data)
    
    betas = {}
    for ticker in tickers:
        if ticker in returns.columns and market_returns is not None:
            betas[ticker] = formulas.beta(returns[ticker], market_returns)
        else:
            betas[ticker] = 0.0
    
    return data, adj_close_data, returns, betas


