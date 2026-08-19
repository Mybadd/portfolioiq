# PortfolioIQ — API Design

## 1. API Overview

PortfolioIQ exposes a REST API implemented using FastAPI.

The API separates request handling from quantitative business
logic by delegating calculations to dedicated service classes.

The main API domains are:

- Portfolio
- Risk Analysis
- Optimization
- Stress Testing
- Monte Carlo Simulation

---

## 2. Base URL

During local development:

```text
http://127.0.0.1:8000