from django.test import TestCase
import datetime

# Create your tests here.
from historical_performance.forms import PortfolioForm, AllocationForm, AllocationFormSet
from historical_performance.models import Portfolio, Allocation, PerformancePortfolio


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
		self.portfolio.start_date = datetime.datetime.strptime("2016-01-01", "%Y-%m-%d")
		self.portfolio.initial_balance = 10000
		self.portfolio.residual = 0
		self.portfolio.save()

		self.empty_data = {"allocations-0-portfolio": "",
		        "allocations-0-stock": "",
		        "allocations-0-percentage": "",
		        "allocations-0-unit_value": "",
		        "allocations-0-quantity": "",
		        "allocations-0-total": ""}

		self.data = {"allocations-0-portfolio": self.portfolio,
			      "allocations-0-stock": "SNAP",
			      "allocations-0-percentage": 100,
			      "allocations-0-unit_value": 10,
			      "allocations-0-quantity": 10,
			      "allocations-0-total": 100}

	# Valid Form Data
	def test_valid(self):
		form = AllocationForm(
			data= self.data,
			prefix= "allocations-0")
		self.assertTrue(form.is_valid(), "Should be valid")

		allocation = form.save()
		self.assertTrue(allocation.pk is not None, "Allocation saved by form")

	#Required fields
	def test_required_fields(self):

		form = AllocationForm(
			data=self.empty_data,
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

	# Stock is valid
	def test_valid_stock(self):
		data = self.data
		data["allocations-0-stock"] = "SNAP11"
		form = AllocationForm(
			data = data,
			prefix= "allocations-0")
		self.assertFalse(form.is_valid(), "Should be invalid")

		self.assertEqual(form.errors, {
			"stock":  ["Stock symbol is not valid."],
			"__all__": ["Stock symbol is not valid."]
		})

	#Percentage is in a valid range
	def test_valid_percentage(self):
		data = self.data
		data["allocations-0-percentage"] = 200
		form = AllocationForm(
			data= data,
			prefix= "allocations-0")
		self.assertFalse(form.is_valid())

		self.assertEqual(form.errors, {
			"percentage":  ["The percentage should be between 0 and 100."]
		})

	#Total is equal unit_value x quantity
	def test_valid_total(self):
		data = self.data
		data["allocations-0-total"] = 200
		form = AllocationForm(
			data= data,
			prefix= "allocations-0")
		self.assertFalse(form.is_valid())

		correct_total = self.data.get("allocations-0-unit_value") * self.data.get("allocations-0-quantity")

		self.assertEqual(form.errors, {
			"total":  ["The total should be %s, %s found." % (correct_total, self.data.get("allocations-0-total"))]
		})


class AllocationFormSetTests(TestCase):

	def setUp(self):
		self.portfolio = Portfolio()
		self.portfolio.username = "aborges"
		self.portfolio.start_date = datetime.datetime.strptime("2016-01-01", "%Y-%m-%d")
		self.portfolio.initial_balance = 10000
		self.portfolio.residual = 0
		self.portfolio.save()

		self.empty_data = {
			'allocations-TOTAL_FORMS': 0,
			'allocations-INITIAL_FORMS': 0,
			'allocations-MIN_NUM_FORMS': 1,
			'allocations-MAX_NUM_FORMS': 1000
		}

		self.data = {
            'allocations-0-portfolio': self.portfolio,
            'allocations-0-stock': "SNAP",
            'allocations-0-percentage': 50,
            'allocations-0-unit_value': 10,
            'allocations-0-quantity': 10,
			'allocations-0-total': 100,
			'allocations-TOTAL_FORMS': 2,
			'allocations-1-portfolio': self.portfolio,
			'allocations-1-stock': "SNAP",
			'allocations-1-percentage': 60,
			'allocations-1-unit_value': 20,
			'allocations-1-quantity': 10,
			'allocations-1-total': 200,
			'allocations-INITIAL_FORMS': 0,
			'allocations-MIN_NUM_FORMS': 1,
			'allocations-MAX_NUM_FORMS': 1000
		}

	#At least one form is informed
	def test_required(self):
		formset = AllocationFormSet(instance= self.portfolio, data=self.empty_data)

		self.assertFalse(formset.is_valid())

		self.assertEqual(formset.non_form_errors(), ["Inform at least one stock."])

	#Total of percentages is in a valid rante
	def test_total_percentage(self):
		formset = AllocationFormSet(instance= self.portfolio, data=self.data)

		self.assertFalse(formset.is_valid())

		self.assertEqual(formset.non_form_errors(), ["The sum of the percentages should not be more than 100."])


class PortfolioTest(TestCase):

	#username is slugify
	def test_username(self):
		portfolio = Portfolio()
		portfolio.username = "Alessandro Borges"
		portfolio.start_date = datetime.datetime.strptime("2016-01-01", "%Y-%m-%d")
		portfolio.initial_balance = 10000
		portfolio.residual = 0
		portfolio.save()

		self.assertEqual(portfolio.username, "alessandro-borges")

	def test_percentage(self):
		#add portfolio
		portfolio = Portfolio()
		portfolio.username = "Alessandro Borges"
		portfolio.start_date = datetime.datetime.strptime("2016-01-01", "%Y-%m-%d")
		portfolio.initial_balance = 4782.8
		portfolio.residual = 0
		portfolio.save()

		#add allocation
		allocation = Allocation()
		allocation.portfolio = portfolio
		allocation.stock = "ASNA"
		allocation.unit_value = 217.4
		allocation.quantity = 22
		allocation.percentage = 50
		allocation.save()

		#add performance
		performance_portfolio = PerformancePortfolio()
		performance_portfolio.allocation = allocation
		performance_portfolio.unit_value = 215.4
		performance_portfolio.quantity = allocation.quantity
		performance_portfolio.percentage = 0
		performance_portfolio.date = datetime.datetime.strptime("2016-01-06", "%Y-%m-%d")
		performance_portfolio.save()

		# add allocation
		allocation = Allocation()
		allocation.portfolio = portfolio
		allocation.stock = "CGOOF"
		allocation.unit_value = 1.15
		allocation.quantity = 2608
		allocation.percentage = 30
		allocation.save()

		# add performance
		performance_portfolio = PerformancePortfolio()
		performance_portfolio.allocation = allocation
		performance_portfolio.unit_value = 1.23
		performance_portfolio.quantity = allocation.quantity
		performance_portfolio.percentage = 0
		performance_portfolio.date = datetime.datetime.strptime("2016-01-06", "%Y-%m-%d")
		performance_portfolio.save()

		# add allocation
		allocation = Allocation()
		allocation.portfolio = portfolio
		allocation.stock = "APPF"
		allocation.unit_value = 13.95
		allocation.quantity = 143
		allocation.percentage = 20
		allocation.save()

		# add performance
		performance_portfolio = PerformancePortfolio()
		performance_portfolio.allocation = allocation
		performance_portfolio.unit_value = 13.94
		performance_portfolio.quantity = allocation.quantity
		performance_portfolio.percentage = 0
		performance_portfolio.date = datetime.datetime.strptime("2016-01-06", "%Y-%m-%d")
		performance_portfolio.save()

		#calculate percentages
		PerformancePortfolio.calculate_percentage(portfolio)

		performance_asna = PerformancePortfolio.objects.get(allocation__stock= "ASNA")
		performance_cgoof = PerformancePortfolio.objects.get(allocation__stock="CGOOF")
		performance_appf = PerformancePortfolio.objects.get(allocation__stock="APPF")

		self.assertEqual([round(performance_asna.percentage),
		                  round(performance_cgoof.percentage),
		                  round(performance_appf.percentage)], [48, 32, 20])

