import unicodedata

from django.db import models

# Create your models here.
from django.utils.encoding import force_text

class Portfolio(models.Model):
	"""
	Class to persist Initial balance data
	"""

	username = models.CharField(max_length=255, verbose_name="Username", unique=True)
	start_date = models.DateField(verbose_name="Start Date")
	initial_balance = models.DecimalField(verbose_name="Initial Balance", max_digits=12, decimal_places=2)
	residual = models.DecimalField(verbose_name="Residual value", max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '{} - Start Date: {}'.format(self.username, self.start_date.strftime("%d/%m/%Y"))

	def save(self, *args, **kwargs):
		#normalize the username
		self.username = unicodedata.normalize('NFKC', force_text(self.username))

		super(Portfolio, self).save(*args, **kwargs)


class Allocation(models.Model):
	"""
	Class to persist Portfolio
	"""

	portfolio = models.ForeignKey(Portfolio, verbose_name="Portfolio", related_name='allocations', on_delete=models.PROTECT)
	stock = models.CharField(max_length=20, verbose_name="Stock")
	quantity = models.PositiveIntegerField(verbose_name="Quantity")
	percentage = models.PositiveIntegerField(verbose_name="Percentage")
	unit_value = models.DecimalField(verbose_name="Value", max_digits=8, decimal_places=2)

	def __str__(self):
		return self.stock

class PerformancePortfolio(models.Model):
	"""
	Class to persist daily performance of portifolio
	"""

	date = models.DateField(verbose_name="Date")
	allocation = models.ForeignKey(Allocation, verbose_name="Portfolio", related_name='performances', on_delete=models.PROTECT)
	unit_value = models.DecimalField(verbose_name="Value", max_digits=8, decimal_places=2)

	def __str__(self):
		return '{} - Date: {}'.format(self.portfolio.allocation, self.date.strftime("%d/%m/%Y"))