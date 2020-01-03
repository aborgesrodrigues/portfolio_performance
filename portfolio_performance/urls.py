from django.urls import path
from django.contrib import admin

from historical_performance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.portfolio_view, name='portfolio_view'),
    path('<slug:username>', views.portfolio_view, name='portfolio_view'),
    path('stock-autocomplete/', views.StockAutocomplete.as_view(), name='stock-autocomplete')
]
