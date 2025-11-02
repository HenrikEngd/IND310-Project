def returns(price_series):
    """
    Calculate daily percentage returns from a series of prices.
    
    Formula: Return_t = (Price_t - Price_(t-1)) / Price_(t-1)
    
    Args:
        price_series: Series of stock prices over time.
    
    Returns:
        Series of daily percentage returns.
    """
    return price_series.pct_change().dropna()

def adjusted_close_price(raw_close_price, dividends, splits):
    """
    Calculate adjusted close prices accounting for dividends and stock splits.
    
    Args:
        raw_close_price: DataFrame or Series of raw closing prices.
        dividends: DataFrame or Series of dividend payments.
        splits: DataFrame or Series of stock split ratios.
    
    Returns:
        DataFrame or Series of adjusted closing prices.
    """
    import pandas as pd
    
    if isinstance(raw_close_price, pd.DataFrame):
        # Handle multiple tickers
        adj_prices = pd.DataFrame(index=raw_close_price.index, columns=raw_close_price.columns)
        for ticker in raw_close_price.columns:
            adj_prices[ticker] = adjusted_close_price(
                raw_close_price[ticker],
                dividends[ticker],
                splits[ticker]
            )
        return adj_prices
    
    # Handle single ticker (Series)
    adj_price = raw_close_price.copy()
    cumulative_split = 1.0
    for i in range(len(adj_price)-1, -1, -1):
        if splits.iloc[i] != 0 and splits.iloc[i] != 1:
            cumulative_split *= splits.iloc[i]
        adj_price.iloc[i] = (adj_price.iloc[i] + dividends.iloc[i]) / cumulative_split
    return adj_price

def return_on_equity(net_income, equity):
    """
    Calculate Return on Equity (ROE).
    Measures the company's ability to generate profit on invested equity.
    
    Formula: ROE = Net Income / Equity
    
    Args:
        net_income: Net income after tax (Resultat etter skatt)
        equity: Total shareholders' equity (Egenkapital)
    
    Returns:
        ROE as a percentage
    """
    if equity == 0:
        return 0
    return (net_income / equity) * 100

def debt_to_equity_ratio(total_liabilities, equity):
    """
    Calculate Debt-to-Equity Ratio (D/E).
    Shows how much of the capital structure is financed by debt.
    
    Formula: D/E = Total Liabilities / Equity
    
    Args:
        total_liabilities: Total liabilities (Totale forpliktelser)
        equity: Total shareholders' equity (Egenkapital)
    
    Returns:
        Debt-to-equity ratio
    """
    if equity == 0:
        return 0
    return total_liabilities / equity

def price_to_earnings_ratio(stock_price, earnings_per_share):
    """
    Calculate Price-to-Earnings Ratio (P/E).
    Shows how much investors pay per unit of earnings.
    
    Formula: P/E = Stock Price / Earnings per Share
    
    Args:
        stock_price: Current stock price (Aksjekurs)
        earnings_per_share: Earnings per share (Resultat per aksje)
    
    Returns:
        P/E ratio
    """
    if earnings_per_share == 0:
        return 0
    return stock_price / earnings_per_share

def ebitda_margin(ebitda, operating_revenue):
    """
    Calculate EBITDA Margin.
    Shows operational profitability independent of financing and depreciation.
    
    Formula: EBITDA Margin = (EBITDA / Operating Revenue) × 100
    
    Args:
        ebitda: Earnings Before Interest, Taxes, Depreciation and Amortization
        operating_revenue: Total operating revenue (Driftsinntekter)
    
    Returns:
        EBITDA margin as a percentage
    """
    if operating_revenue == 0:
        return 0
    return (ebitda / operating_revenue) * 100

def dividend_yield(annual_dividend_per_share, stock_price):
    """
    Calculate Dividend Yield (DY).
    Shows the cash flow returned to shareholders relative to stock price.
    
    Formula: DY = Annual Dividend per Share / Stock Price
    
    Args:
        annual_dividend_per_share: Annual dividend per share (Årlig utbytte per aksje)
        stock_price: Current stock price (Aksjekurs)
    
    Returns:
        Dividend yield as a percentage
    """
    if stock_price == 0:
        return 0
    return (annual_dividend_per_share / stock_price) * 100

def beta(stock_returns, market_returns):
    """
    Calculate Beta coefficient.
    Measures the stock's volatility relative to the market.
    
    Formula: Beta = Covariance(Stock Returns, Market Returns) / Variance(Market Returns)
    
    Args:
        stock_returns: Series of stock returns
        market_returns: Series of market index returns
    
    Returns:
        Beta coefficient
    """
    import pandas as pd
    
    # Debug: print input info
    print(f"Stock returns length: {len(stock_returns)}, Market returns length: {len(market_returns)}")
    print(f"Stock returns index type: {type(stock_returns.index)}")
    print(f"Market returns index type: {type(market_returns.index)}")
    print(f"Stock returns first/last dates: {stock_returns.index[0]} to {stock_returns.index[-1]}")
    print(f"Market returns first/last dates: {market_returns.index[0]} to {market_returns.index[-1]}")
    
    # Align the series to have matching dates
    combined = pd.concat([stock_returns, market_returns], axis=1, join='inner').dropna()
    combined.columns = ['stock', 'market']
    
    print(f"Combined length after join: {len(combined)}")
    print(f"Covariance: {combined['stock'].cov(combined['market'])}")
    print(f"Market variance: {combined['market'].var()}")
    
    if len(combined) < 2:
        return 0
    
    covariance = combined['stock'].cov(combined['market'])
    market_variance = combined['market'].var()
    
    if market_variance == 0:
        return 0
    
    return covariance / market_variance