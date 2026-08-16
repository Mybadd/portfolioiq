
---

# 4. `docs/roadmap.md`

The important part is to bring the roadmap up to the actual state.

Use this as the new roadmap:

```md
# PortfolioIQ Development Roadmap

## Project Status

PortfolioIQ is being developed as a quantitative portfolio risk
assessment and decision-support platform.

Development is being performed incrementally, beginning with the
core portfolio and quantitative risk engine, followed by API
integration and the frontend decision-support workflow.

---

# Phase 1 — Project Foundation

**Status: Completed**

- Established the project directory structure.
- Created separate modules for models, services, portfolio
  management, risk analysis, utilities, configuration, and APIs.
- Implemented centralized application logging.
- Defined financial constants and the supported market universe.

---

# Phase 2 — Market Data Layer

**Status: Completed**

- Implemented `MarketDataService`.
- Added stock symbol validation.
- Added historical market data retrieval using Yahoo Finance.
- Added current market price retrieval.
- Added downloaded market-data validation.
- Added error handling and logging for market-data operations.

### Current Market Data

- Historical period: approximately 10 years
- Frequency: Daily
- Current price lookup: 5 days
- Primary implementation: Yahoo Finance through `yfinance`

---

# Phase 3 — Portfolio Management

**Status: Completed**

- Implemented portfolio creation using asset weights.
- Implemented portfolio creation using investment amounts.
- Implemented portfolio creation using share holdings.
- Added portfolio weight validation.
- Added asset-symbol validation.
- Added investment amount validation.
- Added share quantity validation.
- Added current-price-based valuation for share holdings.
- Implemented calculation of portfolio weights from share holdings.
- Implemented normalization of investment amounts into portfolio
  weights.

### Portfolio Input Methods

1. DMAT Holdings
2. Investment Amounts
3. Portfolio Weights

### Portfolio Processing

```text
DMAT Holdings
      ↓
Current Market Prices
      ↓
Market Values
      ↓
Portfolio Weights