# rag_pipeline/retriever.py

import os
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class SimpleRetriever:
    def __init__(self, corpus_folder: str):
        """
        corpus_folder: path to a folder containing .txt files,
                       each representing a document.
        """
        self.corpus_folder = corpus_folder
        self.docs = []
        self.doc_names = []

        for filename in os.listdir(self.corpus_folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.corpus_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    self.docs.append(text)
                    self.doc_names.append(filename)

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.doc_vectors = self.vectorizer.fit_transform(self.docs)

    def retrieve_top_k(self, query: str, k: int = 2):
        """
        Returns top-k most relevant documents based on TF-IDF similarity.
        """
        query_vec = self.vectorizer.transform([query])
        scores = (query_vec * self.doc_vectors.T).toarray()[0]
        top_indices = np.argsort(scores)[::-1][:k]  
        results = []
        for idx in top_indices:
            doc_name = self.doc_names[idx]
            text = self.docs[idx]
            similarity = scores[idx]
            results.append({
                "doc_name": doc_name,
                "similarity": float(similarity),
                "text": text
            })
        return results
