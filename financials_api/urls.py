from django.urls import path

from financials_api.views.chatbot_views import ChatbotView
from financials_api.views.financial_views import FinancialDataView
from financials_api.views.rag_view import RAGView

urlpatterns = [
    path('financials/<str:stock_symbol>/', FinancialDataView.as_view(), name='financial-data'),
    path('ask/', RAGView.as_view(), name='rag-ask'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]
