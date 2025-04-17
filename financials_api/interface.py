from .retriever import SimpleQARetriever
from .generator import T5Generator
import os

# Corrected path calculation assuming interface.py is in financials_api/
CORPUS_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CORPUS_FILENAME = "qa_corpus.csv"
CORPUS_FILE_PATH = os.path.join(CORPUS_DATA_DIR, CORPUS_FILENAME)

retriever = None
generator = None

try:
    retriever = SimpleQARetriever(corpus_path=CORPUS_FILE_PATH)
except FileNotFoundError:
    print(f"CRITICAL WARNING: Corpus file '{CORPUS_FILENAME}' not found in '{CORPUS_DATA_DIR}'. RAG endpoint will fail.")

try:
    generator = T5Generator(model_name="t5-small")
except Exception as e:
    print(f"CRITICAL WARNING: Failed to initialize T5 Generator: {e}. RAG endpoint will fail.")


def answer_question(query: str, k: int = 4) -> dict:
    if retriever is None or generator is None:
        return {"answer": "Error: RAG components not available."}

    top_docs = retriever.retrieve_top_k(query, k=k)

    if not top_docs:
        context_str = "No relevant context found."
    else:
        context_str = "\n".join([doc["text"] for doc in top_docs]) # Use answers as context

    prompt = f"question: {query}\ncontext: {context_str}\nanswer:"

    try:
        generated_answer = generator.generate(prompt)
    except Exception as e:
        print(f"Error during T5 generation: {e}")
        return {"answer": "Error generating answer from retrieved context."}

    return {"answer": generated_answer.strip()}