"""
Portfolio Optimization API routes.

Provides risk-adjusted portfolio optimization and
before/after portfolio comparison.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)
from backend.portfolio.portfolio_optimizer import (
    PortfolioOptimizer,
)
from backend.services.portfolio_comparison_service import (
    PortfolioComparisonService,
)
from backend.risk.risk_service import RiskService

router = APIRouter(
    prefix="/api/optimization",
    tags=["Optimization"],
)


portfolio_data_service = PortfolioDataService()
portfolio_optimizer = PortfolioOptimizer()
portfolio_comparison_service = (
    PortfolioComparisonService()
)
risk_service = RiskService()

class OptimizationRequest(BaseModel):
    """
    Request model for portfolio optimization.
    """

    weights: dict[str, float] = Field(
        ...,
        description=(
            "Current portfolio weights expressed "
            "as decimals."
        ),
    )

    maximum_weight: float = Field(
        default=0.30,
        gt=0.0,
        le=1.0,
        description=(
            "Maximum allowed allocation to any "
            "single asset."
        ),
    )

    target_volatility: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional maximum annualized portfolio "
            "volatility."
        ),
    )

    risk_free_rate: float = Field(
        default=0.0,
        ge=0.0,
        description="Annual risk-free rate.",
    )
    method: str = Field(
    default="MINIMUM_VARIANCE",
    description=(
        "Portfolio optimization method. "
        "Supported methods: MINIMUM_VARIANCE, "
        "RISK_PARITY."
    ),
)

@router.post("/optimize")
def optimize_portfolio(
    request: OptimizationRequest,
) -> dict:
    """
    Optimize the current portfolio and compare
    the original portfolio with the optimized one.
    """

    try:
        # --------------------------------------------------
        # Validate portfolio
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
                "Portfolio weights cannot be negative: "
                f"{invalid_weights}"
            )

        # --------------------------------------------------
        # Normalize symbols
        # --------------------------------------------------

        normalized_weights = {
            symbol.strip().upper(): float(weight)
            for symbol, weight in request.weights.items()
        }

        symbols = list(
            normalized_weights.keys()
        )

        # --------------------------------------------------
        # Retrieve historical market data
        # --------------------------------------------------

        price_data = (
            portfolio_data_service.get_price_data(
                symbols
            )
        )

        # --------------------------------------------------
        # Prepare asset returns
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Optimize portfolio
        # --------------------------------------------------

        optimized_weights = (
            portfolio_optimizer.optimize(
            asset_returns=asset_returns,
            maximum_weight=request.maximum_weight,
            target_volatility=request.target_volatility,
            risk_free_rate=request.risk_free_rate,
            method=request.method,
    )
)

        # --------------------------------------------------
        # Compare original and optimized portfolios
        # --------------------------------------------------

        comparison = (
            portfolio_comparison_service.compare(
                asset_returns=asset_returns,
                before_weights=normalized_weights,
                after_weights=optimized_weights,
            )
        )
        # --------------------------------------------------
# Calculate risk contribution before and after
# optimization
# --------------------------------------------------

        before_risk_contribution = (
            risk_service.calculate_risk_contribution(
                asset_returns=asset_returns,
                weights=normalized_weights,
            )
        )

        after_risk_contribution = (
            risk_service.calculate_risk_contribution(
                asset_returns=asset_returns,
                weights=optimized_weights,
            )
        )

        normalized_before_risk_contribution = {
            symbol: float(value)
            for symbol, value in before_risk_contribution.items()
        }

        normalized_after_risk_contribution = {
            symbol: float(value)
            for symbol, value in after_risk_contribution.items()
        }
        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "original_weights": normalized_weights,
            "optimized_weights": optimized_weights,
            "comparison": {
                "before_volatility": (
                    comparison.before_volatility
                ),
                "after_volatility": (
                    comparison.after_volatility
                ),
                "before_drawdown": (
                    comparison.before_drawdown
                ),
                "after_drawdown": (
                    comparison.after_drawdown
                ),
                "before_sharpe": (
                    comparison.before_sharpe
                ),
                "after_sharpe": (
                    comparison.after_sharpe
                ),
                "before_var": (
                    comparison.before_var
                ),
                "after_var": (
                    comparison.after_var
                ),
                "before_expected_shortfall": (
                    comparison.before_expected_shortfall
                ),
                "after_expected_shortfall": (
                    comparison.after_expected_shortfall
                ),
                "before_risk_score": (
                    comparison.before_risk_score
                ),
                "after_risk_score": (
                    comparison.after_risk_score
                ),
            },
            "maximum_weight": (
                request.maximum_weight
            ),
            "method": request.method.upper(),
            "target_volatility": (
                request.target_volatility
            ),
            "risk_free_rate": (
                request.risk_free_rate
            ),
            "trading_days": len(asset_returns),
            "risk_contribution_before": (
            normalized_before_risk_contribution
        ),

            "risk_contribution_after": (
            normalized_after_risk_contribution
        ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Portfolio optimization failed: "
                f"{str(error)}"
            ),
        ) from error