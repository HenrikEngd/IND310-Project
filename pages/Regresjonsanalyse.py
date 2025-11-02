import pandas as pd
import streamlit as st
import statsmodels.api as sm
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
    st.dataframe(
        coef_df.style.format({
            'Coefficient': '{:.6f}',
            'Std Error': '{:.6f}',
            't-value': '{:.3f}',
            'p-value': '{:.4f}'
        }).background_gradient(subset=['p-value'], cmap='RdYlGn_r', vmin=0, vmax=0.1),
        use_container_width=True
    )
    
    st.divider()
