"""
Risk API routes.

Provides portfolio risk analysis through FastAPI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.models.investor_profile import InvestorProfile

from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)

from backend.risk.risk_service import RiskService

from backend.risk.risk_scoring_service import (
    RiskScoringService,
)

from backend.services.investor_assessment_service import (
    InvestorAssessmentService,
)


router = APIRouter(
    prefix="/api/risk",
    tags=["Risk"],
)

portfolio_data_service = PortfolioDataService()
risk_service = RiskService()
risk_scoring_service = RiskScoringService()
investor_assessment_service = InvestorAssessmentService()


class InvestorProfileRequest(BaseModel):
    """
    Investor profile used for portfolio compatibility assessment.
    """

    investment_amount: float = Field(
        ...,
        gt=0,
        description="Total amount invested.",
    )

    investment_horizon_years: int = Field(
        ...,
        gt=0,
        description="Investment horizon in years.",
    )

    risk_tolerance: str = Field(
        ...,
        description="Investor risk tolerance: LOW, MODERATE, or HIGH.",
    )

    maximum_acceptable_loss: float = Field(
        ...,
        gt=0,
        le=1,
        description="Maximum acceptable loss expressed as a decimal.",
    )

    investment_objective: str = Field(
        ...,
        min_length=1,
        description="Primary investment objective.",
    )


class RiskAnalysisRequest(BaseModel):
    """
    Request model for portfolio risk analysis.
    """

    weights: dict[str, float] = Field(
        ...,
        description="Portfolio weights expressed as decimals.",
    )

    risk_free_rate: float = Field(
        default=0.0,
        ge=0.0,
        description="Annual risk-free rate.",
    )

    confidence_level: float = Field(
        default=0.95,
        gt=0.0,
        lt=1.0,
        description=(
            "Confidence level used for VaR and "
            "Expected Shortfall."
        ),
    )

    investor_profile: InvestorProfileRequest = Field(
        ...,
        description=(
            "Investor profile used for compatibility "
            "assessment."
        ),
    )


@router.post("/analyze")
def analyze_risk(
    request: RiskAnalysisRequest,
) -> dict:
    """
    Calculate quantitative risk metrics,
    risk score, investor compatibility,
    and actionable recommendations.
    """

    try:
        # --------------------------------------------------
        # Validate portfolio weights
        # --------------------------------------------------

        if not request.weights:
            raise ValueError(
                "Portfolio weights cannot be empty."
            )

        total_weight = sum(
            request.weights.values()
        )

        if abs(total_weight - 1.0) > 0.0001:
            raise ValueError(
                "Portfolio weights must sum to 1.0."
            )

        invalid_weights = [
            symbol
            for symbol, weight in request.weights.items()
            if weight < 0
        ]

        if invalid_weights:
            raise ValueError(
                f"Portfolio weights cannot be negative: "
                f"{invalid_weights}"
            )

        # --------------------------------------------------
        # Normalize symbols
        # --------------------------------------------------

        symbols = [
            symbol.strip().upper()
            for symbol in request.weights
        ]

        normalized_weights = {
            symbol.strip().upper(): weight
            for symbol, weight in request.weights.items()
        }

        # --------------------------------------------------
        # Retrieve historical market prices
        # --------------------------------------------------

        price_data = (
            portfolio_data_service.get_price_data(
                symbols
            )
        )

        # --------------------------------------------------
        # Combine closing prices
        # --------------------------------------------------

        combined_prices = (
            portfolio_data_service.combine_price_data(
                price_data
            )
        )

        # --------------------------------------------------
        # Calculate daily asset returns
        # --------------------------------------------------

        asset_returns = (
            portfolio_data_service.calculate_returns(
                combined_prices
            )
        )

        # --------------------------------------------------
        # Calculate daily portfolio returns
        # --------------------------------------------------

        portfolio_returns = (
            portfolio_data_service.calculate_portfolio_returns(
                asset_returns,
                normalized_weights,
            )
        )

        # --------------------------------------------------
        # Calculate quantitative risk metrics
        # --------------------------------------------------

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
                portfolio_returns,
                request.risk_free_rate,
            )
        )

        historical_var = (
            risk_service.calculate_historical_value_at_risk(
                portfolio_returns,
                request.confidence_level,
            )
        )

        expected_shortfall = (
            risk_service.calculate_expected_shortfall(
                portfolio_returns,
                request.confidence_level,
            )
        )

        # --------------------------------------------------
        # Calculate asset-level risk contribution
        # --------------------------------------------------

        risk_contribution = (
            risk_service.calculate_risk_contribution(
                asset_returns,
                normalized_weights,
            )
        )

        normalized_risk_contribution = {
            symbol: float(value)
            for symbol, value in risk_contribution.items()
        }

        # --------------------------------------------------
        # Calculate overall risk score
        # --------------------------------------------------

        risk_score = (
            risk_scoring_service.calculate_risk_score(
                annualized_volatility=(
                    annualized_volatility
                ),
                maximum_drawdown=(
                    maximum_drawdown
                ),
                sharpe_ratio=(
                    sharpe_ratio
                ),
                historical_value_at_risk=(
                    historical_var
                ),
                expected_shortfall=(
                    expected_shortfall
                ),
            )
        )

        risk_category = (
            risk_scoring_service.classify_risk(
                risk_score
            )
        )

        # --------------------------------------------------
        # Create investor domain model
        # --------------------------------------------------

        investor = InvestorProfile(
            investment_amount=(
                request.investor_profile
                .investment_amount
            ),
            investment_horizon_years=(
                request.investor_profile
                .investment_horizon_years
            ),
            risk_tolerance=(
                request.investor_profile
                .risk_tolerance
            ),
            maximum_acceptable_loss=(
                request.investor_profile
                .maximum_acceptable_loss
            ),
            investment_objective=(
                request.investor_profile
                .investment_objective
            ),
        )

        # --------------------------------------------------
        # Assess investor compatibility
        # --------------------------------------------------

        compatibility = (
            investor_assessment_service
            .assess_compatibility(
                investor=investor,
                risk_score=risk_score,
                maximum_drawdown=maximum_drawdown,
            )
        )

        # --------------------------------------------------
        # Generate recommendations
        # --------------------------------------------------

        recommendations = (
            investor_assessment_service
            .generate_recommendations(
                investor=investor,
                risk_score=risk_score,
                maximum_drawdown=maximum_drawdown,
                risk_contribution=(
                    normalized_risk_contribution
                ),
            )
        )

        # --------------------------------------------------
        # Return complete analysis
        # --------------------------------------------------

        return {
            "weights": normalized_weights,

            "metrics": {
                "annualized_volatility": (
                    annualized_volatility
                ),
                "maximum_drawdown": (
                    maximum_drawdown
                ),
                "sharpe_ratio": (
                    sharpe_ratio
                ),
                "historical_var": (
                    historical_var
                ),
                "expected_shortfall": (
                    expected_shortfall
                ),
            },

            "risk_score": risk_score,

            "risk_category": risk_category,

            "risk_contribution": (
                normalized_risk_contribution
            ),

            "compatibility": compatibility,

            "recommendations": recommendations,

            "confidence_level": (
                request.confidence_level
            ),

            "risk_free_rate": (
                request.risk_free_rate
            ),

            "trading_days": (
                len(portfolio_returns)
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(exc)}",
        ) from exc