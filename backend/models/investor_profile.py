from dataclasses import dataclass


@dataclass
class InvestorProfile:
    """
    Represents an investor's risk preferences
    and investment objectives.
    """

    investment_amount: float
    investment_horizon_years: int
    risk_tolerance: str
    maximum_acceptable_loss: float
    investment_objective: str

    def __post_init__(self) -> None:

        if self.investment_amount <= 0:
            raise ValueError(
                "Investment amount must be greater than zero."
            )

        if self.investment_horizon_years <= 0:
            raise ValueError(
                "Investment horizon must be greater than zero."
            )

        allowed_risk_tolerances = {
            "LOW",
            "MODERATE",
            "HIGH",
        }

        if self.risk_tolerance not in allowed_risk_tolerances:
            raise ValueError(
                "Risk tolerance must be LOW, MODERATE, or HIGH."
            )

        if not 0 < self.maximum_acceptable_loss <= 1:
            raise ValueError(
                "Maximum acceptable loss must be between "
                "0 and 1."
            )

        if not self.investment_objective:
            raise ValueError(
                "Investment objective cannot be empty."
            )