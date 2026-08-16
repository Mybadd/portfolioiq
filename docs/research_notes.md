
---

# 3. `docs/research_notes.md`

Replace/update it with:

```md
# PortfolioIQ — Research Notes

## 1. Risk Analysis Methodology

PortfolioIQ performs quantitative risk analysis using historical
daily market data.

The current analysis pipeline is:

1. Retrieve historical prices.
2. Validate market data.
3. Combine closing prices.
4. Calculate daily asset returns.
5. Calculate weighted portfolio returns.
6. Calculate portfolio risk metrics.
7. Calculate asset-level risk contribution.
8. Convert metrics into an overall risk score.
9. Compare portfolio risk with investor requirements.
10. Generate recommendations.

---

## 2. Annualized Volatility

Annualized volatility measures the variability of portfolio
returns over an annualized period.

The implementation uses daily portfolio returns and annualizes
their standard deviation using the configured trading-day
constant.

Higher volatility indicates greater uncertainty in portfolio
returns.

---

## 3. Maximum Drawdown

Maximum drawdown measures the largest historical decline from a
previous portfolio peak.

The metric is represented as a negative return.

Portfolio value is calculated from cumulative returns and compared
with the historical running maximum.

---

## 4. Sharpe Ratio

The Sharpe ratio measures historical risk-adjusted performance.

It compares annualized excess portfolio returns with annualized
portfolio volatility.

The calculation uses the configured annual risk-free rate.

---

## 5. Historical Value at Risk

Historical VaR estimates a loss threshold at a selected
confidence level using the historical distribution of portfolio
returns.

The current default confidence level is 95%.

---

## 6. Expected Shortfall

Expected Shortfall measures the average portfolio return during
observations that fall beyond the historical VaR threshold.

It therefore describes the severity of losses in the historical
tail.

---

## 7. Risk Contribution

Risk contribution measures the proportion of portfolio variance
attributable to each asset.

This allows the system to identify assets that contribute
disproportionately to portfolio risk.

A high portfolio allocation does not necessarily correspond to
the highest risk contribution because risk contribution depends on
the historical behavior of the asset and its interaction with the
portfolio.

---

# 8. Overall Risk Score

PortfolioIQ converts the quantitative risk metrics into a single
risk score ranging from 0 to 100.

A higher score represents higher portfolio risk.

The current scoring model considers:

- Annualized volatility
- Maximum drawdown
- Historical VaR
- Expected Shortfall
- Sharpe ratio adjustment

The resulting score is classified as:

| Score | Classification |
|---|---|
| 0–24.99 | LOW |
| 25–49.99 | MODERATE |
| 50–74.99 | HIGH |
| 75–100 | VERY HIGH |

The scoring model is implemented in `RiskScoringService`.

---

# 9. Investor Compatibility

Risk analysis is not evaluated independently of the investor.

The system compares portfolio risk with:

- Investor risk tolerance
- Maximum acceptable loss
- Investment horizon
- Portfolio risk score

The assessment produces:

- `SUITABLE`
- `REVIEW`
- `NOT SUITABLE`

The service also provides explanatory reasons for the
classification.

For example, a portfolio may have a moderate risk score but still
require review if its historical maximum drawdown exceeds the
investor's maximum acceptable loss.

---

# 10. Recommendations

The Investor Assessment Service generates actionable
recommendations.

Current recommendation rules consider:

### Maximum Drawdown

If historical drawdown exceeds the investor's maximum acceptable
loss, the system recommends reducing portfolio exposure.

### Risk Concentration

If one asset contributes more than 40% of portfolio risk, the
system identifies the asset as a concentration concern.

### Risk Tolerance

The system provides additional recommendations when the portfolio
risk score exceeds the investor's stated tolerance.

### Investment Horizon

Short investment horizons combined with higher portfolio risk may
generate an additional warning.

---

# 11. Portfolio Input Methodology

PortfolioIQ supports three input methods.

## DMAT Holdings

The user provides the number of shares held.

```text
Shares
  ↓
Current Market Price
  ↓
Market Value
  ↓
Portfolio Weight