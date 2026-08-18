"""
PortfolioIQ FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.portfolio_routes import router as portfolio_router
from backend.api.risk_routes import router as risk_router
from backend.api.optimization_routes import (
    router as optimization_router,
)
from backend.api.stress_test_routes import (
    router as stress_test_router,
)
from backend.api.monte_carlo_routes import (
    router as monte_carlo_router,
)

app = FastAPI(
    title="PortfolioIQ",
    description="Quantitative Portfolio Risk Assessment Engine",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Check whether the API is running."""
    return {
        "status": "healthy",
        "service": "PortfolioIQ API",
    }


app.include_router(portfolio_router)
app.include_router(risk_router)
app.include_router(optimization_router)
app.include_router(
    stress_test_router
)
app.include_router(
    monte_carlo_router
)