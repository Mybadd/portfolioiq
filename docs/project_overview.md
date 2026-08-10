# PortfolioIQ — Project Overview

## 1. Project Introduction

PortfolioIQ is a quantitative risk assessment and portfolio analysis system designed to help investors understand the risk associated with their stock portfolios.

The system combines historical market data, portfolio analytics, risk metrics, investor preferences, portfolio optimization, and recommendations into a single risk assessment workflow.

The primary objective is not simply to determine whether a stock or portfolio has performed well, but to determine whether the portfolio's risk characteristics are appropriate for a particular investor.

---

## 2. Problem Statement

Investors may hold multiple stocks without having a clear understanding of the overall risk of their portfolio.

Looking at individual stock performance is not sufficient because:

- Different stocks have different levels of volatility.
- Some assets contribute disproportionately to portfolio risk.
- Historical losses may be larger than an investor is willing to tolerate.
- A portfolio can have acceptable volatility but still experience significant drawdowns.
- The same portfolio may be suitable for one investor and unsuitable for another.
- Investors may not know whether their desired risk constraints can actually be satisfied using the available assets.

PortfolioIQ addresses these problems by combining quantitative portfolio analysis with investor-specific risk requirements.

---

## 3. Target User

The primary user is an investor who wants to evaluate the risk of an existing or proposed stock portfolio.

The system supports two practical portfolio input methods:

### 3.1 Existing DMAT Holdings

An investor can provide the number of shares held for each supported stock.

Example:

    NFLX: 5 shares
    PEP: 10 shares
    WMT: 8 shares
    UNH: 6 shares
    DIS: 4 shares

The system retrieves current market prices and calculates the market value and portfolio weight of each holding.

### 3.2 Investment Amounts

An investor can provide the monetary amount allocated to each stock.

Example:

    NFLX: ₹200,000
    PEP: ₹250,000
    WMT: ₹200,000
    UNH: ₹150,000
    DIS: ₹200,000

The amounts are converted into portfolio weights.

---

## 4. Investor Profile

PortfolioIQ represents an investor using an `InvestorProfile`.

The investor profile contains:

- Investment amount
- Investment horizon
- Risk tolerance
- Maximum acceptable loss
- Investment objective

Example:

    Investment Amount: ₹1,000,000
    Investment Horizon: 7 years
    Risk Tolerance: MODERATE
    Maximum Acceptable Loss: 20%
    Investment Objective: LONG_TERM_GROWTH

The investor profile is used when evaluating whether the portfolio is appropriate for that investor.

---

## 5. Portfolio Processing

All portfolio inputs are ultimately converted into portfolio weights.

For investment amounts:

    Investment Amounts
            ↓
    Position Values
            ↓
    Portfolio Weights

For DMAT holdings:

    Number of Shares
            ↓
    Current Market Prices
            ↓
    Position Values
            ↓
    Portfolio Weights

The portfolio is represented internally using a `Portfolio` model containing asset weights.

---

## 6. Market Data

Historical market data is retrieved using Yahoo Finance through the `yfinance` library.

The system currently retrieves approximately 10 years of daily historical data for supported stocks.

Current market prices are also retrieved when converting DMAT share holdings into portfolio weights.

Market data is validated before being used by the portfolio and risk calculation services.

---

## 7. Quantitative Risk Metrics

PortfolioIQ calculates several quantitative risk measures.

### 7.1 Annualized Volatility

Measures the annualized variability of portfolio returns.

Higher volatility generally indicates greater uncertainty in portfolio returns.

### 7.2 Maximum Drawdown

Measures the largest historical decline from a previous portfolio peak.

The metric is represented as a negative return.

Example:

    Maximum Drawdown: -39.10%

### 7.3 Sharpe Ratio

Measures historical risk-adjusted performance by comparing excess returns with portfolio volatility.

### 7.4 Historical Value at Risk

Historical VaR estimates a loss threshold at a selected confidence level using historical portfolio returns.

The current implementation uses a 95% confidence level by default.

### 7.5 Expected Shortfall

Expected Shortfall measures the average return of observations that fall beyond the historical VaR threshold.

It provides information about the severity of losses in the tail of the historical return distribution.

### 7.6 Risk Contribution

The system calculates the proportion of total portfolio variance attributable to each asset.

This helps identify assets that contribute disproportionately to portfolio risk.

---

## 8. Overall Risk Score

The individual risk metrics are converted into a single risk score from 0 to 100.

A higher score represents higher portfolio risk.

The current system considers:

- Annualized volatility
- Maximum drawdown
- Historical VaR
- Expected Shortfall
- Sharpe ratio

The numerical score is classified into:

    LOW
    MODERATE
    HIGH
    VERY HIGH

---

## 9. Investor Compatibility

The system compares the portfolio's risk characteristics with the investor profile.

The assessment considers:

- Portfolio risk score
- Investor risk tolerance
- Maximum acceptable loss
- Investment horizon

The resulting recommendation can be:

    SUITABLE
    REVIEW
    NOT SUITABLE

The system also provides reasons explaining why the portfolio received the recommendation.

---

## 10. Constraint Feasibility

PortfolioIQ checks whether an investor's constraints can actually be satisfied using the available asset universe.

Examples of constraints include:

- Maximum acceptable loss
- Target volatility
- Maximum asset allocation

If the available assets cannot satisfy the investor's constraints, the system reports that the constraints are not feasible.

This is important because an investor's desired risk level may not always be achievable using the available stocks.

---

## 11. Portfolio Optimization

The portfolio optimization component searches for portfolio allocations that satisfy specified constraints while optimizing portfolio characteristics.

The system can evaluate whether a suitable portfolio can be constructed from the available assets.

Optimization is particularly useful when the current portfolio does not align with the investor's risk requirements.

---

## 12. Stress Testing

The system supports hypothetical stress scenarios in which predefined shocks are applied to individual assets.

For example:

    NFLX: -20%
    PEP:  -10%

The system calculates the estimated portfolio impact based on the asset weights and scenario shocks.

Stress testing helps investors understand how the portfolio could respond to adverse hypothetical market conditions.

---

## 13. Comprehensive Risk Report

The `RiskReportService` combines the major analysis components into a single report.

The report contains:

- Portfolio risk metrics
- Overall risk score
- Risk classification
- Investor assessment
- Constraint feasibility
- Asset risk contributions
- Recommendations

Example:

    Risk Score: 38.00 / 100
    Risk Level: MODERATE
    Recommendation: REVIEW

The report can also explain specific issues such as:

    Historical maximum drawdown exceeds
    the investor's maximum acceptable loss.

And:

    NFLX contributes approximately 52.3%
    of portfolio risk.

---

## 14. Validation

The system validates user and portfolio inputs before performing calculations.

Examples include:

- Empty portfolios are rejected.
- Portfolio weights must be positive.
- Portfolio weights must sum to 100%.
- Unsupported stock symbols are rejected.
- Investment amounts must be positive.
- Share quantities must be positive.
- Investor investment amounts must be positive.
- Maximum acceptable loss must be within the valid range.
- Invalid risk tolerances are rejected.
- Invalid confidence levels are rejected.

---

## 15. Automated Testing

The project is being developed with automated tests using `pytest`.

Current automated test coverage includes:

### Portfolio Tests

    tests/test_portfolio.py

Current status:

    8 tests passed

### Risk Tests

    tests/test_risk.py

Current status:

    15 tests passed

### Current Total

    23 tests passed

The test suite covers both successful calculations and invalid-input scenarios.

---

## 16. Current Architecture

The current backend follows a service-oriented structure.

    Investor / Portfolio Input
              ↓
       PortfolioService
              ↓
       Portfolio Model
              ↓
       RiskService
              ↓
    RiskScoringService
              ↓
    InvestorAssessmentService
              ↓
       RiskReportService
              ↓
       Comprehensive Report

Market data is provided through the market-data and portfolio-data services.

---

## 17. Current Project Scope

The current system focuses on stock portfolio risk analysis.

The current DMAT portfolio workflow focuses on securities holdings rather than cash-management functionality.

Cash balances, deposits, withdrawals, and broader account-management functionality are outside the current scope.

---

## 18. Project Status

The quantitative backend currently contains the major portfolio risk-analysis components:

- Portfolio management
- Market data retrieval
- Investor profiling
- Risk metrics
- Risk scoring
- Investor compatibility assessment
- Constraint feasibility
- Portfolio optimization
- Stress testing
- Risk reporting
- Automated testing

The next development phase will focus on organizing the automated test suite and subsequently exposing the backend functionality through an application/API layer.