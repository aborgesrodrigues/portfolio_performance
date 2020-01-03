from dal import autocomplete
from django.forms import inlineformset_factory
from django.contrib.admin import widgets
from django import forms

from historical_performance.models import Portfolio, Allocation


class PortfolioForm(forms.ModelForm):
	start_date = forms.DateField(label='Start Date', help_text='dd/mm/aaaa',
	                                      widget=widgets.AdminDateWidget(
		                                      attrs={'mask': '99/99/9999', 'pattern': '[0-9]{2}/[0-9]{2}/[0-9]{4}',
		                                             'style': 'width:120px'}))
	initial_balance = forms.CharField(label='Initial Balance', widget=forms.TextInput(
		attrs={"style": "width:100px", "mask":"#,##0.00", "placeholder": ""}))
	residual = forms.CharField(label='Residual', widget=forms.TextInput(
		attrs={"style": "width:100px", "mask":"#,##0.00", "placeholder": "", "disabled": ""}))

	class Meta:
		model = Portfolio
		fields = ("username", "start_date", "initial_balance", "residual")
		exclude = ("created_at",)


class AllocationForm(forms.ModelForm):
	unit_value = forms.DecimalField(label="Unit Value", widget=forms.TextInput(attrs={"style": "width:100px", "mask":"'#,##0.00'", "placeholder": ""}))
	stock = forms.CharField(
		widget=autocomplete.ListSelect2(url='stock-autocomplete', attrs={'data-minimum-input-length': 3, 'class': 'form-control', "style": "width: 100px"}))
	desired_percentage = forms.DecimalField(label="Desired Percentage", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "'#,##0.00'", "placeholder": ""}))
	percentage = forms.DecimalField(label="Real Percentage", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "'#,##0.00'", "placeholder": ""}))
	quantity = forms.IntegerField(label="Quantity", widget=forms.TextInput(
		attrs={"style": "width:100px", "mask": "'#,##0.00'", "placeholder": ""}))

	class Meta:
		model = Allocation
		exclude = ()


AllocationFormSet = inlineformset_factory(
    Portfolio, Allocation, extra=0, can_delete=True, form=AllocationForm, min_num=1
)