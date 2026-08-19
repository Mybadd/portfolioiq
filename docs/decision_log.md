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

## Decision: Historical Stress Testing

### Decision

Add historical market-event stress testing alongside the existing
hypothetical stress-testing framework.

### Rationale

Hypothetical stress testing evaluates the portfolio under manually
defined asset-level shocks, while historical stress testing replays
actual market behavior observed during a defined historical period.

Historical scenarios provide an economically plausible stress case
because the underlying market movements actually occurred. However,
historical scenarios are backward-looking and do not imply that the
same event or loss will recur.

### Implementation

Historical stress testing uses the existing portfolio market-data
pipeline.

The process is:

1. Retrieve historical closing prices for all portfolio assets.
2. Select the dates corresponding to the historical scenario.
3. Calculate each asset's event-period return:

   R_i = (P_i,end / P_i,start) - 1

4. Calculate the portfolio impact:

   R_p = Σ(w_i × R_i)

5. Calculate the portfolio value after the event:

   V_after = 1 + R_p

6. Calculate the recovery return required:

   Recovery = (1 / V_after) - 1

7. Calculate each asset's contribution:

   Contribution_i = w_i × R_i

### Historical Scenarios

The first supported scenarios are:

| Scenario | Start Date | End Date |
|---|---|---|
| COVID-19 Crash | 2020-02-19 | 2020-03-23 |
| 2022 Bear Market | 2022-01-03 | 2022-10-12 |

### API

Historical stress testing is exposed through:

POST `/api/stress-test/historical`

The existing hypothetical stress-testing endpoint remains:

POST `/api/stress-test/analyze`

This keeps hypothetical and historical stress testing as separate
scenario methodologies while sharing the same portfolio and result
framework.

### Example Result

For the portfolio:

- NFLX: 10%
- PEP: 20%
- WMT: 15%
- UNH: 40%
- DIS: 15%

the COVID-19 Crash scenario produced:

- Portfolio impact: -27.02%
- Portfolio value after event: 72.98%
- Recovery required: 37.02%

UNH was the largest contributor to the portfolio loss:

- Portfolio weight: 40%
- Historical return: -36.18%
- Portfolio contribution: -14.47%

### Risk Interpretation

Historical stress testing is complementary to statistical risk
measures such as volatility, VaR, and Expected Shortfall. It provides
a concrete scenario-based view of portfolio vulnerability rather than
a probability estimate of future losses.

Historical scenarios should therefore not be interpreted as forecasts.
They demonstrate how the current portfolio would have behaved if the
specified historical asset movements were applied to it.

### Design Decision

The implementation intentionally reuses the existing
`PortfolioDataService` rather than introducing a separate market-data
pipeline.

This reduces duplicated data retrieval logic and ensures that
historical stress testing uses the same market-data source as the
portfolio risk and optimization modules.
## Monte Carlo Simulation

### Decision

Implemented historical bootstrap Monte Carlo simulation
for forward-looking portfolio return and tail-risk analysis.

### Method

Historical daily asset-return observations are sampled
with replacement. Complete historical rows are sampled
together to preserve cross-asset relationships.

### Horizons

- 1M — 21 trading days
- 3M — 63 trading days
- 6M — 126 trading days
- 1Y — 252 trading days
- 2Y — 504 trading days

### Simulation Configuration

- Default simulations: 10,000
- Confidence level: 95%
- Random seed: 42
- Historical observations: determined from available market data

### Metrics

- Mean Return
- Median Return
- Probability of Loss
- Value at Risk (VaR)
- Expected Shortfall

### Frontend

The backend calculates all supported horizons in a
single request. The frontend provides a horizon dropdown
and displays the results for the selected horizon.

### Rationale

Historical bootstrap was selected because it does not
assume normally distributed returns and preserves the
historical dependence structure between portfolio assets.
## Recommendation Engine

### Decision

No automated investment recommendation engine was added.

### Rationale

PortfolioIQ is designed primarily as a quantitative
risk assessment and portfolio analysis engine. The system
reports measurable risk characteristics, optimization
results, stress-test outcomes, and simulated distributions
rather than generating discretionary buy/sell recommendations.

This keeps the output evidence-based and avoids introducing
unsupported investment recommendations.

---

# 2. `docs/decision_log.md`

For this one, I recommend **preserving your existing decisions** and adding the following entries at the end.

Paste this at the bottom:

```md
---

## Decision: Multi-Horizon Monte Carlo Simulation

**Date:** 2026-08-19

### Decision

Monte Carlo simulation will calculate all supported investment
horizons on the backend:

- 1 Month — 21 trading days
- 3 Months — 63 trading days
- 6 Months — 126 trading days
- 1 Year — 252 trading days
- 2 Years — 504 trading days

The frontend will provide a horizon selector and display the
precomputed result corresponding to the selected horizon.

### Rationale

Calculating all horizons on the backend provides a consistent
simulation result set and prevents the frontend from repeatedly
requesting expensive simulations when the user changes the
selected horizon.

This also keeps quantitative simulation logic inside the backend
service layer.

### Consequence

The Monte Carlo API returns a collection of horizon-specific
results rather than a single simulation result.

---

## Decision: Historical Bootstrap Monte Carlo

**Date:** 2026-08-19

### Decision

PortfolioIQ uses historical bootstrap sampling as the initial
Monte Carlo methodology.

Complete historical daily return rows are sampled together
rather than sampling each asset independently.

### Rationale

Sampling complete historical rows preserves the observed
cross-asset relationship in the historical data.

This is more appropriate for portfolio-level simulation than
independently sampling each asset's historical returns.

### Consequence

The simulation remains dependent on the historical return
distribution and historical asset relationships.

---

## Decision: Monte Carlo Metrics

**Date:** 2026-08-19

### Decision

The backend calculates a comprehensive set of Monte Carlo
statistics, while the frontend may selectively display the
metrics that are most useful to the user.

The backend output includes:

- Mean return
- Median return
- Probability of loss
- Probability of loss greater than 10%
- Probability of loss greater than 20%
- Value at Risk
- Expected Shortfall
- 5th percentile
- 95th percentile
- Worst simulated return
- Best simulated return
- Distribution histogram

### Rationale

Keeping the full quantitative result in the backend allows
future frontend reporting and visualization features without
re-running the simulation.

The user interface should avoid unnecessary duplication and
should prioritize metrics that directly support portfolio
risk interpretation.

### Consequence

Backend and frontend responsibilities remain separated:
the backend produces quantitative results, while the frontend
controls presentation.

---

## Decision: Shared Frontend Navigation

**Date:** 2026-08-19

### Decision

Application navigation is implemented through a shared
Next.js `Navigation` component.

The component is reused across the primary application pages.

### Rationale

Previously, navigation structures were duplicated inside
individual pages.

Centralizing navigation:

- Reduces duplicated code
- Keeps routes consistent
- Makes future navigation changes easier
- Provides a consistent user experience

### Consequence

Individual pages no longer maintain their own primary
progress/navigation structure.

The navigation component is responsible for:

- Navigation labels
- Navigation order
- Application routes
- Active-page highlighting

---

## Decision: No Automated Investment Recommendation

**Date:** 2026-08-19

### Decision

PortfolioIQ will not provide an automated investment
recommendation based solely on Monte Carlo simulation results.

### Rationale

A recommendation such as "buy", "sell", or "increase allocation"
would require assumptions beyond the available simulation results,
including investor objectives, valuation, market conditions,
liquidity requirements, and other financial considerations.

Monte Carlo simulation is therefore treated as a quantitative
risk-analysis tool rather than an automated investment-advice
engine.

### Consequence

Monte Carlo results are presented as scenario and risk
information.

The system does not convert simulation outcomes directly into
investment recommendations.