"""
Portfolio API routes.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.portfolio.portfolio_service import PortfolioService


router = APIRouter(
    prefix="/api/portfolio",
    tags=["Portfolio"],
)

portfolio_service = PortfolioService()


class PortfolioRequest(BaseModel):
    weights: dict[str, float]


@router.post("/create")
def create_portfolio(
    request: PortfolioRequest,
) -> dict:
    """
    Create and validate a portfolio from asset weights.
    """

    portfolio = portfolio_service.create_portfolio(
        request.weights
    )

    return {
        "weights": portfolio.weights,
        "asset_count": len(portfolio.weights),
        "total_weight": sum(portfolio.weights.values()),
    }