"""
Risk Scoring Service

Converts quantitative risk metrics into an
investor-friendly overall risk score.
"""

from backend.core.logger import get_logger


class RiskScoringService:
    """
    Calculates an overall portfolio risk score.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

    def calculate_risk_score(
        self,
        annualized_volatility: float,
        maximum_drawdown: float,
        sharpe_ratio: float,
        historical_value_at_risk: float,
        expected_shortfall: float,
    ) -> float:
        """
        Calculate an overall risk score from 0 to 100.

        Higher score means higher portfolio risk.
        """

        self.logger.info(
            "Calculating overall portfolio risk score."
        )

        if annualized_volatility < 0:
            raise ValueError(
                "Annualized volatility cannot be negative."
            )

        if maximum_drawdown > 0:
            raise ValueError(
                "Maximum drawdown should be zero or negative."
            )

        if historical_value_at_risk > 0:
            raise ValueError(
                "Historical Value at Risk should be zero or negative."
            )

        if expected_shortfall > 0:
            raise ValueError(
                "Expected Shortfall should be zero or negative."
            )

        # Volatility component
        volatility_score = min(
            annualized_volatility / 0.50 * 100,
            100,
        )

        # Drawdown component
        drawdown_score = min(
            abs(maximum_drawdown) / 0.60 * 100,
            100,
        )

        # Value at Risk component
        value_at_risk_score = min(
            abs(historical_value_at_risk) / 0.10 * 100,
            100,
        )

        # Expected Shortfall component
        expected_shortfall_score = min(
            abs(expected_shortfall) / 0.15 * 100,
            100,
        )

        # Sharpe Ratio reduces the risk score when
        # historical risk-adjusted performance is stronger.
        if sharpe_ratio >= 2:
            sharpe_adjustment = -15
        elif sharpe_ratio >= 1:
            sharpe_adjustment = -8
        elif sharpe_ratio >= 0:
            sharpe_adjustment = 0
        else:
            sharpe_adjustment = 10

        risk_score = (
            volatility_score * 0.25
            + drawdown_score * 0.25
            + value_at_risk_score * 0.20
            + expected_shortfall_score * 0.20
            + 50 * 0.10
            + sharpe_adjustment
        )

        risk_score = max(
            0,
            min(risk_score, 100),
        )

        self.logger.info(
            f"Overall risk score: {risk_score:.2f}"
        )

        return float(risk_score)

    def classify_risk(
        self,
        risk_score: float,
    ) -> str:
        """
        Convert the numerical risk score into
        an investor-friendly risk category.
        """

        if not 0 <= risk_score <= 100:
            raise ValueError(
                "Risk score must be between 0 and 100."
            )

        if risk_score < 25:
            return "LOW"

        if risk_score < 50:
            return "MODERATE"

        if risk_score < 75:
            return "HIGH"

        return "VERY HIGH"