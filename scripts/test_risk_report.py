from backend.portfolio.portfolio_service import PortfolioService
from backend.risk.risk_service import RiskService
from backend.services.risk_report_service import RiskReportService
from backend.models.investor_profile import InvestorProfile


# -----------------------------------------
# Create services
# -----------------------------------------

portfolio_service = PortfolioService()
risk_service = RiskService()
report_service = RiskReportService()


# -----------------------------------------
# Create portfolio
# -----------------------------------------

weights = {
    "NFLX": 0.30,
    "PEP": 0.25,
    "WMT": 0.20,
    "UNH": 0.15,
    "DIS": 0.10,
}

portfolio = portfolio_service.create_portfolio(
    weights
)


# -----------------------------------------
# Calculate portfolio returns
# -----------------------------------------

portfolio_returns = (
    portfolio_service.calculate_portfolio_returns(
        portfolio
    )
)


# -----------------------------------------
# Calculate risk metrics
# -----------------------------------------

annualized_volatility = (
    risk_service.calculate_volatility(
        portfolio_returns
    )
)

maximum_drawdown = (
    risk_service.calculate_maximum_drawdown(
        portfolio_returns
    )
)

sharpe_ratio = (
    risk_service.calculate_sharpe_ratio(
        portfolio_returns
    )
)

historical_value_at_risk = (
    risk_service.calculate_historical_value_at_risk(
        portfolio_returns
    )
)

expected_shortfall = (
    risk_service.calculate_expected_shortfall(
        portfolio_returns
    )
)


# -----------------------------------------
# Calculate asset returns
# -----------------------------------------

portfolio_data_service = (
    portfolio_service.portfolio_data_service
)

price_data = (
    portfolio_data_service.get_price_data(
        list(portfolio.weights.keys())
    )
)

combined_prices = (
    portfolio_data_service.combine_price_data(
        price_data
    )
)

asset_returns = (
    portfolio_data_service.calculate_returns(
        combined_prices
    )
)


# -----------------------------------------
# Risk contribution
# -----------------------------------------

risk_contribution_series = (
    risk_service.calculate_risk_contribution(
        asset_returns=asset_returns,
        weights=portfolio.weights,
    )
)

risk_contribution = (
    risk_contribution_series.to_dict()
)


# -----------------------------------------
# Investor profile
# -----------------------------------------

investor = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)


# -----------------------------------------
# Constraint feasibility
# -----------------------------------------

feasibility = (
    report_service
    .investor_assessment_service
    .check_constraint_feasibility(
        asset_returns=asset_returns,
        investor_profile=investor,
        maximum_weight=0.30,
        target_volatility=0.20,
    )
)


# -----------------------------------------
# Generate report
# -----------------------------------------

report = report_service.generate_report(
    portfolio_returns=portfolio_returns,
    investor=investor,
    annualized_volatility=annualized_volatility,
    maximum_drawdown=maximum_drawdown,
    sharpe_ratio=sharpe_ratio,
    historical_value_at_risk=(
        historical_value_at_risk
    ),
    expected_shortfall=(
        expected_shortfall
    ),
    risk_contribution=risk_contribution,
    feasibility=feasibility,
)


# -----------------------------------------
# Display report
# -----------------------------------------

print()
print("=" * 55)
print("        QUANTITATIVE RISK ASSESSMENT")
print("=" * 55)

print()
print("RISK METRICS")
print("-" * 55)

print(
    f"Annualized Volatility: "
    f"{report['risk_metrics']['annualized_volatility']:.2%}"
)

print(
    f"Maximum Drawdown: "
    f"{report['risk_metrics']['maximum_drawdown']:.2%}"
)

print(
    f"Sharpe Ratio: "
    f"{report['risk_metrics']['sharpe_ratio']:.4f}"
)

print(
    f"Historical VaR (95%): "
    f"{report['risk_metrics']['historical_value_at_risk']:.2%}"
)

print(
    f"Expected Shortfall (95%): "
    f"{report['risk_metrics']['expected_shortfall']:.2%}"
)


print()
print("RISK ASSESSMENT")
print("-" * 55)

print(
    f"Risk Score: "
    f"{report['risk_assessment']['risk_score']:.2f}/100"
)

print(
    f"Risk Level: "
    f"{report['risk_assessment']['risk_level']}"
)


print()
print("INVESTOR")
print("-" * 55)

assessment = report["investor_assessment"]

print(
    f"Risk Tolerance: "
    f"{assessment['risk_tolerance']}"
)

print(
    f"Maximum Acceptable Loss: "
    f"{assessment['maximum_acceptable_loss']:.2%}"
)

print(
    f"Investment Horizon: "
    f"{assessment['investment_horizon_years']} years"
)


print()
print("CONSTRAINT FEASIBILITY")
print("-" * 55)

feasibility_report = (
    report["constraint_feasibility"]
)

print(
    f"Status: "
    f"{'FEASIBLE' if feasibility_report['feasible'] else 'NOT FEASIBLE'}"
)

if feasibility_report["best_drawdown"] is not None:
    print(
        f"Best Achievable Drawdown: "
        f"{feasibility_report['best_drawdown']:.2%}"
    )


print()
print("INVESTOR COMPATIBILITY")
print("-" * 55)

print(
    f"Recommendation: "
    f"{assessment['recommendation']}"
)

print()
print("Assessment Reasons:")

for reason in assessment["reasons"]:
    print(f"- {reason}")


print()
print("RECOMMENDED ACTIONS")
print("-" * 55)

for recommendation in report["recommendations"]:
    print(f"- {recommendation}")


print()
print("=" * 55)