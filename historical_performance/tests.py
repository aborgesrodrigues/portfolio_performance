from django.test import TestCase

# Create your tests here.
from historical_performance.forms import PortfolioForm, AllocationForm
from historical_performance.models import Portfolio


class PortfolioFormTests(TestCase):

	# Valid Form Data
	def test_valid(self):
		form = PortfolioForm(data={"username": "aborges",
		                           "start_date": "01/01/2016",
		                           "initial_balance": "10,000.0",
		                           "residual": "1,000.0"})
		self.assertTrue(form.is_valid(), "Should be valid")

		portfolio = form.save()
		self.assertTrue(portfolio.pk is not None, "Allocation saved by form")

	# Invalid Form Data
	def test_invalid(self):
		# validate required fields
		data = {"username": "", "start_date": "", "initial_balance": "", "residual": ""}
		form = PortfolioForm(data=data)
		self.assertFalse(form.is_valid(), "Fields required.")
		
		self.assertEqual(form.errors, {
			"username":  ["This field is required."],
			"start_date": ["This field is required."],
			"initial_balance": ["This field is required."],
			"residual": ["This field is required."],
		})



class AllocationTests(TestCase):
	def setUp(self):
		self.portfolio = Portfolio()
		self.portfolio.username = "aborges"
		self.portfolio.start_date = "2016-01-01"
		self.portfolio.initial_balance = 10000
		self.portfolio.residual = 0
		self.portfolio.save()

	# Valid Form Data
	def test_valid(self):
		form = AllocationForm(
			data={"allocations-0-portfolio": self.portfolio, 
			      "allocations-0-stock": "SNAP", 
			      "allocations-0-percentage": 100, 
			      "allocations-0-unit_value": 10, 
			      "allocations-0-quantity": 10,
			      "allocations-0-total": 10},
			prefix= "allocations-0")
		self.assertTrue(form.is_valid(), "Should be valid")
		print(form.errors)

		allocation = form.save()
		self.assertTrue(allocation.pk is not None, "Allocation saved by form")

	# Invalid Form Data
	def test_invalid(self):
		#validate required fields
		data = {"allocations-0-portfolio": "", 
		        "allocations-0-stock": "", 
		        "allocations-0-percentage": "", 
		        "allocations-0-unit_value": "",
		        "allocations-0-quantity": "",
		        "allocations-0-total": ""}
		form = AllocationForm(
			data=data,
			prefix= "allocations-0")
		self.assertFalse(form.is_valid(), "Fields required.")

		self.assertEqual(form.errors, {
			"portfolio": ["This field is required."],
			"stock":  ["This field is required."],
			"percentage": ["This field is required."],
			"unit_value": ["This field is required."],
			"quantity": ["This field is required."],
			"total": ["This field is required."],
		})

		#validate stock is valid
		form = AllocationForm(
			{"allocations-0-portfolio": self.portfolio,
			 "allocations-0-stock": "SNAP11",
			 "allocations-0-percentage": 100,
			 "allocations-0-unit_value": 10,
			 "allocations-0-quantity": 10,
			 "allocations-0-total": 10},
			prefix= "allocations-0")
		self.assertFalse(form.is_valid())

		self.assertEqual(form.errors, {
			"stock":  ["Stock symbol is not valid."],
			"__all__": ["Stock symbol is not valid."]
		})

		#validate percentage is valid
		form = AllocationForm(
			{"allocations-0-portfolio": self.portfolio,
			 "allocations-0-stock": "SNAP",
			 "allocations-0-percentage": 200,
			 "allocations-0-unit_value": 10,
			 "allocations-0-quantity": 10,
			 "allocations-0-total": 10},
			prefix= "allocations-0")
		self.assertFalse(form.is_valid())

		self.assertEqual(form.errors, {
			"percentage":  ["The percentage should be between 0 and 100."]
		})

