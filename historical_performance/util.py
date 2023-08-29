from portfolio_performance import settings


def get_api_url(symbol, path=""):
	return f"http://api.marketstack.com/v1{path}?symbols={symbol}&access_key={settings.CHARTJS_TOKEN}"

def get_search_api_url(symbol):
	return f"http://api.marketstack.com/v1/tickers?search={symbol}&access_key={settings.CHARTJS_TOKEN}"