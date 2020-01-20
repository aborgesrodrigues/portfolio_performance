from decimal import Decimal

from dal import autocomplete
from django.forms import inlineformset_factory
from django.contrib.admin import widgets
from django import forms

from historical_performance.models import Portfolio, Allocation
import requests
import json

from historical_performance.util import get_api_url


class BaseFormSet(forms.models.BaseInlineFormSet):
	def is_valid(self):
		return super(BaseFormSet, self).is_valid() and \
		       not any([bool(e) for e in self.errors])

	def clean(self):
		# get forms that actually have valid data
		count = 0
		percentage = 0
		for form in self.forms:
			try:
				if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
					count += 1
					percentage += form.cleaned_data.get('percentage', 0)
			except AttributeError:
				# annoyingly, if a subform is invalid Django explicity raises
				# an AttributeError for cleaned_data
				pass
		#should be informed at least one stock
		if count < 1:
			raise forms.ValidationError('Inform at least one stock.')
		#the total percenta should not be bigger than 100
		if percentage > 100:
			raise forms.ValidationError('The sum of the percentages should not be more than 100.')


class PortfolioForm(forms.ModelForm):
	start_date = forms.DateField(label='Start Date', help_text='dd/mm/yyyy',
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

	def clean_initial_balance(self):
		# format the initial balance value to a valid decimal value
		self.cleaned_data["initial_balance"] = Decimal(self.cleaned_data["initial_balance"].replace(",",""))

		return self.cleaned_data["initial_balance"]

	def clean_residual(self):
		#format the residual value to a valid decimal value
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
	total = forms.CharField(label="Total", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "#,##0.00", "placeholder": ""}))
	percentage = forms.IntegerField(label="Percentage", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "999", "placeholder": ""}))
	quantity = forms.IntegerField(label="Quantity", widget=forms.TextInput(
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
		#when using the autocomplete library the stock value is not in the self.cleaned_data variable
		if self.data.get("%s-stock" % (self.prefix), None):
			stock = self.data["%s-stock" % (self.prefix)]

			#Validate if the stock informed exist
			response = requests.get(get_api_url("stock_search") + "&search_term=%s&search_by=symbol&limit=50&page=1" % stock)
			json_response = json.loads(response.text)

			#the method clean_stock is not callend when using the autocomplete libray
			if json_response.get("total_returned") == 0:
				self.errors["stock"][0] = "Stock symbol is not valid."
				raise forms.ValidationError("Stock symbol is not valid.")
			else:
				self.fields['stock'].choices = [(stock, stock)]
				self.cleaned_data["stock"] = stock
				if self.errors.get("stock", None):
					del self.errors["stock"]

		return self.cleaned_data

	def clean_total(self):
		total = Decimal(self.cleaned_data["total"].replace(",",""))
		unit_value = self.cleaned_data["unit_value"]
		quantity = self.cleaned_data["quantity"]
		correct_total = unit_value * quantity

		if total != correct_total:
			raise forms.ValidationError("The total should be %s, %s found." % (correct_total, total))

		return total

	def clean_percentage(self):
		percentage = self.cleaned_data["percentage"]

		if percentage > 100:
			raise forms.ValidationError("The percentage should be between 0 and 100.")

		return percentage

	class Meta:
		model = Allocation
		exclude = ()


AllocationFormSet = inlineformset_factory(
    Portfolio, Allocation, formset=BaseFormSet, extra= 0, min_num=1, can_delete=True, form=AllocationForm
)