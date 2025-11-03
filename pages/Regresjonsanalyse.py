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

# SMB = Avkastning fra små selskaper minus avkastning fra store selskaper
small = returns_df[['AKRBP.OL', 'MOWI.OL', 'ORK.OL']].mean(axis=1)
big = returns_df[['EQNR.OL', 'DNB.OL']].mean(axis=1)
SMB = small - big

# HML = Avkastning fra høy bokført-til-markedsverdi minus lav bokført-til-markedsverdi
value = returns_df[['AKRBP.OL', 'DNB.OL', 'EQNR.OL']].mean(axis=1)
growth = returns_df[['ORK.OL', 'MOWI.OL']].mean(axis=1)
HML = value - growth

Rf = 0.0 # Risikofri rente

factors = pd.concat([market_returns - Rf, SMB, HML], axis=1)
factors.columns = ['Market-Rf', 'SMB', 'HML']
factors = sm.add_constant(factors)

results = {}
for col in returns_df.columns:
    Ri = returns_df[col] - Rf
    model = sm.OLS(Ri, factors, missing='drop').fit()
    results[col] = model

# Vis resultater for hver aksje
st.title("Fama-French Trefaktormodell - Resultater")

# Lag sammendragsdata for diagrammer
r_squared_data = []
all_coefficients = []

for ticker, model in results.items():
    r_squared_data.append({
        'Ticker': ticker,
        'R²': model.rsquared
    })
    
    for i, factor in enumerate(['Intercept (α)', 'Marked-Rf (β)', 'SMB', 'HML']):
        all_coefficients.append({
            'Ticker': ticker,
            'Faktor': factor,
            'Koeffisient': model.params.values[i]
        })

# R² søylediagram
st.header("R² Sammenligning på tvers av aksjer")
r2_df = pd.DataFrame(r_squared_data)
r2_chart = alt.Chart(r2_df).mark_bar().encode(
    x=alt.X('Ticker:N', title='Aksje'),
    y=alt.Y('R²:Q', title='R² Verdi', scale=alt.Scale(domain=[0, 1])),
    color=alt.Color('R²:Q', scale=alt.Scale(scheme='blues'), legend=None),
    tooltip=['Ticker', alt.Tooltip('R²:Q', format='.4f')]
).properties(
    height=400
)
st.altair_chart(r2_chart, use_container_width=True)

# Grupperte søylediagram for koeffisienter
st.header("Sammenligning av faktorkoeffisienter")

# Filtrer bort Intercept for renere visualisering (valgfritt)
coef_df_chart = pd.DataFrame(all_coefficients)
coef_df_chart = coef_df_chart[coef_df_chart['Faktor'] != 'Intercept (α)']

coef_chart = alt.Chart(coef_df_chart).mark_bar().encode(
    x=alt.X('Ticker:N', title='Aksje', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Koeffisient:Q', title='Koeffisientverdi'),
    color=alt.Color('Faktor:N', 
                    scale=alt.Scale(scheme='category10'),
                    legend=alt.Legend(title='Faktor')),
    xOffset='Faktor:N',
    tooltip=['Ticker', 'Faktor', alt.Tooltip('Koeffisient:Q', format='.6f')]
).properties(
    height=400
)

st.altair_chart(coef_chart, use_container_width=True)

st.divider()

# Detaljerte resultater for hver aksje
st.header("Detaljerte regresjonsresultater")

for ticker, model in results.items():
    st.subheader(f"{ticker}")
    
    # Vis hovedstatistikk i kolonner
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("R²", f"{model.rsquared:.4f}")
    with col2:
        st.metric("Justert R²", f"{model.rsquared_adj:.4f}")
    with col3:
        st.metric("F-statistikk", f"{model.fvalue:.2f}")
    
    # Vis koeffisienter i en pen tabell
    coef_df = pd.DataFrame({
        'Faktor': ['Intercept (α)', 'Marked-Rf (β)', 'SMB', 'HML'],
        'Koeffisient': model.params.values,
        'Standardfeil': model.bse.values,
        't-verdi': model.tvalues.values,
        'p-verdi': model.pvalues.values
    })
    
    # Formater numeriske kolonner
    coef_df['Koeffisient'] = coef_df['Koeffisient'].apply(lambda x: f"{x:.6f}")
    coef_df['Standardfeil'] = coef_df['Standardfeil'].apply(lambda x: f"{x:.6f}")
    coef_df['t-verdi'] = coef_df['t-verdi'].apply(lambda x: f"{x:.3f}")
    coef_df['p-verdi'] = coef_df['p-verdi'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(coef_df, use_container_width=True)
    
    st.divider()
