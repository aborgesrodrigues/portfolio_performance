from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from historical_performance import views
from portfolio_performance import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('teste/', views.teste_view, name='teste_view'),
    path('', views.portfolio_view, name='portfolio_view'),
    path('<slug:stock>/<slug:date>', views.get_quotation, name='portfolio_view'),
    path('<slug:username>', views.portfolio_view, name='portfolio_view'),
    path('stock-autocomplete/', views.StockAutocomplete.as_view(), name='stock-autocomplete')
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.autodiscover()