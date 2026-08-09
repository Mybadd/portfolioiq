"""
Investor Assessment Service

Compares portfolio risk with an investor's
risk tolerance, investment horizon, and
maximum acceptable loss.
"""

from backend.core.logger import get_logger
from backend.models.investor_profile import InvestorProfile
from backend.portfolio.portfolio_optimizer import PortfolioOptimizer


class InvestorAssessmentService:

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__    
        )
        self.portfolio_optimizer = PortfolioOptimizer()
    def assess_compatibility(
        self,
        investor: InvestorProfile,
        risk_score: float,
        maximum_drawdown: float,
    ) -> dict:
        """
        Assess whether portfolio risk is compatible
        with the investor profile.
        """

        self.logger.info(
            "Assessing portfolio-investor compatibility."
        )

        if not 0 <= risk_score <= 100:
            raise ValueError(
                "Risk score must be between 0 and 100."
            )

        if maximum_drawdown > 0:
            raise ValueError(
                "Maximum drawdown must be zero or negative."
            )

        investor_risk_limits = {
            "LOW": (0, 40),
            "MODERATE": (25, 65),
            "HIGH": (50, 100),
        }

        min_score, max_score = investor_risk_limits[
            investor.risk_tolerance
        ]

        score_compatible = (
            min_score <= risk_score <= max_score
        )

        drawdown_compatible = (
            abs(maximum_drawdown)
            <= investor.maximum_acceptable_loss
        )

        horizon_supports_risk = (
            investor.investment_horizon_years >= 5
            or risk_score <= 50
        )

        if (
            score_compatible
            and drawdown_compatible
            and horizon_supports_risk
        ):
            recommendation = "SUITABLE"

        elif (
            score_compatible
            or drawdown_compatible
        ):
            recommendation = "REVIEW"

        else:
            recommendation = "NOT SUITABLE"

        reasons = []

        if not score_compatible:
            reasons.append(
                "Portfolio risk score does not match "
                "the investor's risk tolerance."
            )

        if not drawdown_compatible:
            reasons.append(
                "Historical maximum drawdown exceeds "
                "the investor's maximum acceptable loss."
            )

        if not horizon_supports_risk:
            reasons.append(
                "Investment horizon may be too short "
                "for the portfolio's risk level."
            )

        if not reasons:
            reasons.append(
                "Portfolio risk characteristics are "
                "consistent with the investor profile."
            )

        result = {
            "recommendation": recommendation,
            "risk_score": risk_score,
            "risk_tolerance": investor.risk_tolerance,
            "maximum_drawdown": maximum_drawdown,
            "maximum_acceptable_loss": (
                investor.maximum_acceptable_loss
            ),
            "investment_horizon_years": (
                investor.investment_horizon_years
            ),
            "reasons": reasons,
        }

        self.logger.info(
            f"Compatibility assessment: "
            f"{recommendation}"
        )

        return result
    def generate_recommendations(
    self,
    investor: InvestorProfile,
    risk_score: float,
    maximum_drawdown: float,
    risk_contribution: dict[str, float],
) -> list[str]:
        """
        Generate actionable recommendations based on
        investor requirements and portfolio risk.
        """

        recommendations = []

        # Drawdown warning
        if (
            abs(maximum_drawdown)
            > investor.maximum_acceptable_loss
        ):
            recommendations.append(
                "Consider reducing portfolio exposure "
                "because historical drawdown exceeds "
                "your maximum acceptable loss."
            )

        # Risk score warning
        if investor.risk_tolerance == "MODERATE":
            if risk_score >= 50:
                recommendations.append(
                    "Consider lowering overall portfolio "
                    "risk to better match moderate risk tolerance."
                )

        elif investor.risk_tolerance == "LOW":
            if risk_score >= 40:
                recommendations.append(
                    "Consider moving toward lower-volatility "
                    "assets and reducing high-risk allocations."
                )

        # Risk concentration
        if risk_contribution:
            highest_asset = max(
                risk_contribution,
                key=risk_contribution.get,
            )

            highest_contribution = (
                risk_contribution[highest_asset]
            )

            if highest_contribution > 0.40:
                recommendations.append(
                    f"{highest_asset} contributes approximately "
                    f"{highest_contribution:.1%} of portfolio risk. "
                    f"Consider reducing its allocation."
                )

        # Investment horizon
        if investor.investment_horizon_years < 5:
            if risk_score > 50:
                recommendations.append(
                    "Your investment horizon may be short "
                    "for the current portfolio risk level."
                )

        if not recommendations:
            recommendations.append(
                "The portfolio is broadly aligned with "
                "the investor profile."
            )

        return recommendations
    def check_constraint_feasibility(
    self,
    asset_returns,
    investor_profile,
    maximum_weight: float = 0.30,
    target_volatility: float | None = None,
) -> dict:
        """
        Check whether the investor's constraints can
        be satisfied using the available assets.
        """

        self.logger.info(
            "Checking investor constraint feasibility."
        )

        result = (
            self.portfolio_optimizer.check_feasibility(
            asset_returns=asset_returns,
            maximum_acceptable_loss=(
            investor_profile.maximum_acceptable_loss
            ),
            target_volatility=target_volatility,
            maximum_weight=maximum_weight,
            )
        )

        return result