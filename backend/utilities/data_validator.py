"""
Data Validation Utilities

Provides reusable validation methods for
market data and future datasets.
"""

import pandas as pd


class DataValidator:
    """
    Utility class for validating datasets.
    """

    REQUIRED_COLUMNS = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    @staticmethod
    def validate_market_data(dataframe: pd.DataFrame) -> None:
        """
        Validate downloaded market data.
        """

        # Rule 1
        if dataframe.empty:
            raise ValueError("Downloaded dataset is empty.")

        # Rule 2
        missing_columns = [
            column
            for column in DataValidator.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        # Rule 3
        if dataframe.isnull().values.any():
            raise ValueError(
                "Dataset contains missing values."
            )

        # Rule 4
        if dataframe.index.duplicated().any():
            raise ValueError(
                "Duplicate dates detected."
            )

        # Rule 5
        if not dataframe.index.is_monotonic_increasing:
            raise ValueError(
                "Dates are not sorted."
            )