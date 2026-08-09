from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)
from backend.portfolio.portfolio_optimizer import (
    PortfolioOptimizer,
)
from backend.services.investor_assessment_service import (
    InvestorAssessmentService,
)
from backend.models.investor_profile import InvestorProfile


# --------------------------------------------------
# Investor Profile
# --------------------------------------------------

investor_profile = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)


# --------------------------------------------------
# Assets
# --------------------------------------------------

symbols = [
    "NFLX",
    "PEP",
    "WMT",
    "UNH",
    "DIS",
]


# --------------------------------------------------
# Retrieve market data
# --------------------------------------------------

data_service = PortfolioDataService()

price_data = data_service.get_price_data(
    symbols
)

prices = data_service.combine_price_data(
    price_data
)

asset_returns = data_service.calculate_returns(
    prices
)


# --------------------------------------------------
# Investor Assessment
# --------------------------------------------------

assessment_service = InvestorAssessmentService()


# --------------------------------------------------
# Constraint Feasibility
# --------------------------------------------------

feasibility = (
    assessment_service.check_constraint_feasibility(
        asset_returns=asset_returns,
        investor_profile=investor_profile,
        maximum_weight=0.30,
        target_volatility=0.20,
    )
)


# --------------------------------------------------
# Output
# --------------------------------------------------

print()
print("## Investor Constraint Feasibility")
print()

print(
    f"Maximum Acceptable Loss: "
    f"{feasibility['maximum_acceptable_loss']:.2%}"
)

if feasibility["target_volatility"] is not None:
    print(
        f"Target Volatility: "
        f"{feasibility['target_volatility']:.2%}"
    )

print()

if feasibility["best_drawdown"] is not None:
    print(
        f"Best Achievable Maximum Drawdown: "
        f"{feasibility['best_drawdown']:.2%}"
    )

print()

if feasibility["feasible"]:

    print("Status: FEASIBLE")

    print()
    print(
        "Investor constraints can be satisfied "
        "with the available assets."
    )

else:

    print("Status: NOT FEASIBLE")

    print()
    print(
        "Investor constraints cannot be satisfied "
        "with the available assets."
    )

    print()
    print("Suggested Actions:")

    print(
        "- Expand the asset universe."
    )

    print(
        "- Consider adding lower-risk assets."
    )

    print(
        "- Consider allocating part of the portfolio "
        "to cash or fixed-income assets."
    )