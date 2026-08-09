from backend.services.market_data_service import MarketDataService

service = MarketDataService()

dataframe = service._fetch_data("AAPL")

service._validate_dataframe(dataframe)

print("Validation Successful")