"""
Portfolio data model.
"""

from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    Represents an investor portfolio.
    """

    weights: dict[str, float]