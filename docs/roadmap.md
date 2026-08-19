
---

# 5. `docs/roadmap.md`

This one should clearly distinguish **implemented** from **future** work.

Replace it with:

```md
# PortfolioIQ — Roadmap

## 1. Completed

### Portfolio Construction

- Investor profile capture
- Portfolio input
- Portfolio validation
- Portfolio weight normalization
- Portfolio persistence through frontend session storage

### Market Data

- Historical market data retrieval
- Closing price extraction
- Historical daily return calculation

### Risk Analysis

- Volatility
- Maximum drawdown
- Sharpe ratio
- Historical VaR
- Expected Shortfall
- Risk score
- Asset-level risk contribution
- Investor risk compatibility

### Portfolio Optimization

- Minimum Variance
- Risk Parity
- CVaR
- Maximum asset weight constraint
- Optional target volatility
- Risk-free rate configuration
- Before/after risk comparison

### Stress Testing

- Hypothetical market scenarios
- Historical market events
- Portfolio impact calculation
- Asset-level stress contribution

### Monte Carlo Simulation

- Historical bootstrap simulation
- Multi-asset joint sampling
- 10,000 simulation support
- Configurable confidence level
- Reproducible random seed
- Multi-horizon simulation
- 1M / 3M / 6M / 1Y / 2Y horizons
- Return distribution histogram
- Tail-risk statistics

### Frontend

- Shared application navigation
- Portfolio page
- Dashboard
- Risk analysis
- Optimization
- Stress testing
- Monte Carlo simulation

---

## 2. Near-Term

### Reporting

Implement the `/report` route as a consolidated portfolio
analysis report.

Potential sections:

- Portfolio summary
- Risk summary
- Optimization results
- Stress test results
- Monte Carlo results
- Key quantitative metrics

The report should consume existing analysis results rather than
re-running every analysis independently.

### Testing

Expand automated testing for:

- Portfolio validation
- Risk calculations
- Optimization constraints
- Stress scenarios
- Monte Carlo simulation
- API validation
- Frontend integration

### API Improvements

Improve:

- Response schemas
- Error handling
- API documentation
- Input validation
- Configuration management

---

## 3. Medium-Term

### Advanced Monte Carlo Models

Evaluate additional simulation methodologies such as:

- Parametric simulation
- Multivariate distribution models
- Volatility-aware simulation
- Block bootstrap methods

These should only be introduced after validating the
historical-bootstrap implementation.

### Advanced Stress Testing

Potential extensions:

- Sector-specific shocks
- Asset-specific shocks
- Correlation breakdown scenarios
- Interest-rate scenarios
- Inflation scenarios
- Liquidity stress

### Portfolio Analytics

Potential additions:

- Rolling volatility
- Rolling Sharpe ratio
- Rolling drawdown
- Factor exposure
- Correlation analysis
- Concentration analysis

---

## 4. Long-Term

### Persistent User Portfolios

Move beyond browser session storage toward persistent portfolio
storage.

### Authentication

Introduce user authentication and portfolio ownership.

### Database Integration

Persist:

- Portfolios
- Investor profiles
- Analysis results
- Simulation configurations
- Historical reports

### Report Export

Support export of portfolio analysis reports to formats such
as PDF.

### Deployment

Prepare the application for production deployment with:

- Containerized services
- Production configuration
- Secure secrets management
- Monitoring
- Logging
- CI/CD

---

## 5. Out of Scope

The following are intentionally outside the current project
scope:

- Automated buy/sell recommendations
- Guaranteed return predictions
- Personalized financial advice
- Fully autonomous portfolio trading

PortfolioIQ is designed as a quantitative analysis and
decision-support platform.