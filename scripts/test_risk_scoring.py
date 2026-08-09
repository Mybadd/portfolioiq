from backend.risk.risk_scoring_service import (
    RiskScoringService,
)


risk_scoring_service = RiskScoringService()

risk_score = (
    risk_scoring_service.calculate_risk_score(
        annualized_volatility=0.272049,
        maximum_drawdown=-0.481057,
        sharpe_ratio=0.853070,
        historical_value_at_risk=-0.027606,
        expected_shortfall=-0.0397,
    )
)

risk_level = (
    risk_scoring_service.classify_risk(
        risk_score
    )
)

print()
print("Portfolio Risk Assessment")
print("--------------------------")

print(
    f"Risk Score: "
    f"{risk_score:.2f}/100"
)

print(
    f"Risk Level: "
    f"{risk_level}"
)