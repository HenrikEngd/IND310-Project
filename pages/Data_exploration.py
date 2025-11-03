import streamlit as st
import pandas as pd
from data_cache import load_market_data, DEFAULT_TICKERS

st.title("Data Exploration Page")

# Load cached data shared across pages
data, adj_close_df, returns_df, betas = load_market_data(tickers=DEFAULT_TICKERS)

st.caption(
	f"Available tickers: {', '.join(adj_close_df.columns)} | Rows: {len(adj_close_df):,}"
)

st.subheader("Close Prices (preview)")
st.dataframe(adj_close_df.tail(), use_container_width=True)

st.subheader("Daily Returns (preview)")
st.dataframe(returns_df.tail(), use_container_width=True)
