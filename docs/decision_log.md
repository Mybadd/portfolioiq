# PortfolioIQ — Decision Log

This document records important architectural and implementation
decisions made during the development of PortfolioIQ and explains
the reasoning behind them.

---

## 2026-08-16

### 1. Backend-driven risk assessment

**Decision**

Risk scoring, investor compatibility assessment, and portfolio
recommendations are implemented in the Python backend rather than
calculated in the Next.js frontend.

**Reason**

These operations contain quantitative and business logic. Keeping
them in the backend avoids duplicating decision logic across the
frontend and makes the calculations easier to test and maintain.

**Implementation**

- `RiskScoringService` calculates the overall risk score.
- `RiskScoringService` classifies the portfolio risk.
- `InvestorAssessmentService` evaluates investor compatibility.
- `InvestorAssessmentService` generates recommendations.
- `risk_routes.py` combines the results into the Risk API response.
- The Dashboard displays the returned results.

**Result**

The frontend acts primarily as a presentation layer while the
backend remains responsible for quantitative portfolio decisions.

---

### 2. Risk analysis accepts investor profile information

**Decision**

The Risk API accepts the investor profile together with portfolio
weights.

**Reason**

Portfolio risk cannot be evaluated against an investor's requirements
without knowing the investor's risk tolerance, investment horizon, and
maximum acceptable loss.

**Implementation**

The Risk API accepts:

- Investment amount
- Investment horizon
- Risk tolerance
- Maximum acceptable loss
- Investment objective

**Result**

The backend can calculate both portfolio risk and
portfolio-investor compatibility in a single analysis request.

---

### 3. Maximum acceptable loss is represented as a decimal

**Decision**

Maximum acceptable loss is represented internally as a value between
`0` and `1`.

**Reason**

This matches the `InvestorProfile` validation rules and allows direct
comparison with decimal portfolio drawdown values.

**Examples**

- `0.10` = 10%
- `0.20` = 20%
- `0.30` = 30%

**Result**

The backend can directly compare:

`abs(maximum_drawdown)`

against:

`maximum_acceptable_loss`

---

### 4. Dashboard consumes backend risk results

**Decision**

The Dashboard uses the Risk API response for risk score, risk
category, compatibility, and recommendations.

**Reason**

The same quantitative result should be used throughout the
application rather than recalculating values independently in the
frontend.

**Result**

The Dashboard displays the actual backend analysis and remains
consistent with the Risk API.

---

### 5. Risk contribution is used for actionable recommendations

**Decision**

Asset-level risk contribution is used to identify concentrated
sources of portfolio risk.

**Reason**

Portfolio allocation alone does not show which asset is responsible
for portfolio risk. Risk contribution provides a more meaningful
basis for portfolio recommendations.

**Example**

If one asset contributes more than 40% of total portfolio risk, the
system can identify it as a concentration concern.

**Result**

The recommendation engine can provide asset-specific actions rather
than only generic portfolio-level warnings.
# PortfolioIQ — Decision Log

This document records important implementation decisions and the
reasoning behind them.

The purpose is to preserve why architectural and implementation
choices were made, rather than only documenting what was built.

---

## Decision 001 — Normalize All Portfolio Inputs to Weights

**Status:** Accepted

### Decision

All portfolio input methods ultimately produce normalized asset
weights before risk analysis.

### Input Methods

- DMAT holdings
- Investment amounts
- Portfolio weights

### Reasoning

The risk engine operates on portfolio weights when calculating
weighted portfolio returns.

Converting all input methods into a common representation allows
the same risk-analysis pipeline to be reused regardless of how the
investor entered the portfolio.

### Result

```text
DMAT Holdings
      ↓
Portfolio Weights
Investment Amounts
      ↓
Portfolio Weights
Portfolio Weights
      ↓
Portfolio Weights