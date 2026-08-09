"""
Risk Report Service

Combines portfolio risk metrics, risk scoring,
and investor assessment into a single report.
"""
import numpy as np
from backend.core.logger import get_logger
from backend.risk.risk_scoring_service import RiskScoringService
from backend.services.investor_assessment_service import (
    InvestorAssessmentService,
)


class RiskReportService:
    """
    Generates a complete quantitative risk report
    for a portfolio and investor.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

        self.risk_scoring_service = (
            RiskScoringService()
        )

        self.investor_assessment_service = (
            InvestorAssessmentService()
        )

    def generate_report(
        self,
        portfolio_returns,
        investor,
        annualized_volatility: float,
        maximum_drawdown: float,
        sharpe_ratio: float,
        historical_value_at_risk: float,
        expected_shortfall: float,
        risk_contribution: dict[str, float],
        feasibility: dict,
    ) -> dict:
        """
        Generate a complete portfolio risk report.
        """

        self.logger.info(
            "Generating comprehensive portfolio risk report."
        )

        # -----------------------------------------
        # Risk Score
        # -----------------------------------------

        risk_score = (
            self.risk_scoring_service.calculate_risk_score(
                annualized_volatility=annualized_volatility,
                maximum_drawdown=maximum_drawdown,
                sharpe_ratio=sharpe_ratio,
                historical_value_at_risk=(
                    historical_value_at_risk
                ),
                expected_shortfall=expected_shortfall,
            )
        )

        risk_level = (
            self.risk_scoring_service.classify_risk(
                risk_score
            )
        )

        # -----------------------------------------
        # Investor Compatibility
        # -----------------------------------------

        assessment = (
            self.investor_assessment_service
            .assess_compatibility(
                investor=investor,
                risk_score=risk_score,
                maximum_drawdown=maximum_drawdown,
            )
        )

        # -----------------------------------------
        # Recommendations
        # -----------------------------------------

        recommendations = (
            self.investor_assessment_service
            .generate_recommendations(
                investor=investor,
                risk_score=risk_score,
                maximum_drawdown=maximum_drawdown,
                risk_contribution=risk_contribution,
            )
        )

        # -----------------------------------------
        # Constraint Feasibility
        # -----------------------------------------

        constraints_feasible = feasibility.get(
        "feasible",
        False,
        )

        best_drawdown = feasibility.get(
        "best_drawdown"
        )

        # Add feasibility information to reasons
        if not constraints_feasible:

            assessment["reasons"].append(
                "Investor constraints cannot be "
                "satisfied with the available assets."
            )

            recommendations.append(
                "Consider expanding the asset universe "
                "to include lower-risk assets."
            )

        # -----------------------------------------
        # Final Report
        # -----------------------------------------

        report = {
            "risk_metrics": {
                "annualized_volatility": (
                    annualized_volatility
                ),
                "maximum_drawdown": (
                    maximum_drawdown
                ),
                "sharpe_ratio": (
                    sharpe_ratio
                ),
                "historical_value_at_risk": (
                    historical_value_at_risk
                ),
                "expected_shortfall": (
                    expected_shortfall
                ),
            },

            "risk_assessment": {
                "risk_score": risk_score,
                "risk_level": risk_level,
            },

            "investor_assessment": assessment,

            "constraint_feasibility": {
            "feasible": constraints_feasible,
            "maximum_acceptable_loss": (
            investor.maximum_acceptable_loss
            ),
            "target_volatility": 0.20,
            "best_drawdown": best_drawdown,
            }   ,

            "risk_contribution": risk_contribution,

            "recommendations": recommendations,
        }

        self.logger.info(
            "Comprehensive portfolio risk report "
            "generated successfully."
        )

        return report