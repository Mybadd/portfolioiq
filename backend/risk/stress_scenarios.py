from backend.models.stress_test import StressScenario


BROAD_MARKET_DECLINE = StressScenario(
    name="Broad Market Decline",
    asset_shocks={
        "JNJ": -0.10,
        "PG": -0.10,
        "KO": -0.10,
        "MCD": -0.10,
        "HD": -0.10,
    },
)


SEVERE_MARKET_SHOCK = StressScenario(
    name="Severe Market Shock",
    asset_shocks={
        "JNJ": -0.20,
        "PG": -0.20,
        "KO": -0.20,
        "MCD": -0.25,
        "HD": -0.25,
    },
)


CONSUMER_SECTOR_SHOCK = StressScenario(
    name="Consumer Sector Shock",
    asset_shocks={
        "JNJ": -0.15,
        "PG": -0.20,
        "KO": -0.20,
        "MCD": -0.20,
        "HD": -0.25,
    },
)