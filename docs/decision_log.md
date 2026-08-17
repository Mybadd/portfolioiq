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
## Decision 07 — Add Risk Parity Portfolio Optimization

**Date:** 2026-08-17

### Context

PortfolioIQ already supported quantitative portfolio risk analysis and
minimum-variance portfolio optimization. A minimum-variance objective
primarily minimizes portfolio variance and does not explicitly control
how total portfolio risk is distributed across individual assets.

### Decision

Add **Risk Parity** as a second portfolio optimization methodology.

Risk Parity attempts to make each asset contribute approximately equally
to total portfolio risk.

For asset i, the portfolio risk contribution is calculated as:

RC_i = w_i × (Σw)_i / (wᵀΣw)

For N assets, the optimizer targets:

RC_i ≈ 1/N

The implementation minimizes the squared deviation between each asset's
risk contribution and the equal-risk target.

### Constraints

The Risk Parity optimizer uses:

- Long-only portfolio weights.
- Portfolio weights summing to 100%.
- Configurable maximum allocation per asset.
- Optional maximum portfolio volatility.
- SLSQP constrained optimization.
- Covariance-matrix regularization for numerical stability.

### Rationale

Risk Parity provides a different portfolio construction philosophy
from Minimum Variance.

Minimum Variance asks:

> Which portfolio minimizes total variance?

Risk Parity asks:

> How can portfolio risk be distributed more evenly across assets?

This is particularly useful when one asset dominates the portfolio's
risk despite having a moderate capital allocation.

### Validation

For the five-asset test portfolio, Risk Parity produced approximately:

- NFLX: 20% risk contribution
- PEP: 20% risk contribution
- WMT: 20% risk contribution
- UNH: 20% risk contribution
- DIS: 20% risk contribution

This confirms that the implementation is optimizing risk contribution,
rather than simply assigning equal capital weights.

### Result

Risk Parity is now supported alongside Minimum Variance through the
optimization API.

Supported methods:

- `MINIMUM_VARIANCE`
- `RISK_PARITY`

The API returns the selected optimization method together with the
original weights, optimized weights, and before/after risk metrics.

---

## Decision 08 — Use Risk-Based Optimization Rather Than Drawdown-Only Optimization

**Date:** 2026-08-17

### Context

Maximum drawdown is an important portfolio risk metric, but directly
optimizing historical maximum drawdown can produce an objective that is
highly dependent on a particular historical path.

### Decision

Do not make historical maximum drawdown the sole optimization objective.

Instead, use multiple quantitative optimization methodologies and
evaluate their resulting portfolios using a common risk framework.

The comparison framework evaluates:

- Annualized volatility
- Maximum drawdown
- Sharpe ratio
- Historical VaR
- Expected Shortfall
- Portfolio risk score

### Rationale

This separates:

1. **Portfolio construction** — how weights are selected.
2. **Risk measurement** — how the resulting portfolio is evaluated.

This prevents a single historical metric from dominating the entire
optimization engine.

---

## Decision 09 — Add CVaR Optimization as the Next Quantitative Method

**Date:** 2026-08-17

### Context

PortfolioIQ already calculates Expected Shortfall (CVaR) as part of its
portfolio risk analysis. Risk Parity improves the distribution of risk
contributions, but it does not directly minimize losses in the tail of
the return distribution.

### Decision

The next optimization methodology will be **CVaR / Expected Shortfall
Optimization**.

The objective will focus on minimizing expected losses beyond a chosen
confidence threshold, such as the worst 5% of historical outcomes.

### Rationale

CVaR optimization directly connects portfolio construction with the
tail-risk metrics already reported by PortfolioIQ.

The planned optimization hierarchy is:

1. Minimum Variance
2. Risk Parity
3. CVaR / Expected Shortfall Optimization

Future methods may include:

- Maximum Sharpe Ratio
- Mean-CVaR Optimization
- Black-Litterman
- Robust Portfolio Optimization

### Expected Outcome

The optimization engine should allow users to select an optimization
method based on their desired portfolio construction objective rather
than relying on a single optimization model.