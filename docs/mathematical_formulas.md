# PortfolioIQ — Mathematical Formulas

## Purpose and conventions

This document records the quantitative calculations implemented in PortfolioIQ as of this repository version. Every entry is tied to the file that implements it; it intentionally does not describe formulas that are not present in the source code.

Unless stated otherwise, returns are decimals (for example, `0.05` means 5%), asset weights are long-only, and PortfolioIQ uses \(D = 252\) trading days per year (`backend/constants/financial_constants.py`). Historical Value at Risk and Expected Shortfall are returned as lower-tail **returns** (normally negative), not as positive loss magnitudes.

---

## 1. Prices, positions, and returns

### 1.1 Daily asset return

**Formula:** \(r_{i,t}=P_{i,t}/P_{i,t-1}-1\)

**Definition:** Percentage change in an asset's closing price between two trading days.

**Implementation:** `backend/portfolio/portfolio_data_service.py` (`calculate_returns`).

**Project use:** Converts combined closing-price data into the daily asset-return table used by portfolio analysis, risk calculations, optimization, and simulation.

### 1.2 Weight from monetary allocation

**Formula:** \(w_i=A_i/\sum_{j=1}^{n}A_j\)

**Definition:** The allocation to asset \(i\) divided by the total invested amount.

**Implementation:** `backend/portfolio/portfolio_service.py` (`create_portfolio_from_amounts`).

**Project use:** Converts an investor's currency allocations into normalized portfolio weights.

### 1.3 Position value and weight from shares

**Formula:** \(X_i=q_iP_i,\quad w_i=X_i/\sum_{j=1}^{n}X_j\)

**Definition:** A position value is shares multiplied by the current market price; its portfolio weight is its share of total market value.

**Implementation:** `backend/portfolio/portfolio_service.py` (`create_portfolio_from_shares`).

**Project use:** Builds a portfolio from existing share holdings using current prices.

### 1.4 Portfolio daily return

**Formula:** \(r_{p,t}=\sum_{i=1}^{n}w_ir_{i,t}\)

**Definition:** Weighted sum of the selected assets' daily returns.

**Implementation:** `backend/portfolio/portfolio_data_service.py` (`calculate_portfolio_returns`); also used in `backend/services/portfolio_comparison_service.py`, `backend/portfolio/portfolio_optimizer.py`, and `backend/services/monte_carlo_service.py`.

**Project use:** Produces the return series on which risk metrics and before/after optimization comparisons are based.

### 1.5 Fully invested portfolio constraint

**Formula:** \(\sum_{i=1}^{n}w_i=1\)

**Definition:** All asset allocations add to 100% of the portfolio.

**Implementation:** `backend/portfolio/portfolio_service.py`, `backend/portfolio/portfolio_optimizer.py`, `backend/services/monte_carlo_service.py`, and `backend/api/stress_test_routes.py`.

**Project use:** Validates portfolio inputs and is an equality constraint in each optimizer.

---

## 2. Historical risk metrics

### 2.1 Sample daily volatility and annualized volatility

**Formula:**

\[
\sigma_{daily}=\sqrt{\frac{1}{T-1}\sum_{t=1}^{T}(r_{p,t}-\bar r_p)^2},\qquad
\sigma_{annual}=\sigma_{daily}\sqrt{252}
\]

**Definition:** Sample standard deviation measures daily return dispersion; annualization scales it using 252 trading days.

**Implementation:** `backend/risk/risk_service.py` (`calculate_volatility`). The same annualization is applied to path returns in `backend/portfolio/portfolio_optimizer.py` for the CVaR volatility constraint.

**Project use:** Main portfolio-risk metric, optimizer constraint, risk-score input, and before/after comparison metric.

### 2.2 Annual risk-free rate converted to daily rate

**Formula:** \(r_{f,daily}=(1+r_{f,annual})^{1/252}-1\)

**Definition:** Converts the annual risk-free rate into a daily compounded equivalent.

**Implementation:** `backend/risk/risk_service.py` (`calculate_sharpe_ratio`).

**Project use:** Subtracted from daily portfolio returns before calculating the Sharpe ratio.

### 2.3 Annualized Sharpe ratio

**Formula:** \(S=\operatorname{mean}(r_{p,t}-r_{f,daily})/\sigma_{daily}\times\sqrt{252}\)

**Definition:** Historical excess return earned per unit of daily volatility, annualized.

**Implementation:** `backend/risk/risk_service.py` (`calculate_sharpe_ratio`).

**Project use:** Risk-adjusted performance metric and an adjustment in the PortfolioIQ risk score.

### 2.4 Cumulative value, drawdown, and maximum drawdown

**Formula:**

\[
V_t=\prod_{k=1}^{t}(1+r_{p,k}),\quad Peak_t=\max_{k\le t}V_k,\quad
DD_t=\frac{V_t-Peak_t}{Peak_t},\quad MDD=\min_t DD_t
\]

**Definition:** Compounds historical returns into a value index, measures each decline from the running peak, and selects the deepest decline.

**Implementation:** `backend/risk/risk_service.py` (`calculate_maximum_drawdown`); also implemented in `backend/portfolio/portfolio_optimizer.py` (`check_feasibility`).

**Project use:** Downside-risk metric, risk-score input, investor suitability check, and feasibility-search objective.

### 2.5 Historical Value at Risk (VaR)

**Formula:** \(VaR_c=Q_{1-c}(r_p)\)

**Definition:** Lower-tail historical return quantile at confidence level \(c\). For example, the 95% VaR is the 5th percentile. PortfolioIQ retains its usual negative-return sign.

**Implementation:** `backend/risk/risk_service.py` (`calculate_historical_value_at_risk`).

**Project use:** Historical tail-risk measure and risk-score input.

### 2.6 Historical Expected Shortfall (ES)

**Formula:** \(ES_c=\operatorname{mean}(r_{p,t}\mid r_{p,t}\le VaR_c)\)

**Definition:** Average historical return in outcomes at or below the VaR threshold. It is normally negative in this application.

**Implementation:** `backend/risk/risk_service.py` (`calculate_expected_shortfall`).

**Project use:** Measures tail severity beyond VaR and feeds the risk score and portfolio comparison.

### 2.7 Variance-based asset risk contribution

**Formula:**

\[
\Sigma=\operatorname{Cov}(r),\quad \sigma_p^2=w^T\Sigma w,\quad
MC=w\odot(\Sigma w),\quad RC=MC/\sigma_p^2
\]

**Definition:** \(MC\) is each asset's component contribution to portfolio variance; \(RC\) divides it by total portfolio variance, yielding proportional contributions that sum to approximately 1.

**Implementation:** `backend/risk/risk_service.py` (`calculate_risk_contribution`). A matching calculation appears in `backend/portfolio/portfolio_optimizer.py` for risk parity.

**Project use:** Attributes total portfolio variance across assets and supports concentration-related recommendations.

---

## 3. PortfolioIQ risk score

### 3.1 Capped metric components

**Formula:**

\[
V=\min(100,100\sigma_{annual}/0.50),\quad D=\min(100,100|MDD|/0.60)
\]
\[
Q=\min(100,100|VaR|/0.10),\quad E=\min(100,100|ES|/0.15)
\]

**Definition:** Normalizes volatility, drawdown, VaR, and Expected Shortfall into capped 0–100 component scores using the application thresholds.

**Implementation:** `backend/risk/risk_scoring_service.py` (`calculate_risk_score`); duplicated for comparisons in `backend/services/portfolio_comparison_service.py`.

**Project use:** Inputs to the investor-friendly risk score.

### 3.2 Sharpe adjustment

**Formula:**

\[
A(S)=\begin{cases}-15&S\ge2\\-8&1\le S<2\\0&0\le S<1\\10&S<0\end{cases}
\]

**Definition:** Better historical Sharpe ratios reduce the risk score, while a negative ratio increases it.

**Implementation:** `backend/risk/risk_scoring_service.py` and `backend/services/portfolio_comparison_service.py`.

**Project use:** Adjusts the score for risk-adjusted performance.

### 3.3 Overall risk score and classification

**Formula:** \(Score=\operatorname{clip}_{[0,100]}(0.25V+0.25D+0.20Q+0.20E+5+A(S))\)

**Definition:** Weighted, bounded score from 0 to 100. The `+5` is the implemented baseline term (equivalent to \(50\times0.10\)).

**Implementation:** `backend/risk/risk_scoring_service.py` (`calculate_risk_score`, `classify_risk`); replicated in `backend/services/portfolio_comparison_service.py`.

**Project use:** Produces the overall risk score and the labels `LOW` (<25), `MODERATE` (<50), `HIGH` (<75), and `VERY HIGH` (otherwise).

---

## 4. Portfolio optimization and feasibility

### 4.1 Annual covariance, portfolio variance, and volatility

**Formula:** \(\Sigma_{annual}=252\operatorname{Cov}(r),\quad \sigma_p^2=w^T\Sigma_{annual}w,\quad \sigma_p=\sqrt{\sigma_p^2}\)

**Definition:** Covariance captures joint daily asset movements and is annualized before the optimizer evaluates portfolio variance and volatility.

**Implementation:** `backend/portfolio/portfolio_optimizer.py` (`optimize`, `_minimum_variance`, `_risk_parity`, `check_feasibility`). `optimize` adds \(10^{-8}I\) to the covariance matrix for numerical stability.

**Project use:** Central risk model for minimum-variance, risk-parity, and feasibility calculations.

### 4.2 Long-only allocation and optional volatility constraints

**Formula:** \(\sum_iw_i=1,\quad0\le w_i\le w_{max},\quad\sigma_p\le\sigma_{target}\) (when supplied).

**Definition:** Requires a fully invested, non-negative portfolio, caps every asset allocation, and can impose an annualized volatility ceiling.

**Implementation:** `backend/portfolio/portfolio_optimizer.py`.

**Project use:** Feasibility and risk controls applied to all three optimization methods.

### 4.3 Minimum-variance optimization

**Formula:** \(\min_w\ w^T\Sigma_{annual}w\), subject to section 4.2 constraints.

**Definition:** Finds the valid portfolio with the lowest modeled annual variance.

**Implementation:** `backend/portfolio/portfolio_optimizer.py` (`_minimum_variance`).

**Project use:** Provides the `MINIMUM_VARIANCE` optimization method.

### 4.4 Risk-parity optimization

**Formula:** \(RC_i=w_i(\Sigma_{annual}w)_i/(w^T\Sigma_{annual}w)\), then \(\min_w\sum_i(RC_i-1/n)^2\).

**Definition:** Minimizes the squared distance between each asset's proportional variance contribution and equal risk contribution.

**Implementation:** `backend/portfolio/portfolio_optimizer.py` (`_risk_parity`).

**Project use:** Provides the `RISK_PARITY` optimization method.

### 4.5 CVaR optimization (Rockafellar–Uryasev)

**Formula:**

\[
r_{p,t}=r_t^Tw,\quad L_t=-r_{p,t},\quad
\min_{w,\alpha}\ \alpha+\frac{1}{1-\beta}\frac1T\sum_{t=1}^{T}\max(L_t-\alpha,0),\quad\beta=0.95
\]

subject to section 4.2 constraints. \(\alpha\) is the auxiliary VaR-loss threshold.

**Definition:** Minimizes the estimated average loss in the worst 5% of historical daily portfolio outcomes.

**Implementation:** `backend/portfolio/portfolio_optimizer.py` (`_cvar`).

**Project use:** Provides the `CVAR` optimization method for tail-loss-aware allocation.

### 4.6 Feasibility objective and investor loss rule

**Formula:** \(\min_w|MDD(w)|\); feasible when \(MDD(w)\ge-|L_{max}|\).

**Definition:** Searches for the valid allocation with the shallowest historical maximum drawdown, then checks it against the investor's maximum acceptable loss.

**Implementation:** `backend/portfolio/portfolio_optimizer.py` (`check_feasibility`); invoked by `backend/services/investor_assessment_service.py`.

**Project use:** Determines whether the available asset universe can meet the investor's drawdown requirement and optional volatility target.

---

## 5. Stress testing

### 5.1 Hypothetical stress impact and asset contribution

**Formula:** \(Impact=\sum_iw_is_i,\quad Contribution_i=w_is_i\)

**Definition:** Applies a scenario shock \(s_i\) to every asset and adds its weighted contribution.

**Implementation:** `backend/risk/risk_service.py` (`calculate_stress_test`) and `backend/api/stress_test_routes.py`.

**Project use:** Calculates results for predefined and custom hypothetical stress scenarios.

### 5.2 Value after stress and required recovery

**Formula:** \(V_{after}=1+Impact,\quad Recovery=1/(1+Impact)-1\)

**Definition:** Uses a normalized starting value of 1. Recovery gives the gain needed to return to the starting value after the scenario loss; it is unavailable when the value is zero or below.

**Implementation:** `backend/api/stress_test_routes.py`; recovery is also implemented in `backend/services/historical_stress_service.py` (`calculate_recovery_required`).

**Project use:** Displays remaining portfolio value and the percentage gain needed to recover from a stress event.

### 5.3 Historical scenario asset return and portfolio impact

**Formula:** \(R_i^{scenario}=P_{i,end}/P_{i,start}-1,\quad Impact=\sum_iw_iR_i^{scenario}\)

**Definition:** Calculates each asset's return over a selected historical event, then weights those returns by the current portfolio.

**Implementation:** `backend/services/historical_stress_service.py` (`calculate_asset_returns`, `calculate_portfolio_impact`); used by `backend/api/stress_test_routes.py`.

**Project use:** Evaluates the current portfolio against `COVID_CRASH` and `2022_BEAR_MARKET`.

---

## 6. Historical-bootstrap Monte Carlo simulation

### 6.1 Bootstrap sampling of complete historical rows

**Formula:** \(\tilde r_{s,h}=r_{I_{s,h}},\quad I_{s,h}\sim\operatorname{Uniform}\{1,\ldots,T\}\).

**Definition:** For each simulation and horizon day, PortfolioIQ samples one complete historical cross-asset return row with replacement. Sampling whole rows preserves observed cross-asset relationships.

**Implementation:** `backend/services/monte_carlo_service.py` (`simulate`).

**Project use:** Creates future daily-return scenarios without assuming a parametric distribution.

### 6.2 Simulated portfolio return and terminal return

**Formula:** \(\tilde r_{p,s,h}=\sum_iw_i\tilde r_{i,s,h},\quad V_{T,s}=\prod_{h=1}^{H}(1+\tilde r_{p,s,h}),\quad R_{T,s}=V_{T,s}-1\).

**Definition:** Converts sampled asset-return rows into portfolio returns, compounds them across the selected horizon, and reports terminal return.

**Implementation:** `backend/services/monte_carlo_service.py` (`simulate`).

**Project use:** Produces the terminal-return distribution for 1M, 3M, 6M, 1Y, and 2Y horizons.

### 6.3 Monte Carlo summary statistics and loss probabilities

**Formula:** \(\bar R=S^{-1}\sum_sR_{T,s},\quad P(R_T<a)=S^{-1}\sum_s\mathbf1\{R_{T,s}<a\}\).

**Definition:** The simulation reports mean and median terminal return. Probability of loss uses \(a=0\); 10% and 20% loss measures use \(-0.10\) and \(-0.20\). It also reports the 5th and 95th percentiles, minimum, maximum, and a 40-bin histogram.

**Implementation:** `backend/services/monte_carlo_service.py` (`simulate`).

**Project use:** Summarizes likely, downside, best, and worst simulated outcomes.

### 6.4 Monte Carlo VaR and Expected Shortfall

**Formula:** \(VaR_c^{MC}=Q_{1-c}(R_T),\quad ES_c^{MC}=\operatorname{mean}(R_T\mid R_T\le VaR_c^{MC})\).

**Definition:** Calculates lower-tail terminal-return VaR and the average terminal return in that tail. Returned values retain their return signs.

**Implementation:** `backend/services/monte_carlo_service.py` (`simulate`).

**Project use:** Reports forward-looking simulated tail risk at the supplied confidence level (95% by default).

---

## Implementation reference

| Area | Primary implementation file |
| --- | --- |
| Price and portfolio returns | `backend/portfolio/portfolio_data_service.py` |
| Portfolio construction from allocations or shares | `backend/portfolio/portfolio_service.py` |
| Historical risk metrics and risk contributions | `backend/risk/risk_service.py` |
| Risk score and classification | `backend/risk/risk_scoring_service.py` |
| Optimization and feasibility | `backend/portfolio/portfolio_optimizer.py` |
| Hypothetical stress testing | `backend/api/stress_test_routes.py`, `backend/risk/risk_service.py` |
| Historical stress testing | `backend/services/historical_stress_service.py` |
| Monte Carlo simulation | `backend/services/monte_carlo_service.py` |
| Original-versus-optimized comparison | `backend/services/portfolio_comparison_service.py` |
