from backend.portfolio.portfolio_service import PortfolioService
from backend.risk.risk_service import RiskService
from backend.risk.stress_scenarios import (
    BROAD_MARKET_DECLINE,
    SEVERE_MARKET_SHOCK,
    CONSUMER_SECTOR_SHOCK,
)


portfolio_service = PortfolioService()
risk_service = RiskService()

portfolio = portfolio_service.create_portfolio(
    {
        "JNJ": 0.30,
        "PG": 0.25,
        "KO": 0.20,
        "MCD": 0.15,
        "HD": 0.10,
    }
)

print()
print("Portfolio:")
print(portfolio)

print()
print("Stress Test Results")
print("-------------------")

broad_market_result = (
    risk_service.calculate_stress_test(
        portfolio,
        BROAD_MARKET_DECLINE,
    )
)

print(
    f"{BROAD_MARKET_DECLINE.name}: "
    f"{broad_market_result:.2%}"
)

severe_market_result = (
    risk_service.calculate_stress_test(
        portfolio,
        SEVERE_MARKET_SHOCK,
    )
)

print(
    f"{SEVERE_MARKET_SHOCK.name}: "
    f"{severe_market_result:.2%}"
)

consumer_sector_result = (
    risk_service.calculate_stress_test(
        portfolio,
        CONSUMER_SECTOR_SHOCK,
    )
)

print(
    f"{CONSUMER_SECTOR_SHOCK.name}: "
    f"{consumer_sector_result:.2%}"
)