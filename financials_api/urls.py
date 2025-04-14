from django.urls import path
from .views import FinancialDataView

urlpatterns = [
    path('financials/<str:stock_symbol>/', FinancialDataView.as_view(), name='financial-data'),
]