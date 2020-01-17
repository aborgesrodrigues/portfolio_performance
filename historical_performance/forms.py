from decimal import Decimal

from dal import autocomplete
from django.forms import inlineformset_factory
from django.contrib.admin import widgets
from django import forms

from historical_performance.models import Portfolio, Allocation
import requests
import json



class PortfolioForm(forms.ModelForm):
	start_date = forms.DateField(label='Start Date', help_text='dd/mm/aaaa',
	                                      widget=widgets.AdminDateWidget(
		                                      attrs={'mask': '99/99/9999', 'pattern': '[0-9]{2}/[0-9]{2}/[0-9]{4}',
		                                             'style': 'width:120px'}))
	initial_balance = forms.CharField(label='Initial Balance', widget=forms.TextInput(
		attrs={"style": "width:100px", "mask":"#,##0.00", "placeholder": ""}))
	residual = forms.CharField(label='Residual', widget=forms.TextInput(
		attrs={"style": "width:100px", "placeholder": "", "disabled": ""}))
	username = forms.CharField(label='Username', widget=forms.TextInput(
		attrs={"onkeyup": "slugify(this)", "onblur": "slugify(this)"}))

	def __init__(self, *args, **kwargs):
		super(PortfolioForm, self).__init__(*args, **kwargs)

		if self.instance.pk:
			self.fields['username'].widget.attrs['disabled'] = True
			self.fields["start_date"].initial = self.instance.start_date.strftime("%d/%m/%Y")

	def clean_initial_balance(self):
		self.cleaned_data["initial_balance"] = Decimal(self.cleaned_data["initial_balance"].replace(",",""))

		return self.cleaned_data["initial_balance"]

	def clean_residual(self):
		self.cleaned_data["residual"] = Decimal(self.cleaned_data["residual"].replace(",",""))

		return self.cleaned_data["residual"]

	class Meta:
		model = Portfolio
		fields = ("username", "start_date", "initial_balance", "residual")
		exclude = ("created_at",)


class AllocationForm(forms.ModelForm):
	unit_value = forms.DecimalField(label="Unit Value", widget=forms.TextInput(attrs={"style": "width:100px", "mask":"#,##0.00", "placeholder": ""}))
	stock = autocomplete.Select2ListChoiceField(
		widget=autocomplete.ListSelect2(url='stock-autocomplete', attrs={'data-minimum-input-length': 3, 'class': 'form-control'}))
	total = forms.CharField(required=False, label="Total", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "#,##0.00", "placeholder": ""}))
	percentage = forms.IntegerField(label="Percentage", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "999", "placeholder": ""}))
	quantity = forms.IntegerField(required=False, label="Quantity", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "#,##0.00", "placeholder": ""}))


	def __init__(self, *args, **kwargs):
		super(AllocationForm, self).__init__(*args, **kwargs)
		#The quantity, unit_value and total are automatically filled
		self.fields['quantity'].widget.attrs['disabled'] = True
		self.fields['total'].widget.attrs['disabled'] = True
		self.fields['unit_value'].widget.attrs['disabled'] = True

		if self.instance.pk:
			self.fields['stock'].choices = [(self.instance.stock, self.instance.stock)]


	def clean(self):
		stock = self.data["%s-stock" % (self.prefix)]

		#Validate if the stock informed exist
		response = requests.get("https://api.worldtradingdata.com/api/v1/stock_search?search_term=%s&search_by=symbol&limit=50&page=1&api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG" % stock)
		json_response = json.loads(response.text)

		if json_response.get("total_returned") == 0:
			raise forms.ValidationError("Stock symbol is not valid!")
		else:
			self.fields['stock'].choices = [(stock, stock)]
			self.cleaned_data["stock"] = stock
			if self._errors.get("stock", None):
				del self._errors["stock"]

		return self.cleaned_data

	class Meta:
		model = Allocation
		exclude = ()


AllocationFormSet = inlineformset_factory(
    Portfolio, Allocation, extra= 0, min_num=1, can_delete=True, form=AllocationForm
)