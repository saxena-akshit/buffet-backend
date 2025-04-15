
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yfinance as yf
import pandas as pd
import numpy as np
from financials_api.interface import answer_question

class RAGView(APIView):
    """
    Example Django REST view that uses the RAG pipeline.
    """
    def get(self, request):
        query = request.GET.get('question', None)
        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = answer_question(query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
