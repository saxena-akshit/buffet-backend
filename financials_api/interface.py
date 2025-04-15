# from .retriever import SimpleRetriever
# from .generator import T5Generator

import os

# CORPUS_FOLDER = os.path.join(os.path.dirname(__file__), "data")

# retriever = SimpleRetriever(corpus_folder=CORPUS_FOLDER)
# generator = T5Generator(model_name="t5-small")

def answer_question(query: str, k: int = 2) -> dict:
    """
    1) Retrieve top-k relevant documents 
    2) Combine them into a prompt
    3) Generate an answer
    4) Return the result
    """
    # top_docs = retriever.retrieve_top_k(query, k=k)

    # context_str = "\n".join([doc["text"] for doc in top_docs])
    # prompt = f"question: {query}\ncontext: {context_str}\nanswer:"

    # answer = generator.generate(prompt)

    # return {
    #     "question": query,
    #     "answer": answer.strip(),
    #     "retrieved_docs": top_docs
    # }
    
    return {}
