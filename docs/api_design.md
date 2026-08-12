# API Design

## Overview

PortfolioIQ uses FastAPI to expose the quantitative portfolio
risk engine to the frontend application.

The API acts as an interface between the Next.js frontend and
the Python backend services.

## Current API

### Health Check

**Method:** GET

**Endpoint:**
`/health`

**Purpose:**
Verifies that the PortfolioIQ API is running correctly.

### Create Portfolio

**Method:** POST

**Endpoint:**
`/api/portfolio/create`

**Purpose:**
Creates and validates a portfolio using asset allocation
weights.

**Request:**

```json
{
  "weights": {
    "NFLX": 0.20,
    "PEP": 0.25,
    "WMT": 0.20,
    "UNH": 0.15,
    "DIS": 0.20
  }
}
## Risk Analysis API

### POST /api/risk/analyze

Calculates quantitative risk metrics for a portfolio using
historical market data.

#### Request

```json
{
  "weights": {
    "NFLX": 0.0681,
    "PEP": 0.2520,
    "WMT": 0.1650,
    "UNH": 0.4394,
    "DIS": 0.0754
  },
  "risk_free_rate": 0.0,
  "confidence_level": 0.95
}
Processing

The API performs the following steps:

Validates portfolio weights.
Retrieves historical market data.
Combines closing prices.
Calculates daily asset returns.
Calculates weighted portfolio returns.
Calculates quantitative risk metrics.
Calculates asset-level risk contribution.
Response

The API returns:

Portfolio weights
Annualized volatility
Maximum drawdown
Sharpe ratio
Historical VaR
Expected Shortfall
Asset-level risk contribution
Confidence level
Risk-free rate
Number of trading days
{
  "metrics": {
    "annualized_volatility": 0.1897,
    "maximum_drawdown": -0.3237,
    "sharpe_ratio": 0.6866,
    "historical_var": -0.0161,
    "expected_shortfall": -0.0274
  },
  "confidence_level": 0.95,
  "risk_free_rate": 0.0,
  "trading_days": 2511
}
Validation

The API rejects:

Empty portfolios
Negative weights
Weights that do not sum to 1.0
Invalid confidence levels