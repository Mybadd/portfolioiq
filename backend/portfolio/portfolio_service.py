"""
Portfolio Service

Responsible for creating and validating investor portfolios.
"""

import pandas as pd

from backend.core.logger import get_logger
from backend.constants.market_universe import SUPPORTED_STOCKS
from backend.models.investor_profile import InvestorProfile
from backend.models.portfolio import Portfolio
from backend.models.portfolio_state import PortfolioState
from backend.portfolio.portfolio_data_service import PortfolioDataService
from backend.services.market_data_service import MarketDataService


class PortfolioService:
    """
    Service responsible for portfolio operations.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.portfolio_data_service = PortfolioDataService()
        self.market_data_service = MarketDataService()

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
            f"Portfolio created with "
            f"{len(portfolio.weights)} assets."
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
            if not isinstance(amount, (int, float)):
                raise TypeError(
                    f"Investment amount for {symbol} "
                    f"must be numeric."
                )

            if amount <= 0:
                raise ValueError(
                    f"Investment amount for {symbol} "
                    f"must be greater than zero."
                )

        self._validate_symbols(amounts)

        total_amount = sum(amounts.values())

        if total_amount <= 0:
            raise ValueError(
                "Total investment amount must be "
                "greater than zero."
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

        portfolio_state = self.create_portfolio_state(
            holdings
        )

        return self.create_portfolio(
            portfolio_state.weights
        )

    def create_portfolio_state(
        self,
        holdings: dict[str, float],
    ) -> PortfolioState:
        """
        Create the current market state of a portfolio.

        Fetches current market prices and calculates
        position values, total portfolio value, and
        dynamically calculated portfolio weights.
        """

        self.logger.info(
            "Creating portfolio state from share holdings."
        )

        if not holdings:
            raise ValueError(
                "Portfolio holdings cannot be empty."
            )

        self._validate_symbols(holdings)

        normalized_holdings: dict[str, float] = {}
        latest_prices: dict[str, float] = {}
        position_values: dict[str, float] = {}

        for symbol, shares in holdings.items():

            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(
                    "Stock symbol must be a non-empty string."
                )

            if not isinstance(shares, (int, float)):
                raise TypeError(
                    f"Shares for {symbol} must be numeric."
                )

            if shares <= 0:
                raise ValueError(
                    f"Shares for {symbol} "
                    f"must be greater than zero."
                )

            normalized_symbol = symbol.upper()

            current_price = (
                self.market_data_service.get_current_price(
                    normalized_symbol
                )
            )

            if (
                current_price is None
                or current_price <= 0
            ):
                raise ValueError(
                    f"Could not retrieve a valid price "
                    f"for {normalized_symbol}."
                )

            normalized_holdings[normalized_symbol] = float(
                shares
            )

            latest_prices[normalized_symbol] = float(
                current_price
            )

            position_value = (
                float(shares)
                * float(current_price)
            )

            position_values[normalized_symbol] = (
                position_value
            )

            self.logger.info(
                f"{normalized_symbol}: "
                f"{shares} shares × "
                f"{current_price:.2f} = "
                f"{position_value:.2f}"
            )

        total_portfolio_value = sum(
            position_values.values()
        )

        if total_portfolio_value <= 0:
            raise ValueError(
                "Total portfolio value must be "
                "greater than zero."
            )

        weights = {
            symbol: position_value
            / total_portfolio_value
            for symbol, position_value
            in position_values.items()
        }

        self.logger.info(
            f"Total portfolio market value: "
            f"{total_portfolio_value:.2f}"
        )

        return PortfolioState(
            holdings=normalized_holdings,
            latest_prices=latest_prices,
            position_values=position_values,
            total_portfolio_value=float(
                total_portfolio_value
            ),
            weights=weights,
        )

    def _validate_weights(
        self,
        weights: dict[str, float],
    ) -> None:
        """
        Validate portfolio weights.
        """

        if not weights:
            raise ValueError(
                "Portfolio cannot be empty."
            )

        for symbol, weight in weights.items():

            if not isinstance(weight, (int, float)):
                raise TypeError(
                    f"Weight for {symbol} must be numeric."
                )

            if weight <= 0:
                raise ValueError(
                    f"Weight for {symbol} "
                    f"must be greater than zero."
                )

        total_weight = sum(weights.values())

        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(
                "Portfolio weights must sum to 1.0. "
                f"Current total: {total_weight:.6f}"
            )

    def _validate_symbols(
        self,
        weights: dict[str, float],
    ) -> None:
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
                f"Unsupported stock symbols: "
                f"{unsupported_symbols}"
            )

    def calculate_portfolio_returns(
        self,
        portfolio: Portfolio,
    ) -> pd.Series:
        """
        Calculate historical daily returns for a portfolio.
        """

        self.logger.info(
            "Starting portfolio return calculation."
        )

        symbols = list(
            portfolio.weights.keys()
        )

        price_data = (
            self.portfolio_data_service.get_price_data(
                symbols
            )
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