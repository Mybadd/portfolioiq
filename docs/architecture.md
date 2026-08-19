# PortfolioIQ — System Architecture

## 1. Architecture Overview

PortfolioIQ follows a modular, service-oriented architecture.

The system separates:

- Investor profile management
- Portfolio input
- Market data retrieval
- Portfolio processing
- Risk calculations
- Risk scoring
- Investor assessment
- Portfolio optimization
- Stress testing
- Monte Carlo simulation
- Risk reporting
- Frontend presentation

The separation allows individual components to be developed,
tested, and maintained independently.

---

## 2. High-Level Architecture

```text
                         INVESTOR
                            |
                            v
                    Investor Profile
                            |
                            v
                     Portfolio Input
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
     DMAT Holdings    Investment Amounts   Portfolio Weights
          |                 |                 |
          v                 v                 v
   Portfolio API      Portfolio API      Portfolio API
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    PortfolioService
                            |
                            v
                    Portfolio Model
                            |
                            v
                  Normalized Weights
                            |
          +-----------------+-----------------+-----------------+
          |                 |                 |                 |
          v                 v                 v                 v
    Risk Analysis      Optimization      Stress Testing    Monte Carlo
          |                 |                 |                 |
          v                 v                 v                 v
    RiskService      PortfolioOptimizer  Stress Services   MonteCarloService
          |                 |                 |                 |
          v                 v                 v                 v
    Risk Metrics      Optimized Weights   Scenario Impact   Simulated Returns
    Risk Score        Risk Comparison     Historical Events  Tail Risk
    Risk Contribution
          |                 |                 |                 |
          +-----------------+-----------------+-----------------+
                            |
                            v
                     Frontend Analysis
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      Dashboard         Risk Analysis      Decision Support
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    Investor Evaluation