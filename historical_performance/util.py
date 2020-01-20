from portfolio_performance import settings


def get_api_url(command):
	return "https://api.worldtradingdata.com/api/v1/%s?api_token=%s" % (command, settings.CHARTJS_TOKEN)