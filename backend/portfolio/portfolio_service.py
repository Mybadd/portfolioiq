"""
Portfolio Service

Responsible for creating and validating investor portfolios.
"""
import pandas as pd
from backend.models.portfolio import Portfolio
from backend.core.logger import get_logger
from backend.constants.market_universe import SUPPORTED_STOCKS
from backend.portfolio.portfolio_data_service import PortfolioDataService
from backend.services.market_data_service import MarketDataService
from backend.models.investor_profile import InvestorProfile
class PortfolioService:
    """
    Service responsible for portfolio operations.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.portfolio_data_service = PortfolioDataService()
        self.market_data_service = (MarketDataService())
    def create_portfolio(
        self,
        weights: dict[str, float],
    ) -> Portfolio:
        """
        Create and validate an investor portfolio.
        """
        self.logger.info("Creating portfolio...")

        self._validate_weights(weights)
        self._validate_symbols(weights)

        portfolio = Portfolio(
            weights={
                symbol.upper(): weight
                for symbol, weight in weights.items()
            }
        )

        self.logger.info(
            f"Portfolio created with {len(portfolio.weights)} assets."
        )

        return portfolio
    def create_portfolio_from_amounts(
        self,
        amounts: dict[str, float],
        ) -> Portfolio:
        """
        Create a portfolio from monetary allocations.

        Amounts represent how much money the investor
        wants to allocate to each asset.
        """

        self.logger.info(
            "Creating portfolio from investment amounts."
        )

        if not amounts:
            raise ValueError(
                "Investment amounts cannot be empty."
            )

        for symbol, amount in amounts.items():
            if amount <= 0:
                raise ValueError(
                    f"Investment amount for {symbol} "
                    f"must be greater than zero."
                )

        total_amount = sum(amounts.values())

        if total_amount <= 0:
            raise ValueError(
                "Total investment amount must be greater than zero."
            )

        weights = {
            symbol.upper(): amount / total_amount
            for symbol, amount in amounts.items()
        }

        self.logger.info(
            f"Total investment amount: "
            f"{total_amount:.2f}"
        )

        return self.create_portfolio(weights)

    def validate_investment_amount(
    self,
    amounts: dict[str, float],
    investor: InvestorProfile,
) -> None:
        """
        Validate that the portfolio allocation matches
        the investor's available investment amount.
        """

        self.logger.info(
            "Validating portfolio allocation "
            "against investor investment amount."
        )

        if not amounts:
            raise ValueError(
                "Investment allocations cannot be empty."
            )

        total_allocated = sum(
            amounts.values()
        )

        tolerance = 1e-2

        if (
            abs(
                total_allocated
                - investor.investment_amount
            )
            > tolerance
        ):
            raise ValueError(
                f"Portfolio allocation "
                f"({total_allocated:.2f}) does not match "
                f"investor investment amount "
                f"({investor.investment_amount:.2f})."
            )

        self.logger.info(
            "Portfolio allocation matches "
            "investor investment amount."
        )
    def create_portfolio_from_shares(
                    self,
                    holdings: dict[str, float],
                    ) -> Portfolio:
                    """
                    Create a portfolio from the number of shares
                    held for each asset.
            
                    Current market prices are used to calculate
                    portfolio weights.
                    """
            
                    self.logger.info(
                        "Creating portfolio from share holdings."
                    )
            
                    if not holdings:
                        raise ValueError(
                            "Share holdings cannot be empty."
                        )
            
                    for symbol, shares in holdings.items():
                        if shares <= 0:
                            raise ValueError(
                                f"Number of shares for {symbol} "
                                f"must be greater than zero."
                            )
            
                    position_values = {}
            
                    for symbol, shares in holdings.items():
            
                        symbol = symbol.upper()
            
                        current_price = (
                            self.market_data_service
                            .get_current_price(symbol)
                        )
            
                        position_value = (
                            shares * current_price
                        )
            
                        position_values[symbol] = (
                            position_value
                        )
            
                        self.logger.info(
                            f"{symbol}: "
                            f"{shares} shares × "
                            f"{current_price:.2f} = "
                            f"{position_value:.2f}"
                        )
            
                    total_value = sum(
                        position_values.values()
                    )
            
                    if total_value <= 0:
                        raise ValueError(
                            "Total portfolio market value must "
                            "be greater than zero."
                        )
            
                    weights = {
                        symbol: value / total_value
                        for symbol, value in position_values.items()
                    }
            
                    self.logger.info(
                        f"Total portfolio market value: "
                        f"{total_value:.2f}"
                    )
            
                    return self.create_portfolio(weights)
    def _validate_weights(
        self,
        weights: dict[str, float],
    ) -> None:
        """
        Validate portfolio weights.
        """
           # Portfolio must not be empty
        if not weights:
            raise ValueError("Portfolio cannot be empty.")

    # Every asset must have a positive weight
        for symbol, weight in weights.items():
            if weight <= 0:
                raise ValueError(
                    f"Weight for {symbol} must be greater than zero."
                )

    # Portfolio weights must equal 100 percent
        total_weight = sum(weights.values())

        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(
                f"Portfolio weights must sum to 1.0. "
                f"Current total: {total_weight:.6f}"
            )
    
    def _validate_symbols(self,weights: dict[str, float],) -> None:
        """
        Validate that all portfolio assets are supported.
        """

        unsupported_symbols = [
            symbol.upper()
            for symbol in weights
            if symbol.upper() not in SUPPORTED_STOCKS
        ]

        if unsupported_symbols:
            raise ValueError(
                f"Unsupported stock symbols: {unsupported_symbols}"
            )   
    def calculate_portfolio_returns(self,portfolio: Portfolio,) -> pd.Series:
        """
        Calculate historical daily returns for a portfolio.
        """

        self.logger.info(
            "Starting portfolio return calculation."
        )

        symbols = list(portfolio.weights.keys())

        price_data = self.portfolio_data_service.get_price_data(
            symbols
        )

        combined_prices = (
            self.portfolio_data_service.combine_price_data(
                price_data
            )
        )

        asset_returns = (
            self.portfolio_data_service.calculate_returns(
                combined_prices
            )
        )

        portfolio_returns = (
            self.portfolio_data_service.calculate_portfolio_returns(
                asset_returns,
                portfolio.weights,
            )
        )

        self.logger.info(
            "Portfolio return calculation completed."
        )

        return portfolio_returns
