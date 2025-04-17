
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..interface import answer_question as answer_question_rag

class RAGView(APIView):
    """ Handles chatbot requests using the RAG pipeline (TF-IDF + T5). """
    def post(self, request):
        query = request.data.get('message', None)
        if not query:
            return Response({"reply": "No query (message) provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = answer_question_rag(query)
            return Response({"reply": result.get("answer", "Could not generate answer from knowledge base.")}, status=status.HTTP_200_OK)
        except FileNotFoundError:
             print("Error: RAG corpus file not found.")
             return Response({"reply": "Error: RAG knowledge base not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Error in RAGView: {e}")
            return Response({"reply": "An error occurred processing the RAG request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# SAMPLE Qs

# {"message": "How do you determine if a stock is undervalued?"}
# {"message": "What is intrinsic value?"}