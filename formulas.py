import pandas as pd

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
    # Align the series to have matching dates
    combined = pd.concat([stock_returns, market_returns], axis=1, join='inner').dropna()
    combined.columns = ['stock', 'market']
    
    if len(combined) < 2:
        return 0
    
    covariance = combined['stock'].cov(combined['market'])
    market_variance = combined['market'].var()
    
    if market_variance == 0:
        return 0
    
    return covariance / market_variance