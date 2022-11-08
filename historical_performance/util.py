from portfolio_performance import settings


def get_api_url(symbol, path=""):
	return f"http://api.marketstack.com/v1{path}?symbols={symbol}&access_key={settings.CHARTJS_TOKEN}"