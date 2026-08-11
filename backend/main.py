"""
PortfolioIQ FastAPI application entry point.
"""

from fastapi import FastAPI

from backend.api.portfolio_routes import router as portfolio_router


app = FastAPI(
    title="PortfolioIQ",
    description="Quantitative Portfolio Risk Assessment Engine",
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Check whether the API is running."""
    return {
        "status": "healthy",
        "service": "PortfolioIQ API",
    }


app.include_router(portfolio_router)