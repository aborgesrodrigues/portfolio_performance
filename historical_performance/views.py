import datetime
from decimal import Decimal
import os

from django.db import transaction
from django.db.models import Max, Case, When, DateField
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

# Create your views here.
from historical_performance.forms import PortfolioForm, AllocationFormSet
from historical_performance.models import Portfolio, PerformancePortfolio
from dal import autocomplete
import requests
import json
from historical_performance.util import get_api_url
from portfolio_performance.settings import BASE_DIR, STATIC_ROOT


class StockAutocomplete(autocomplete.Select2ListView):
	def get_list(self):
		response = requests.get(get_api_url(self.q, "/eod/latest"))
		if response.ok:
			json_response = json.loads(response.text)

			return [stock.get("symbol") for stock in json_response.get("data")]
		else:
			return []


def get_quotation(request, stock, date):
	response = requests.get(get_api_url(stock, f"/intraday/{date}") + "&offset=1")
	if response.ok:
		return JsonResponse(json.loads(response.text))

	return JsonResponse({})

def teste_view(request):
	return JsonResponse({"BASE_DIR": BASE_DIR, "STATIC_ROOT": STATIC_ROOT})

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

			with transaction.atomic():
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
								performance_portfolio = PerformancePortfolio()
								performance_portfolio.allocation = allocation
								performance_portfolio.unit_value = Decimal(history[key].get("close", None))
								performance_portfolio.quantity = allocation.quantity
								performance_portfolio.percentage = 0
								performance_portfolio.date = datetime.datetime.strptime(key, "%Y-%m-%d")

								performance_portfolio.save()

				PerformancePortfolio.calculate_percentage(initial_portfolio)


			messages.success(request, 'Performance portfolio successfully added .')
			return redirect('portfolio_view', username=initial_portfolio.username)

	#generate the data for the stock price history chart
	#data for the stock history chart
	stock_price_history_day_data = {}
	stock_price_history_month_data = {}
	stock_price_history_year_data = {}
	#data for the performance chart
	portfolio_performance_data = {}
	portfolio_performance_month_data = {}
	portfolio_performance_years_data = {}
	years = []
	#variables to calculate percentage of portfolio
	sum_values_month = {}
	sum_values_year = {}

	if initial_portfolio:

		for allocation in initial_portfolio.allocations.all():
			#instantiate array for each stock
			stock_price_history_day_data[allocation.stock] = []
			stock_price_history_month_data[allocation.stock] = []
			stock_price_history_year_data[allocation.stock] = []

			portfolio_performance_data[allocation.stock] = []
			portfolio_performance_month_data[allocation.stock] = []
			portfolio_performance_years_data[allocation.stock] = []

			for performance in allocation.performances.all().order_by("date"):
				stock_price_history_day_data[allocation.stock].append(dict(x=performance.date.strftime("%Y-%m-%d"),
																		   y=str(performance.unit_value),
																		   x1=performance.date.strftime("%Y-%m-%d")))
				portfolio_performance_data[allocation.stock].append(dict(x=performance.date.strftime("%d/%m/%Y"),
																		 y=str(performance.unit_value * performance.allocation.quantity),
																		 x1=performance.date.strftime("%Y-%m-%d"),
																		 percentage= round(performance.percentage, 0),
																		 unit_value= str(performance.unit_value),
																		 quantity= performance.quantity))

				month = performance.date.strftime("%Y-%m")
				year = performance.date.strftime("%Y")

				#keep values only the last day of month
				if any(month in d.get('x1', '') for d in portfolio_performance_month_data[allocation.stock]):
					portfolio_performance_month_data[allocation.stock].pop()
				portfolio_performance_month_data[allocation.stock].append(dict(x=performance.date.strftime("%d/%m/%Y"),
																			   y=str(performance.unit_value * performance.allocation.quantity),
																			   x1=performance.date.strftime("%Y-%m-%d"),
																			   percentage= round(performance.percentage, 0),
																			   unit_value=str(performance.unit_value),
																			   quantity=performance.quantity))

				if any(month in d.get('x', '') for d in stock_price_history_month_data[allocation.stock]):
					stock_price_history_month_data[allocation.stock].pop()
				stock_price_history_month_data[allocation.stock].append(dict(x=performance.date.strftime("%Y-%m-%d"),
																			 y=str(performance.unit_value),
																			 x1=performance.date.strftime("%Y-%m-%d")))

				# keep values only the last day of year
				if any(year in d.get('x', '') for d in portfolio_performance_years_data[allocation.stock]):
					portfolio_performance_years_data[allocation.stock].pop()
				portfolio_performance_years_data[allocation.stock].append(dict(x=performance.date.strftime("%d/%m/%Y"),
																			   y=str(performance.unit_value * performance.allocation.quantity),
																			   x1=performance.date.strftime("%Y-%m-%d"),
																			   percentage= round(performance.percentage, 0),
																			   unit_value=str(performance.unit_value),
																			   quantity=performance.quantity))

				if any(year in d.get('x', '') for d in stock_price_history_year_data[allocation.stock]):
					stock_price_history_year_data[allocation.stock].pop()
				stock_price_history_year_data[allocation.stock].append(dict(x=performance.date.strftime("%Y-%m-%d"),
																			y=str(performance.unit_value),
																			x1=performance.date.strftime("%Y-%m-%d")))

				if not year in years:
					years.append((year))

	context = {}
	context['form'] = form
	context['formset'] = formset
	context['stock_price_history_day_data'] = json.dumps(stock_price_history_day_data)
	context['stock_price_history_month_data'] = json.dumps(stock_price_history_month_data)
	context['stock_price_history_year_data'] = json.dumps(stock_price_history_year_data)

	context['portfolio_performance_data'] = json.dumps(portfolio_performance_data)
	context['portfolio_performance_month_data'] = json.dumps(portfolio_performance_month_data)
	context['portfolio_performance_years_data'] = json.dumps(portfolio_performance_years_data)
	context['years'] = json.dumps(years)

	return render(request, 'portfolio.html', context)
