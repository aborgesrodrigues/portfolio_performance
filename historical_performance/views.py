import datetime
from decimal import Decimal

from django.db.models import Max, Case, When, DateField
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

# Create your views here.
from historical_performance.forms import PortfolioForm, AllocationFormSet
from historical_performance.models import Portfolio, PerformancePortfolio
from dal import autocomplete
import requests
import json

#api = "https://api.worldtradingdata.com/api/v1/stock_search?api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG"

def get_api_url(command):
	return "https://api.worldtradingdata.com/api/v1/%s?api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG" % command

class StockAutocomplete(autocomplete.Select2ListView):
	def get_list(self):
		response = requests.get(get_api_url("stock_search") + "&search_term=%s&search_by=symbol&limit=50&page=1" % self.q)
		if response.ok:
		    json_response = json.loads(response.text)

		    return [stock.get("symbol") for stock in json_response.get("data")]
		else:
			return []

#	def results(self, results):
#		#Customizing the autuocomplete results
#		response = requests.get(api + "&search_term=%s&search_by=symbol&limit=50&page=1" % self.q)
#		if response.ok:
#		    json_response = json.loads(response.text)
#
#		    return [dict(id=stock.get("symbol"), text="%s - %s" % (stock.get("symbol", ""), stock.get("name", ""))) for stock in json_response.get("data")]
#		else:
#			return []

def portfolio_view(request, username= None):
	# If the username is passed get the data from de database
	initial_portfolio = None
	if username is not None:
		initial_portfolio = get_object_or_404(Portfolio, username=username)

	form = PortfolioForm(request.POST or None, instance=initial_portfolio)
	formset = AllocationFormSet(request.POST or None, instance=initial_portfolio)

	if form.is_valid():
		#Save portifolio data
		initial_portfolio = form.save()

		#Save allocations data
		formset = AllocationFormSet(request.POST or None, instance=initial_portfolio)
		if formset.is_valid():
			formset.save()

			#Save daily historical performance data
			for allocation in initial_portfolio.allocations.all():
				#remove old allocations
				PerformancePortfolio.objects.filter(allocation=allocation).delete()

				#Get historical for the stock
				#https: // api.worldtradingdata.com / api / v1 / history?symbol = SNAP & sort = newest & api_token = avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG
				response = requests.get(get_api_url("history") + "&symbol=%s&date_from=%s&sort=oldest" % (allocation.stock, allocation.portfolio.start_date.strftime("%Y-%m-%d")))

				if response.ok:
					json_response = json.loads(response.text)

					if json_response.get("name",None):
						history = json_response.get("history", [])
						for key in history:
							performancePortfolio = PerformancePortfolio()
							performancePortfolio.allocation = allocation
							performancePortfolio.unit_value = Decimal(history[key].get("close", None))
							performancePortfolio.date = datetime.datetime.strptime(key, "%Y-%m-%d")
							performancePortfolio.save()


			messages.success(request, 'Performance portfolio successfully added .')
			return redirect('portfolio_view', username=initial_portfolio.username)

	#generate the data for the stock price history chart
	stock_price_history_day_data = {}
	portfolio_performance_data = {}
	month_data = {}
	year_data = {}

	if initial_portfolio:

		for allocation in initial_portfolio.allocations.all():
			#stock_price_history_day_data[allocation.stock] = [dict(x=performance.date.strftime("%Y-%m-%d"), y=str(performance.unit_value)) for performance in allocation.performances.all()]

			month_data[allocation.stock] = {}
			year_data[allocation.stock] = {}
			stock_price_history_day_data[allocation.stock] = []
			portfolio_performance_data[allocation.stock] = []
			for performance in allocation.performances.all():
				stock_price_history_day_data[allocation.stock].append(dict(x=performance.date.strftime("%Y-%m-%d"), y=str(performance.unit_value)))

				#get the performance date from the last day of each month
				month_data[allocation.stock][performance.date.strftime("%B/%Y")] = performance
				# get the performance date from the last day of each year
				year_data[allocation.stock][performance.date.strftime("%Y")] = performance

		for stock in month_data:
			for month in month_data[stock]:
				performance = month_data[stock][month]
				portfolio_performance_data[stock].append(dict(x=month, y=str(performance.unit_value * performance.allocation.quantity)))

	context = {}
	context['form'] = form
	context['formset'] = formset
	context['stock_price_history_day_data'] = json.dumps(stock_price_history_day_data)
	context['portfolio_performance_data'] = json.dumps(portfolio_performance_data)

	return render(request, 'portfolio.html', context)
