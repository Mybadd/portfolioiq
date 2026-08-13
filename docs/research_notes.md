## Risk Analysis Methodology

### Annualized Volatility

Annualized volatility measures the variability of portfolio
returns over an annualized period.

The implementation uses daily portfolio returns and annualizes
the standard deviation using the configured trading-day
constant.

### Maximum Drawdown

Maximum drawdown measures the largest historical decline from
a previous portfolio peak.

The portfolio value is calculated from cumulative returns and
compared against the historical running maximum.

### Sharpe Ratio

The Sharpe ratio measures historical risk-adjusted performance.

It compares annualized excess portfolio returns against
annualized portfolio volatility.

### Historical Value at Risk

Historical VaR estimates the loss threshold at a selected
confidence level using the historical distribution of
portfolio returns.

The default confidence level is 95%.

### Expected Shortfall

Expected Shortfall measures the average portfolio return
during observations that fall beyond the historical VaR
threshold.

It therefore describes the severity of losses in the
historical tail.

### Risk Contribution

Risk contribution measures the proportion of portfolio variance
attributable to each asset.

This allows the system to identify assets that contribute
disproportionately to portfolio risk.
## Current Implementation

Risk analysis is performed using historical daily market data.

The current pipeline is:

1. Retrieve historical prices for portfolio assets.
2. Combine closing prices.
3. Calculate daily asset returns.
4. Calculate weighted portfolio returns.
5. Apply the risk-analysis calculations.
6. Calculate asset-level risk contribution.

The current Risk API exposes these calculations through:

`POST /api/risk/analyze`