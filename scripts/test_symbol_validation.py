from backend.services.market_data_service import MarketDataService

service = MarketDataService()

service._validate_symbol("AAPL")

print("Validation passed.")