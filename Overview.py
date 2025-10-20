import streamlit as st
import pandas as pd
import altair as alt
from data_cache import load_market_data, DEFAULT_TICKERS

tickers = DEFAULT_TICKERS
data, all_close_data, returns = load_market_data(tickers=tickers)

st.title("IND310 Project")
st.write(
    "This application allows you to view historical stock prices for selected companies."
)

# Define consistent colors for each ticker
color_map = {
    "EQNR.OL": "#2f4d8e",
    "DNB.OL": "#ffa659",
    "AKRBP.OL": "#ff6464",
    "ORK.OL": "#79ffbc",
    "MOWI.OL": "#c180ff",
}

# Determine which tickers are actually available in the data
available_tickers = [t for t in tickers if t in all_close_data.columns]
if not available_tickers:
    st.error("No ticker data available. Try refreshing or adjusting the date range.")
    st.stop()

# Multi-select for tickers (limit to available ones)
selected_tickers = st.multiselect(
    "Select ticker symbols to display:",
    available_tickers,
    default=available_tickers,  # All available selected by default
)


if selected_tickers:
    st.subheader("Historical Stock Prices")
    # Filter data to show only selected tickers
    # Always use list indexing to ensure DataFrame is returned
    filtered_data = (
        all_close_data[selected_tickers]
        if len(selected_tickers) > 1
        else all_close_data[[selected_tickers[0]]]
    )

    # Handle color parameter based on number of selected tickers
    if len(selected_tickers) == 1:
        st.line_chart(filtered_data, color=color_map[selected_tickers[0]])
    else:
        st.line_chart(
            filtered_data, color=[color_map[ticker] for ticker in selected_tickers]
        )

    # Calculate and display risk metrics
    st.subheader("Risk Analysis (Standard Deviation)")
    st.write(
        "Standard deviation of daily returns measures volatility/risk. Higher values indicate more risk."
    )

    # Calculate standard deviation for selected tickers
    risk_data = []
    for ticker in selected_tickers:
        daily_std = returns[ticker].std()
        annual_std = daily_std * (
            252**0.5
        )  # Annualized standard deviation (252 trading days)
        risk_data.append(
            {
                "Ticker": ticker,
                "Daily Std Dev (%)": f"{daily_std * 100:.4f}",
                "Annual Std Dev (%)": f"{annual_std * 100:.2f}",
            }
        )

    risk_df = pd.DataFrame(risk_data)
    st.dataframe(risk_df, hide_index=True)

    # Visualize risk comparison
    st.subheader("Annualized Standard Deviation Comparison")
    # Build a tidy DataFrame for Altair
    annual_std_df = pd.DataFrame(
        [
            {
                "Ticker": ticker,
                "Annual Std Dev (%)": returns[ticker].std() * (252**0.5) * 100,
            }
            for ticker in selected_tickers
        ]
    )

    # Create bar chart with a labeled y-axis
    chart = (
        alt.Chart(annual_std_df)
        .mark_bar()
        .encode(
            x=alt.X("Ticker:N", sort=selected_tickers, title=None),
            y=alt.Y("Annual Std Dev (%):Q", title="Annual standard deviation (%)"),
            color=alt.Color(
                "Ticker:N",
                scale=alt.Scale(
                    domain=selected_tickers,
                    range=[color_map[t] for t in selected_tickers],
                ),
                legend=None,
            ),
        )
        .properties(height=300)
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.warning("Please select at least one ticker to display.")

st.write("Data source: Yahoo Finance")
