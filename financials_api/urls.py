from django.urls import path
from .views import FinancialDataView, RAGView

urlpatterns = [
    path('financials/<str:stock_symbol>/', FinancialDataView.as_view(), name='financial-data'),
    path('ask/', RAGView.as_view(), name='rag-ask'),
]
