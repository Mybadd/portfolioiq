
---

# 2. `docs/architecture.md`

Replace the architecture flow with this structure:

```md
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
                            v
                   Risk Analysis API
                            |
                            v
                    RiskService
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
    Risk Metrics       Risk Score       Risk Contribution
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
             InvestorAssessmentService
                            |
                  +---------+---------+
                  |                   |
                  v                   v
        Compatibility        Recommendations
                  |
                  v
            Risk Dashboard
                  |
                  v
        Investor Decision Support