"""
Monte Carlo Simulation API routes.

Provides historical bootstrap Monte Carlo simulation
for portfolio forward-looking risk analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)

from backend.services.monte_carlo_service import (
    MonteCarloService,
)


router = APIRouter(
    prefix="/api/monte-carlo",
    tags=["Monte Carlo"],
)


portfolio_data_service = (
    PortfolioDataService()
)

monte_carlo_service = (
    MonteCarloService()
)


class MonteCarloRequest(BaseModel):
    """
    Request model for Monte Carlo simulation.
    """

    weights: dict[str, float] = Field(
        ...,
        description=(
            "Portfolio weights expressed as decimals."
        ),
    )

    simulations: int = Field(
        default=10000,
        ge=100,
        le=100000,
        description=(
            "Number of Monte Carlo simulations."
        ),
    )

    confidence_level: float = Field(
        default=0.95,
        gt=0.0,
        lt=1.0,
        description=(
            "Confidence level used for VaR "
            "and Expected Shortfall."
        ),
    )

    random_seed: int | None = Field(
        default=42,
        description=(
            "Optional random seed for "
            "reproducible simulations."
        ),
    )


@router.post("/simulate")
def simulate_monte_carlo(
    request: MonteCarloRequest,
) -> dict:
    """
    Run historical bootstrap Monte Carlo
    simulations across all supported horizons.
    """

    try:
        # --------------------------------------------------
        # Validate portfolio
        # --------------------------------------------------

        if not request.weights:
            raise ValueError(
                "Portfolio weights cannot be empty."
            )

        invalid_weights = [
            symbol
            for symbol, weight
            in request.weights.items()
            if weight < 0
        ]

        if invalid_weights:
            raise ValueError(
                "Portfolio weights cannot be negative: "
                f"{invalid_weights}"
            )

        total_weight = sum(
            request.weights.values()
        )

        if abs(total_weight - 1.0) > 0.0001:
            raise ValueError(
                "Portfolio weights must sum to 1.0."
            )

        # --------------------------------------------------
        # Normalize symbols
        # --------------------------------------------------

        normalized_weights = {
            symbol.strip().upper(): float(weight)
            for symbol, weight
            in request.weights.items()
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
        # Combine closing prices
        # --------------------------------------------------

        combined_prices = (
            portfolio_data_service.combine_price_data(
                price_data
            )
        )

        # --------------------------------------------------
        # Calculate historical asset returns
        # --------------------------------------------------

        asset_returns = (
            portfolio_data_service.calculate_returns(
                combined_prices
            )
        )

        # --------------------------------------------------
        # Run all Monte Carlo horizons
        # --------------------------------------------------

        simulation_results = (
            monte_carlo_service.simulate_all_horizons(
                asset_returns=asset_returns,
                weights=normalized_weights,
                simulations=request.simulations,
                confidence_level=(
                    request.confidence_level
                ),
                random_seed=request.random_seed,
            )
        )

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "portfolio_weights": (
                normalized_weights
            ),
            "method": (
                "HISTORICAL_BOOTSTRAP"
            ),
            "simulations": (
                request.simulations
            ),
            "confidence_level": (
                request.confidence_level
            ),
            "horizons": (
                simulation_results
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
                "Monte Carlo simulation failed: "
                f"{str(error)}"
            ),
        ) from error