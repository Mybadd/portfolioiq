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