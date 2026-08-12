# PortfolioIQ Development Roadmap

## Project Status

PortfolioIQ is being developed as a quantitative portfolio risk
assessment and decision-support platform.

The implementation is being developed incrementally, starting with
the core backend risk engine and portfolio management functionality,
followed by the frontend and API integration.

---

## Phase 1 — Project Foundation

**Status: Completed**

- Established the project directory structure.
- Created separate modules for models, services, portfolio
  management, risk analysis, utilities, configuration, and APIs.
- Implemented centralized application logging.
- Defined financial constants and the supported market universe.

---

## Phase 2 — Market Data Layer

**Status: Completed**

- Implemented `MarketDataService`.
- Added stock symbol validation.
- Added historical market data retrieval using Yahoo Finance.
- Added current market price retrieval.
- Added downloaded market-data validation.
- Added support for storing historical data as CSV.
- Added error handling and logging for market-data operations.

### Current Market Data

- Historical data: 10 years
- Frequency: Daily
- Current price lookup: 5 days of daily data
- Primary implementation currently uses Yahoo Finance.

---

## Phase 3 — Portfolio Management

**Status: Completed**

- Implemented portfolio creation using asset weights.
- Implemented portfolio creation using investment amounts.
- Implemented portfolio creation from share holdings.
- Added portfolio weight validation.
- Added asset-symbol validation.
- Added investment amount validation.
- Added current-price-based portfolio valuation for share
  holdings.
- Implemented calculation of portfolio weights from share
  holdings.

### Portfolio Input Methods

1. DMAT Holdings
2. Investment Amounts
3. Portfolio Weights

---

## Phase 4 — Risk Analysis Engine

**Status: Completed**

Implemented quantitative portfolio risk calculations:

- Annualized volatility
- Maximum drawdown
- Sharpe ratio
- Historical Value at Risk (VaR)
- Expected Shortfall
- Risk contribution
- Stress testing

Risk calculation validation and error handling have also been
implemented.

---

## Phase 5 — Investor Profile and Assessment

**Status: Completed**

Implemented the `InvestorProfile` model with:

- Investment amount
- Investment horizon
- Risk tolerance
- Maximum acceptable loss
- Investment objective

Validation rules were added for investor inputs.

Portfolio allocation can also be validated against the investor's
investment amount.

---

## Phase 6 — Frontend Foundation

**Status: Completed**

Implemented the initial Next.js frontend.

### Investor Profile

The landing page collects:

- Investment amount
- Investment horizon
- Risk tolerance
- Maximum acceptable loss
- Investment objective

### Portfolio Page

Implemented portfolio input through:

- DMAT holdings
- Investment amounts
- Portfolio weights

The interface supports:

- Adding assets
- Removing assets
- Portfolio-weight validation
- Navigation between workflow stages

### Dashboard

Implemented the initial dashboard interface containing:

- Portfolio overview
- Risk score display
- Risk metrics
- Portfolio allocation
- Risk contribution
- Investor compatibility
- Recommended actions

The dashboard currently contains some mock analytical values that
will later be replaced with results from the backend risk engine.

---

## Phase 7 — FastAPI Integration

**Status: In Progress**

### Completed

- Added FastAPI application entry point.
- Added API health-check endpoint.
- Added FastAPI automatic documentation.
- Added portfolio creation API.
- Connected the portfolio API to the existing
  `PortfolioService`.
- Successfully tested the portfolio creation endpoint.

### Current Endpoints

```text
GET  /health
POST /api/portfolio/create

## Completed Milestones

### Portfolio Input
- Investor profile frontend implemented.
- Portfolio input page implemented.
- DMAT share-based portfolio input implemented.
- Portfolio weights calculated from current market prices.
- Portfolio data persisted using sessionStorage.

### Portfolio API
- `POST /api/portfolio/create` implemented and tested.
- `POST /api/portfolio/from-shares` implemented and tested.

### Risk API
- Risk metrics model completed.
- Portfolio historical data pipeline connected to RiskService.
- `POST /api/risk/analyze` implemented.
- Risk API tested successfully using Postman.
- Annualized volatility calculation verified.
- Maximum drawdown calculation verified.
- Sharpe ratio calculation verified.
- Historical VaR calculation verified.
- Expected Shortfall calculation verified.
- Asset-level risk contribution calculation verified.

### Frontend Integration
- Next.js frontend connected to FastAPI.
- Portfolio data passed from frontend to backend.
- Calculated portfolio weights displayed on Dashboard.
- Portfolio state preserved across navigation.  