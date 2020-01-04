from django.shortcuts import render, get_object_or_404
from django.contrib import messages

# Create your views here.
from historical_performance.forms import PortfolioForm, AllocationFormSet
from historical_performance.models import Portfolio
from dal import autocomplete
import requests
import json

api = "https://api.worldtradingdata.com/api/v1/stock_search?api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG"

class StockAutocomplete(autocomplete.Select2ListView):

	def results(self, results):
		#Customizing the autuocomplete results
		response = requests.get(api + "&search_term=%s&search_by=symbol&limit=50&page=1" % self.q)
		if response.ok:
		    json_response = json.loads(response.text)

		    return [dict(id=stock.get("symbol"), text="%s - %s" % (stock.get("symbol", ""), stock.get("name", ""))) for stock in json_response.get("data")]
		else:
			return []

def portfolio_view(request, username= None):
	# If the username is passed get the data from de database
	initial_portfolio = None
	if username is not None:
		initial_portfolio = get_object_or_404(Portfolio, username=username)

	form = PortfolioForm(request.POST or None, instance=initial_portfolio)
	formset = AllocationFormSet(request.POST or None, instance=initial_portfolio)

	if form.is_valid():
		#Save portifolio data
		portifolio = form.save()

		#Save allocations data
		formset = AllocationFormSet(request.POST or None, instance=portifolio)
		if formset.is_valid():
			formset.save()

		#Save daily performance data
		#for allocation in portifolio.allocations.all()


		messages.success(request, 'Performance portfolio successfully added .')


	context = {}
	context['form'] = form
	context['formset'] = formset

	return render(request, 'portfolio.html', context)