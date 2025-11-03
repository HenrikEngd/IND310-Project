import pandas as pd
import streamlit as st
import statsmodels.api as sm
import altair as alt
from data_cache import load_market_data

# Hent data fra cache
try:
    data, adj_close_data, returns_df, betas = load_market_data()
    
    # Hent markedsdata for OSEBX
    import yfinance as yf
    from data_cache import DEFAULT_START, DEFAULT_END
    market_data = yf.Ticker("OSEBX.OL").history(start=DEFAULT_START, end=DEFAULT_END)
    market_data.index = market_data.index.tz_localize(None)
    market_returns = market_data['Close'].pct_change().dropna()
    
except Exception as e:
    st.error(f"Kunne ikke laste data: {e}")
    st.stop()

# SMB = Returns of small firms minus returns of big firms
small = returns_df[['AKRBP.OL', 'MOWI.OL', 'ORK.OL']].mean(axis=1)
big = returns_df[['EQNR.OL', 'DNB.OL']].mean(axis=1)
SMB = small - big

# HML = Returns of high book-to-market firms minus returns of low book-to-market firms
value = returns_df[['AKRBP.OL', 'DNB.OL', 'EQNR.OL']].mean(axis=1)
growth = returns_df[['ORK.OL', 'MOWI.OL']].mean(axis=1)
HML = value - growth

Rf = 0.0 # Risk free rate

factors = pd.concat([market_returns - Rf, SMB, HML], axis=1)
factors.columns = ['Market-Rf', 'SMB', 'HML']
factors = sm.add_constant(factors)

results = {}
for col in returns_df.columns:
    Ri = returns_df[col] - Rf
    model = sm.OLS(Ri, factors, missing='drop').fit()
    results[col] = model

# Vis resultater for hver aksje
st.title("Fama-French Three-Factor Model Results")

# Create summary data for charts
r_squared_data = []
all_coefficients = []

for ticker, model in results.items():
    r_squared_data.append({
        'Ticker': ticker,
        'R²': model.rsquared
    })
    
    for i, factor in enumerate(['Intercept (α)', 'Market-Rf (β)', 'SMB', 'HML']):
        all_coefficients.append({
            'Ticker': ticker,
            'Factor': factor,
            'Coefficient': model.params.values[i]
        })

# R² Bar Chart
st.header("R² Comparison Across Stocks")
r2_df = pd.DataFrame(r_squared_data)
r2_chart = alt.Chart(r2_df).mark_bar().encode(
    x=alt.X('Ticker:N', title='Stock Ticker'),
    y=alt.Y('R²:Q', title='R² Value', scale=alt.Scale(domain=[0, 1])),
    color=alt.Color('R²:Q', scale=alt.Scale(scheme='blues'), legend=None),
    tooltip=['Ticker', alt.Tooltip('R²:Q', format='.4f')]
).properties(
    height=400
)
st.altair_chart(r2_chart, use_container_width=True)

# Coefficients Grouped Bar Chart
st.header("Factor Coefficients Comparison")

# Filter to exclude Intercept for cleaner visualization (optional)
coef_df_chart = pd.DataFrame(all_coefficients)
coef_df_chart = coef_df_chart[coef_df_chart['Factor'] != 'Intercept (α)']

coef_chart = alt.Chart(coef_df_chart).mark_bar().encode(
    x=alt.X('Ticker:N', title='Stock Ticker', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Coefficient:Q', title='Coefficient Value'),
    color=alt.Color('Factor:N', 
                    scale=alt.Scale(scheme='category10'),
                    legend=alt.Legend(title='Factor')),
    xOffset='Factor:N',
    tooltip=['Ticker', 'Factor', alt.Tooltip('Coefficient:Q', format='.6f')]
).properties(
    height=400
)

st.altair_chart(coef_chart, use_container_width=True)

st.divider()

# Detailed results for each stock
st.header("Detailed Regression Results")

for ticker, model in results.items():
    st.subheader(f"{ticker}")
    
    # Vis hovedstatistikk i kolonner
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("R²", f"{model.rsquared:.4f}")
    with col2:
        st.metric("Adjusted R²", f"{model.rsquared_adj:.4f}")
    with col3:
        st.metric("F-statistic", f"{model.fvalue:.2f}")
    
    # Vis koeffisienter i en pen tabell
    coef_df = pd.DataFrame({
        'Factor': ['Intercept (α)', 'Market-Rf (β)', 'SMB', 'HML'],
        'Coefficient': model.params.values,
        'Std Error': model.bse.values,
        't-value': model.tvalues.values,
        'p-value': model.pvalues.values
    })
    
    # Formater numeriske kolonner
    coef_df['Coefficient'] = coef_df['Coefficient'].apply(lambda x: f"{x:.6f}")
    coef_df['Std Error'] = coef_df['Std Error'].apply(lambda x: f"{x:.6f}")
    coef_df['t-value'] = coef_df['t-value'].apply(lambda x: f"{x:.3f}")
    coef_df['p-value'] = coef_df['p-value'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(coef_df, use_container_width=True)
    
    st.divider()
