import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nlp.preprocessor import clean_text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FAQS_PATH = os.path.join(CURRENT_DIR, 'dataset', 'faqs.json')

class FAQRetriever:
    def __init__(self, faqs_path=FAQS_PATH, similarity_threshold=0.18):
        self.faqs_path = faqs_path
        self.similarity_threshold = similarity_threshold
        self.faqs = []
        self.vectorizer = None
        self.faq_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        with open(self.faqs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.faqs = data.get('faqs', [])

        # Create corpus combining question (boosted), keywords (boosted), category, and answer snippet
        corpus = []
        for faq in self.faqs:
            kw_str = ' '.join(faq.get('keywords', []))
            q_str = faq.get('question', '')
            text_components = [
                q_str, q_str,  # question doubled for weight
                kw_str, kw_str,  # keywords doubled for weight
                faq.get('category', ''),
                faq.get('answer', '')[:140]
            ]
            corpus.append(clean_text(" ".join(text_components)))

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words='english'
        )
        self.faq_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Retrieves top matching FAQs using TF-IDF cosine similarity.
        Returns list of matched FAQ dictionaries with similarity score.
        """
        cleaned_query = clean_text(query)
        if not cleaned_query:
            return []

        query_vec = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vec, self.faq_matrix)[0]

        # Rank indices by score
        ranked_indices = similarities.argsort()[::-1]

        results = []
        for idx in ranked_indices[:top_k]:
            score = float(similarities[idx])
            faq_item = dict(self.faqs[idx])
            faq_item['similarity'] = round(score, 4)
            if score >= self.similarity_threshold:
                results.append(faq_item)

        return results

    def get_best_match(self, query: str) -> dict | None:
        matches = self.retrieve(query, top_k=1)
        if matches and matches[0]['similarity'] >= self.similarity_threshold:
            return matches[0]
        return None

    def get_all_faqs(self) -> list[dict]:
        return self.faqs
