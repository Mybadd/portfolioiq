"""
Stress Testing API routes.

Provides hypothetical portfolio stress testing
using predefined and custom asset-level scenarios,
as well as historical market stress testing.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.models.portfolio import Portfolio
from backend.models.stress_test import StressScenario

from backend.risk.risk_service import RiskService

from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)

from backend.services.historical_stress_service import (
    HistoricalStressService,
)


router = APIRouter(
    prefix="/api/stress-test",
    tags=["Stress Testing"],
)


risk_service = RiskService()

portfolio_data_service = (
    PortfolioDataService()
)

historical_stress_service = (
    HistoricalStressService()
)


# ==========================================================
# Request Models
# ==========================================================


class StressTestRequest(BaseModel):
    """
    Request model for portfolio stress testing.
    """

    weights: dict[str, float] = Field(
        ...,
        description=(
            "Portfolio weights expressed as decimals."
        ),
    )

    scenario: str = Field(
        default="MARKET_CRASH",
        description=(
            "Predefined stress scenario or CUSTOM."
        ),
    )

    asset_shocks: dict[str, float] | None = Field(
        default=None,
        description=(
            "Custom asset shocks expressed as decimals. "
            "Required when scenario is CUSTOM."
        ),
    )


class HistoricalStressTestRequest(BaseModel):
    """
    Request model for historical stress testing.
    """

    weights: dict[str, float] = Field(
        ...,
        description=(
            "Portfolio weights expressed as decimals."
        ),
    )

    scenario: str = Field(
        ...,
        description=(
            "Historical scenario identifier."
        ),
    )


# ==========================================================
# Hypothetical Stress Scenarios
# ==========================================================


PREDEFINED_SCENARIOS = {
    "MARKET_CORRECTION": {
        "NFLX": -0.10,
        "PEP": -0.10,
        "WMT": -0.10,
        "UNH": -0.10,
        "DIS": -0.10,
    },
    "MARKET_CRASH": {
        "NFLX": -0.20,
        "PEP": -0.20,
        "WMT": -0.20,
        "UNH": -0.20,
        "DIS": -0.20,
    },
    "SEVERE_CRASH": {
        "NFLX": -0.35,
        "PEP": -0.35,
        "WMT": -0.35,
        "UNH": -0.35,
        "DIS": -0.35,
    },
    "TECH_SELL_OFF": {
        "NFLX": -0.35,
        "PEP": -0.10,
        "WMT": -0.10,
        "UNH": -0.10,
        "DIS": -0.20,
    },
    "DEFENSIVE_SECTOR_SHOCK": {
        "NFLX": -0.10,
        "PEP": -0.20,
        "WMT": -0.20,
        "UNH": -0.30,
        "DIS": -0.10,
    },
    "CONSUMER_DISCRETIONARY_SHOCK": {
        "NFLX": -0.30,
        "PEP": -0.10,
        "WMT": -0.10,
        "UNH": -0.10,
        "DIS": -0.30,
    },
}


def build_scenario(
    scenario_name: str,
    symbols: list[str],
    custom_shocks: dict[str, float] | None,
) -> StressScenario:
    """
    Build a StressScenario from a predefined
    or custom scenario.
    """

    normalized_name = (
        scenario_name.strip().upper()
    )

    # ------------------------------------------------------
    # Custom scenario
    # ------------------------------------------------------

    if normalized_name == "CUSTOM":

        if not custom_shocks:
            raise ValueError(
                "Custom asset shocks are required "
                "for a CUSTOM scenario."
            )

        normalized_shocks = {
            symbol.strip().upper(): float(shock)
            for symbol, shock in custom_shocks.items()
        }

        missing_symbols = [
            symbol
            for symbol in symbols
            if symbol not in normalized_shocks
        ]

        if missing_symbols:
            raise ValueError(
                "Custom shocks are missing for: "
                f"{missing_symbols}"
            )

        return StressScenario(
            name="Custom Scenario",
            asset_shocks=normalized_shocks,
        )

    # ------------------------------------------------------
    # Predefined scenario
    # ------------------------------------------------------

    if normalized_name not in PREDEFINED_SCENARIOS:
        raise ValueError(
            f"Unsupported stress scenario: "
            f"{scenario_name}. Supported scenarios are: "
            f"{sorted(PREDEFINED_SCENARIOS)} and CUSTOM."
        )

    scenario_shocks = PREDEFINED_SCENARIOS[
        normalized_name
    ]

    missing_symbols = [
        symbol
        for symbol in symbols
        if symbol not in scenario_shocks
    ]

    if missing_symbols:
        raise ValueError(
            "Scenario does not define shocks for: "
            f"{missing_symbols}"
        )

    asset_shocks = {
        symbol: scenario_shocks[symbol]
        for symbol in symbols
    }

    return StressScenario(
        name=normalized_name.replace(
            "_",
            " ",
        ).title(),
        asset_shocks=asset_shocks,
    )


# ==========================================================
# Hypothetical Stress Test
# ==========================================================


@router.post("/analyze")
def analyze_stress_test(
    request: StressTestRequest,
) -> dict:
    """
    Calculate portfolio impact under a hypothetical
    stress scenario.
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
            for symbol, weight in request.weights.items()
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
            for symbol, weight in request.weights.items()
        }

        symbols = list(
            normalized_weights.keys()
        )

        # --------------------------------------------------
        # Build scenario
        # --------------------------------------------------

        stress_scenario = build_scenario(
            scenario_name=request.scenario,
            symbols=symbols,
            custom_shocks=request.asset_shocks,
        )

        # --------------------------------------------------
        # Create portfolio model
        # --------------------------------------------------

        portfolio = Portfolio(
            weights=normalized_weights,
        )

        # --------------------------------------------------
        # Calculate portfolio impact
        # --------------------------------------------------

        portfolio_impact = (
            risk_service.calculate_stress_test(
                portfolio=portfolio,
                scenario=stress_scenario,
            )
        )

        # --------------------------------------------------
        # Calculate asset-level contributions
        # --------------------------------------------------

        contributions = {}

        for symbol, weight in normalized_weights.items():

            shock = stress_scenario.asset_shocks.get(
                symbol,
                0.0,
            )

            contributions[symbol] = {
                "weight": weight,
                "shock": shock,
                "contribution": weight * shock,
            }

        # --------------------------------------------------
        # Calculate recovery requirement
        # --------------------------------------------------

        portfolio_value_after = (
            1.0 + portfolio_impact
        )

        if portfolio_value_after <= 0:

            recovery_required = None

        else:

            recovery_required = (
                1.0 / portfolio_value_after
            ) - 1.0

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "scenario": {
                "name": stress_scenario.name,
                "asset_shocks": (
                    stress_scenario.asset_shocks
                ),
            },
            "portfolio_impact": portfolio_impact,
            "portfolio_value_after": (
                portfolio_value_after
            ),
            "recovery_required": (
                recovery_required
            ),
            "asset_contributions": contributions,
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
                "Stress test failed: "
                f"{str(error)}"
            ),
        ) from error


# ==========================================================
# Historical Stress Test
# ==========================================================


@router.post("/historical")
def analyze_historical_stress_test(
    request: HistoricalStressTestRequest,
) -> dict:
    """
    Calculate portfolio performance during
    a historical market stress period.
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
            for symbol, weight in request.weights.items()
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
            for symbol, weight in request.weights.items()
        }

        symbols = list(
            normalized_weights.keys()
        )

        # --------------------------------------------------
        # Get historical scenario
        # --------------------------------------------------

        scenario = (
            historical_stress_service.get_scenario(
                request.scenario
            )
        )

        # --------------------------------------------------
        # Retrieve historical market prices
        # --------------------------------------------------

        price_data = (
            portfolio_data_service.get_price_data(
                symbols
            )
        )

        # --------------------------------------------------
        # Combine price data
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
            historical_stress_service.calculate_asset_returns(
                price_data=combined_prices,
                scenario=scenario,
            )
        )

        # --------------------------------------------------
        # Calculate portfolio impact
        # --------------------------------------------------

        portfolio_impact = (
            historical_stress_service.calculate_portfolio_impact(
                asset_returns=asset_returns,
                weights=normalized_weights,
            )
        )

        # --------------------------------------------------
        # Calculate portfolio value after event
        # --------------------------------------------------

        portfolio_value_after = (
            1.0 + portfolio_impact
        )

        # --------------------------------------------------
        # Calculate recovery requirement
        # --------------------------------------------------

        recovery_required = (
            historical_stress_service.calculate_recovery_required(
                portfolio_impact
            )
        )

        # --------------------------------------------------
        # Calculate asset-level contributions
        # --------------------------------------------------

        asset_contributions = {}

        for symbol, weight in normalized_weights.items():

            historical_return = float(
                asset_returns[symbol]
            )

            contribution = (
                weight * historical_return
            )

            asset_contributions[symbol] = {
                "weight": weight,
                "historical_return": historical_return,
                "contribution": contribution,
            }

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "scenario": {
                "name": scenario.name,
                "start_date": scenario.start_date,
                "end_date": scenario.end_date,
                "description": scenario.description,
            },
            "portfolio_impact": portfolio_impact,
            "portfolio_value_after": (
                portfolio_value_after
            ),
            "recovery_required": (
                recovery_required
            ),
            "asset_contributions": (
                asset_contributions
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
                "Historical stress test failed: "
                f"{str(error)}"
            ),
        ) from error