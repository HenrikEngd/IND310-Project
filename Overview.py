import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

tickers = ["EQNR.OL", "DNB.OL", "AKRBP.OL", "ORK.OL", "MOWI.OL"]
data = yf.download(tickers, start="2020-10-15", end="2025-10-15")

st.title("IND310 Project")
st.write(
    "This application allows you to view historical stock prices for selected companies."
)

# Prepare close data
all_close_data = data["Close"].copy()
all_close_data.columns = tickers  # Rename columns to just ticker names

# Calculate daily returns for each ticker
returns = all_close_data.pct_change().dropna()

# Define consistent colors for each ticker
color_map = {
    "EQNR.OL": "#2f4d8e",
    "DNB.OL": "#ffa659",
    "AKRBP.OL": "#ff6464",
    "ORK.OL": "#79ffbc",
    "MOWI.OL": "#c180ff",
}

# Multi-select for tickers
selected_tickers = st.multiselect(
    "Select ticker symbols to display:",
    tickers,
    default=tickers,  # All selected by default
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
