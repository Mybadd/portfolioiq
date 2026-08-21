"""
Portfolio API routes.

Provides portfolio creation and validation through FastAPI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.portfolio.portfolio_service import PortfolioService


router = APIRouter(
    prefix="/api/portfolio",
    tags=["Portfolio"],
)

portfolio_service = PortfolioService()


class PortfolioRequest(BaseModel):
    """
    Portfolio request using normalized asset weights.
    """

    weights: dict[str, float] = Field(
        ...,
        description="Portfolio weights expressed as decimals.",
    )


class AmountHoldingsRequest(BaseModel):
    """
    Portfolio request using monetary investment amounts.
    """

    amounts: dict[str, float] = Field(
        ...,
        description="Investment amount for each asset.",
    )


class ShareHoldingsRequest(BaseModel):
    """
    Portfolio request using number of shares held.
    """

    holdings: dict[str, float] = Field(
        ...,
        description="Number of shares held for each asset.",
    )


@router.post("/create")
def create_portfolio(
    request: PortfolioRequest,
) -> dict:
    """
    Create and validate a portfolio from asset weights.
    """

    try:
        portfolio = portfolio_service.create_portfolio(
            request.weights
        )

        return {
            "weights": portfolio.weights,
            "asset_count": len(portfolio.weights),
            "total_weight": sum(
                portfolio.weights.values()
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
            detail=f"Portfolio creation failed: {str(exc)}",
        ) from exc


@router.post("/from-amounts")
def create_portfolio_from_amounts(
    request: AmountHoldingsRequest,
) -> dict:
    """
    Create a portfolio from monetary investment amounts.

    The backend converts the investment amounts into
    normalized portfolio weights.
    """

    try:
        portfolio = (
            portfolio_service.create_portfolio_from_amounts(
                request.amounts
            )
        )

        return {
            "weights": portfolio.weights,
            "asset_count": len(portfolio.weights),
            "total_weight": sum(
                portfolio.weights.values()
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
            detail=f"Portfolio creation from amounts failed: "
            f"{str(exc)}",
        ) from exc


@router.post("/from-shares")
def create_portfolio_from_shares(
    request: ShareHoldingsRequest,
) -> dict:
    """
    Create a portfolio from DMAT share holdings.

    Current market prices are used by PortfolioService
    to calculate normalized portfolio weights.
    """

    try:
        portfolio = (
            portfolio_service.create_portfolio_from_shares(
                request.holdings
            )
        )

        return {
            "weights": portfolio.weights,
            "asset_count": len(portfolio.weights),
            "total_weight": sum(
                portfolio.weights.values()
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
            detail=f"Portfolio creation from shares failed: "
            f"{str(exc)}",
        ) from exc
@router.post("/state")
def get_portfolio_state(
        request: ShareHoldingsRequest,
    ) -> dict:
        """
        Create and return the current market state
        of a portfolio.

        The portfolio state includes the holdings,
        current market prices, position values,
        total portfolio value, and dynamic weights.
        """

        try:
            portfolio_state = (
                portfolio_service.create_portfolio_state(
                    request.holdings
                )
            )

            return {
                "holdings": portfolio_state.holdings,
                "latest_prices": (
                    portfolio_state.latest_prices
                ),
                "position_values": (
                    portfolio_state.position_values
                ),
                "total_portfolio_value": (
                    portfolio_state.total_portfolio_value
                ),
                "weights": portfolio_state.weights,
                "asset_count": len(
                    portfolio_state.holdings
                ),
            }

        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Portfolio state creation failed: "
                    f"{str(exc)}"
                ),
            ) from exc