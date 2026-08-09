from backend.models.investor_profile import InvestorProfile


class InvestorOptimizer:

    RISK_TARGETS = {
        "LOW": 0.15,
        "MODERATE": 0.20,
        "HIGH": 0.30,
    }

    def get_target_volatility(
        self,
        investor: InvestorProfile,
    ) -> float:
        """
        Return the target annualized volatility
        based on investor risk tolerance.
        """

        return self.RISK_TARGETS[
            investor.risk_tolerance
        ]