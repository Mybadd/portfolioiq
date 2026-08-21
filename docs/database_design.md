# PortfolioIQ — Database Design

# 1. Purpose

PortfolioIQ uses a relational database to persist investor, portfolio,
market-data, risk-analysis, optimization, stress-testing, and reporting
information.

The database provides persistent storage for information that should
survive browser sessions and application restarts.

The database is separate from the quantitative calculation layer.

The application services perform calculations, while PostgreSQL stores
the inputs, outputs, and relevant historical records.

---

# 2. Database Technology

## Database

**PostgreSQL**

PostgreSQL is used as the primary relational database for PortfolioIQ.

### Why PostgreSQL?

PostgreSQL provides:

- Relational data modeling
- Strong consistency
- ACID transactions
- Foreign-key constraints
- Numeric data types suitable for financial calculations
- Efficient indexing
- JSON/JSONB support where flexible structures are required
- Compatibility with Python database libraries
- Good support for containerized deployment with Docker

---

# 3. High-Level Database Architecture

```text
                         PortfolioIQ
                              |
                              v
                       Backend API Layer
                              |
                              v
                     Application Services
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        PortfolioService   RiskService   OptimizationService
              |               |               |
              +---------------+---------------+
                              |
                              v
                     PostgreSQL Database
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
    Investors             Portfolios          Market Data
        |                     |                     |
        v                     v                     v
 Risk Assessments       Portfolio Assets      Price History
        |
        +---------------------+
        |
        v
   Analysis Results
        |
   +----+---------+-------------+
   |              |             |
   v              v             v
Risk Results   Optimization   Stress Tests
                  Results
        |
        v
      Reports

---

# 4. Core Entities

The primary entities are Investor, Portfolio, Asset, Portfolio Asset, Market
Price, Risk Analysis, Optimization Run, Stress Test, Monte Carlo Run, and
Report.

```text
Investor -> Portfolio -> Portfolio Asset -> Asset -> Market Price
                  |-> analyses, optimization runs, stress tests, simulations, reports
```

Market data is stored independently from investor-owned portfolios and is
referenced by assets.

---

# 5. Entity Relationship Overview

```text
investors 1---N portfolios 1---N portfolio_assets N---1 assets 1---N market_prices
                         1---N risk_analyses
                         1---N optimization_runs
                         1---N stress_tests
                         1---N monte_carlo_runs
                         1---N reports
```

Detail tables belong to their run headers and have no independent meaning.

---

# 6. Investors

Stores the profile required to own portfolios and apply investor-specific
policy.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| name | VARCHAR(150) | Investor name |
| email | VARCHAR(320) | Optional unique contact address |
| risk_profile | VARCHAR(30) | Conservative, moderate, or aggressive |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Last modification time |

`email` is unique when present; `risk_profile` is constrained to approved
application values.

---

# 7. Assets

`assets` is the security master. One row represents a tradable instrument or
supported benchmark, rather than an investor position.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| symbol | VARCHAR(32) | Unique canonical ticker or identifier |
| name | VARCHAR(255) | Display name |
| asset_class | VARCHAR(50) | Equity, bond, ETF, cash, commodity, or other |
| currency | CHAR(3) | ISO 4217 quote currency |
| exchange | VARCHAR(100) | Listing venue, if applicable |
| is_active | BOOLEAN | Whether new positions may use the asset |
| created_at | TIMESTAMPTZ | Creation time |

---

# 8. Portfolios

`portfolios` represents an investor-owned collection of positions.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| investor_id | BIGINT | References investors(id) |
| name | VARCHAR(150) | Portfolio name within an investor |
| base_currency | CHAR(3) | Reporting currency |
| benchmark_symbol | VARCHAR(32) | Optional benchmark identifier |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Last modification time |

`(investor_id, name)` is unique.

---

# 9. Portfolio Assets

`portfolio_assets` records a position or target allocation in a portfolio.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| asset_id | BIGINT | References assets(id) |
| quantity | NUMERIC(24,8) | Units held |
| average_cost | NUMERIC(20,6) | Optional cost per unit |
| target_weight | NUMERIC(9,6) | Optional target allocation from 0 to 1 |
| acquired_at | DATE | Optional acquisition date |
| updated_at | TIMESTAMPTZ | Last modification time |

`(portfolio_id, asset_id)` is unique. Derived market value is calculated from
the latest valid price.

---

# 10. Market Prices

`market_prices` stores adjusted end-of-period observations for valuation and
returns calculations.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| asset_id | BIGINT | References assets(id) |
| price_date | DATE | Trading date |
| open_price | NUMERIC(20,6) | Optional open |
| high_price | NUMERIC(20,6) | Optional high |
| low_price | NUMERIC(20,6) | Optional low |
| close_price | NUMERIC(20,6) | Closing price |
| adjusted_close | NUMERIC(20,6) | Split/dividend-adjusted close |
| volume | BIGINT | Optional reported volume |
| source | VARCHAR(100) | Market-data provider |
| ingested_at | TIMESTAMPTZ | Ingestion time |

`(asset_id, price_date, source)` is unique. Provider precedence determines the
series selected by calculations.

---

# 11. Risk Analyses

`risk_analyses` is the immutable header for a completed portfolio-risk run.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| as_of_date | DATE | Valuation date |
| lookback_days | INTEGER | Return-history window |
| confidence_level | NUMERIC(5,4) | VaR confidence level |
| method | VARCHAR(50) | Historical, parametric, or simulation |
| parameters | JSONB | Reproducibility inputs |
| total_value | NUMERIC(20,6) | Valued portfolio amount |
| var_value | NUMERIC(20,6) | Value at Risk |
| cvar_value | NUMERIC(20,6) | Conditional VaR |
| volatility | NUMERIC(12,8) | Annualized volatility |
| created_at | TIMESTAMPTZ | Completion time |

---

# 12. Risk Contributions

`risk_contributions` stores per-asset results for a risk analysis.

| Column | Type | Description |
|---|---|---|
| risk_analysis_id | BIGINT | References risk_analyses(id) |
| asset_id | BIGINT | References assets(id) |
| portfolio_weight | NUMERIC(9,6) | Weight used in the run |
| marginal_var | NUMERIC(20,6) | Marginal VaR |
| component_var | NUMERIC(20,6) | Component VaR |
| contribution_pct | NUMERIC(9,6) | Share of total risk |

Primary key: `(risk_analysis_id, asset_id)`.

---

# 13. Optimization Runs

`optimization_runs` records an allocation-optimization request and outcome.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| objective | VARCHAR(50) | Minimum variance, max Sharpe, or target return |
| constraints | JSONB | Bounds and policy constraints |
| expected_return | NUMERIC(12,8) | Resulting expected return |
| volatility | NUMERIC(12,8) | Resulting expected volatility |
| sharpe_ratio | NUMERIC(12,8) | Resulting Sharpe ratio |
| status | VARCHAR(30) | Succeeded, failed, or infeasible |
| created_at | TIMESTAMPTZ | Completion time |

---

# 14. Optimization Weights

`optimization_weights` holds the recommended weight for each included asset.

| Column | Type | Description |
|---|---|---|
| optimization_run_id | BIGINT | References optimization_runs(id) |
| asset_id | BIGINT | References assets(id) |
| weight | NUMERIC(9,6) | Recommended allocation from 0 to 1 |

Primary key: `(optimization_run_id, asset_id)`. Validation ensures weights sum
to one within a calculation tolerance.

---

# 15. Stress Tests

`stress_tests` records a named scenario applied to a portfolio snapshot.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| name | VARCHAR(150) | Scenario name |
| as_of_date | DATE | Valuation date |
| scenario_type | VARCHAR(50) | Historical, factor, or custom |
| total_value_before | NUMERIC(20,6) | Pre-shock value |
| total_value_after | NUMERIC(20,6) | Post-shock value |
| pnl | NUMERIC(20,6) | Scenario profit/loss |
| created_at | TIMESTAMPTZ | Completion time |

---

# 16. Stress Test Asset Shocks

`stress_test_asset_shocks` records the shock and resulting value for each asset.

| Column | Type | Description |
|---|---|---|
| stress_test_id | BIGINT | References stress_tests(id) |
| asset_id | BIGINT | References assets(id) |
| shock_pct | NUMERIC(9,6) | Relative price shock |
| value_before | NUMERIC(20,6) | Value before shock |
| value_after | NUMERIC(20,6) | Value after shock |
| pnl | NUMERIC(20,6) | Asset profit/loss |

Primary key: `(stress_test_id, asset_id)`.

---

# 17. Monte Carlo Runs

`monte_carlo_runs` persists simulation configuration and summary metadata.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| as_of_date | DATE | Starting valuation date |
| horizon_days | INTEGER | Forecast horizon |
| simulations | INTEGER | Number of paths |
| random_seed | BIGINT | Optional reproducibility seed |
| assumptions | JSONB | Distribution and correlation assumptions |
| created_at | TIMESTAMPTZ | Completion time |

---

# 18. Monte Carlo Results

`monte_carlo_results` stores compact distribution outputs instead of all paths.

| Column | Type | Description |
|---|---|---|
| monte_carlo_run_id | BIGINT | References monte_carlo_runs(id) |
| percentile | NUMERIC(6,3) | Distribution percentile |
| portfolio_value | NUMERIC(20,6) | Simulated value at percentile |
| return_pct | NUMERIC(12,8) | Simulated return at percentile |

Primary key: `(monte_carlo_run_id, percentile)`. Full paths, when needed, are
stored in object storage with a durable reference.

---

# 19. Reports

`reports` tracks generated user-facing artifacts.

| Column | Type | Description |
|---|---|---|
| id | BIGSERIAL | Primary key |
| portfolio_id | BIGINT | References portfolios(id) |
| report_type | VARCHAR(50) | Risk, optimization, stress, or summary |
| format | VARCHAR(20) | PDF, HTML, or CSV |
| storage_uri | TEXT | Object-storage location |
| checksum | VARCHAR(128) | Content integrity value |
| generated_at | TIMESTAMPTZ | Generation time |
| expires_at | TIMESTAMPTZ | Optional retention cutoff |

---

# 20. Database Relationships

All ownership relationships use foreign keys. An investor owns portfolios; a
portfolio owns positions and analysis runs; assets are shared reference data.
Run-detail records are deleted with their parent run. Assets with historical
prices or positions are deactivated rather than deleted.

---

# 21. Data Integrity

Constraints enforce non-null ownership, unique natural keys, valid currency
codes, non-negative prices where applicable, and sensible numeric ranges.
Application validation additionally checks business policy, market-calendar
availability, and analysis-input completeness. Each analysis stores its as-of
date, method, and parameters for reproducibility.

---

# 22. Indexing Strategy

- `portfolios(investor_id)` for portfolio lookup.
- `portfolio_assets(portfolio_id)` for valuation and holdings reads.
- `market_prices(asset_id, price_date DESC)` for price-history reads.
- Each analysis header's `portfolio_id, created_at DESC` for history views.
- Foreign-key columns in run-detail tables.

Unique constraints supply indexes for symbols and compound identity keys.
Additional indexes should be introduced only after query profiling.

---

# 23. Transaction Strategy

Portfolio changes use short transactions so a position update and its audit
metadata succeed or fail together. A completed analysis header and detail rows
are inserted in one transaction. Long-running calculations occur outside a
transaction; their final persistence operation is short and atomic.

Market-data ingestion is batched and idempotent through its unique price key.

---

# 24. Persistence vs Calculation

The database persists source data, user inputs, run configuration, summaries,
and material breakdowns. It does not persist transient matrices, intermediate
optimizer state, or all simulation paths by default. Such data is recomputed
from stored inputs or retained externally when audit requirements require it.

---

# 25. PostgreSQL and Backend Architecture

The backend owns all database access. API clients never receive direct database
credentials. Repository or service layers map validated application models to
transactions, and migrations are the sole mechanism for production schema
changes. Connection pooling, statement timeouts, and read-only reporting roles
should be configured as deployment matures.

---

# 26. Docker Deployment

For local development, PostgreSQL will run as a Docker Compose service with a
named volume for data. The API receives a connection URL through environment
configuration. Production uses managed PostgreSQL or an equivalently backed-up
container deployment; containers must not contain the sole copy of data.

---

# 27. Environment Configuration

Configuration is supplied through environment variables, including
`DATABASE_URL`, pool size, connection timeout, and optional SSL mode. Secrets
are never committed. Sample environment files contain placeholders only, while
production values come from the deployment secret manager.

---

# 28. Database Migrations

Each schema change is an ordered, reviewed migration containing structural
changes and required data backfills. Migrations run once per environment before
application rollout. Destructive changes use an expand/migrate/contract
sequence so rolling deployments remain compatible.

---

# 29. Security Considerations

Database roles follow least privilege: the runtime role can access only the
application schema, while migration privileges are separated. TLS is required
for remote connections. Sensitive investor data is minimized, protected by
access controls, and excluded from logs and exported reports unless required.

Parameterized queries and ORM binding prevent SQL injection. Backups are
encrypted and tested for restoration.

---

# 30. Scalability Considerations

Market prices are expected to grow fastest. Their compound index is the initial
scaling measure; PostgreSQL range partitioning by date may be introduced once
volume justifies it. Completed run details can be retained by policy, archived,
or exported to cheaper storage. Read replicas may serve reporting views without
changing ownership or transaction semantics.

---

# 31. Current Implementation Status

This is a target design. PostgreSQL schemas, migrations, containers, ORM models,
and database-backed services are intentionally not implemented yet. Current
application calculations may remain in-memory or file-backed until a separate
implementation task authorizes persistence work.

---

# 32. Design Principles

- Preserve reproducibility by storing analysis inputs and versioned assumptions.
- Keep reference data normalized and portfolio ownership explicit.
- Use constraints for invariants the database can enforce.
- Keep numerical calculation state out of transactional storage unless valuable.
- Evolve safely through migrations, observability, backups, and least privilege.

---

# 33. Summary

PortfolioIQ's proposed database model separates shared market reference data
from investor-owned portfolios and immutable analytical results. It provides a
clear PostgreSQL-ready foundation for later implementation while keeping the
current scope limited to complete design documentation.
