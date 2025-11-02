import yfinance as yf
import pandas as pd
import numpy as np

tickers = ['EQNR.OL','DNB.OL','AKRBP.OL','ORK.OL','MOWI.OL']
data = yf.download(tickers, start='2021-01-01', end='2025-10-01')['Adj Close']
returns = data.pct_change().dropna()

market = yf.download('^OSEAX', start='2021-01-01', end='2025-10-01')['Adj Close'].pct_change().dropna()

beta = {}
for t in tickers:
    aligned = returns[t].align(market, join='inner')
    cov = np.cov(aligned[0], aligned[1])[0, 1]
    var = aligned[1].var()
    beta[t] = cov / var