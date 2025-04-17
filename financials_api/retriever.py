
import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class SimpleQARetriever:
    def __init__(self, corpus_path: str):
        self.corpus_path = corpus_path
        self.questions = []
        self.answers = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.question_vectors = None

        # print(f"Loading Q&A corpus from: {self.corpus_path}") # Minimal Comments
        try:
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, quotechar='"', delimiter=',', skipinitialspace=True)
                for i, row in enumerate(reader):
                    if len(row) == 2:
                        question, answer = row
                        self.questions.append(question.strip())
                        self.answers.append(answer.strip())

            if not self.questions:
                 print("Warning: No questions loaded from corpus.")
            else:
                 # print(f"Loaded {len(self.questions)} Q&A pairs.") # Minimal Comments
                 self.question_vectors = self.vectorizer.fit_transform(self.questions)
                 # print("TF-IDF Vectorizer fitted on questions.") # Minimal Comments

        except FileNotFoundError:
            print(f"Error: Corpus file not found at {self.corpus_path}")
            raise

    def retrieve_top_k(self, query: str, k: int = 3):
        results = []
        if self.question_vectors is None or not self.questions:
             return results

        try:
            query_vec = self.vectorizer.transform([query])
            scores = (query_vec * self.question_vectors.T).toarray()[0]
            num_docs = len(self.questions)
            actual_k = min(k, num_docs)
            # Ensure indices are within bounds if actual_k is 0
            if actual_k > 0:
                top_indices = np.argsort(scores)[::-1][:actual_k]
                for idx in top_indices:
                    results.append({
                        "doc_name": os.path.basename(self.corpus_path),
                        "similarity": float(scores[idx]),
                        "text": self.answers[idx], # Answer text for context
                        "matched_question": self.questions[idx]
                    })
            # else: handle case with no results if needed, currently returns empty list
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

        return results