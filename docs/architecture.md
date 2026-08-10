# PortfolioIQ — System Architecture

## 1. Architecture Overview

PortfolioIQ follows a modular, service-oriented backend architecture.

The system separates:

- Data models
- Market data retrieval
- Portfolio management
- Risk calculations
- Risk scoring
- Investor assessment
- Portfolio optimization
- Stress testing
- Risk reporting

This separation allows each component to be developed, tested, and maintained independently.

---

## 2. High-Level Architecture

```text
                    INVESTOR
                       |
                       v
              Portfolio Input
             /                 \
            /                   \
     Investment Amounts      DMAT Holdings
            |                   |
            |                   v
            |             Current Prices
            |                   |
            +--------+----------+
                     |
                     v
             PortfolioService
                     |
                     v
               Portfolio Model
                     |
                     v
             Portfolio Returns
                     |
                     v
                RiskService
                     |
        +------------+-------------+
        |            |             |
        v            v             v
   Risk Metrics  Risk Score   Risk Contribution
        |            |             |
        +------------+-------------+
                     |
                     v
          InvestorAssessmentService
                     |
        +------------+-------------+
        |                          |
        v                          v
 Constraint Feasibility       Recommendations
        |
        v
 PortfolioOptimizer
        |
        v
 Optimized Portfolio
        |
        +-------------------+
                            |
                            v
                  RiskReportService
                            |
                            v
                  Comprehensive Report