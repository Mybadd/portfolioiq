# Market Data Layer

## 1. Overview

The Market Data Layer is responsible for retrieving, validating, and providing market data required by the PortfolioIQ quantitative risk engine.

It currently uses Yahoo Finance through the `yfinance` Python library.

The market data layer supports:

- Historical stock prices
- Current/latest available stock prices
- Daily market data
- Symbol validation
- Market-data validation

---

## 2. Current Market Data Provider

### Primary Provider

Yahoo Finance

Implementation:

```python
import yfinance as yf