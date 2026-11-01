import json
import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from nlp.preprocessor import clean_text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, 'dataset', 'intents.json')
MODEL_DIR = os.path.join(CURRENT_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'intent_model.joblib')

class IntentClassifier:
    def __init__(self, dataset_path=DATASET_PATH):
        self.dataset_path = dataset_path
        self.pipeline = None
        self.intents_data = None
        self.responses_map = {}
        self._load_dataset()
        self._load_or_train()

    def _load_dataset(self):
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)
        for item in self.intents_data.get('intents', []):
            tag = item['tag']
            self.responses_map[tag] = item.get('responses', [])

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.pipeline = joblib.load(MODEL_PATH)
                return
            except Exception as e:
                print(f"[IntentClassifier] Model loading failed ({e}), retraining...")
        self.train()

    def train(self):
        texts = []
        labels = []
        for item in self.intents_data.get('intents', []):
            tag = item['tag']
            for pattern in item.get('patterns', []):
                cleaned = clean_text(pattern)
                if cleaned:
                    texts.append(cleaned)
                    labels.append(tag)

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
                lowercase=True
            )),
            ('clf', LogisticRegression(
                C=2.0,
                max_iter=1000,
                class_weight='balanced',
                random_state=42
            ))
        ])

        self.pipeline.fit(texts, labels)
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.pipeline, MODEL_PATH)
        print(f"[IntentClassifier] Trained on {len(texts)} samples across {len(set(labels))} classes.")
        return len(texts), len(set(labels))

    def predict(self, text: str) -> dict:
        """
        Predict the intent of input text.
        Returns dict with:
            intent (str): Predicted tag
            confidence (float): Probability score of top prediction
            all_scores (dict): Dictionary of intent -> probability
        """
        cleaned = clean_text(text)
        if not cleaned:
            return {"intent": "unknown", "confidence": 0.0, "all_scores": {}}

        probas = self.pipeline.predict_proba([cleaned])[0]
        classes = self.pipeline.classes_
        top_idx = int(np.argmax(probas))
        top_intent = classes[top_idx]
        top_confidence = float(probas[top_idx])

        # With 15 classes (random chance = 0.067), confidence >= 0.14 or a strong margin over 2nd runner-up indicates clear signal
        sorted_probas = sorted(probas, reverse=True)
        top_val = sorted_probas[0]
        second_val = sorted_probas[1] if len(sorted_probas) > 1 else 0.0

        if top_val < 0.14 and (top_val - second_val) < 0.05:
            top_intent = "unknown"

        scores_dict = {classes[i]: round(float(probas[i]), 4) for i in range(len(classes))}
        return {
            "intent": top_intent,
            "confidence": round(top_confidence, 4),
            "all_scores": scores_dict
        }

    def get_response(self, intent: str) -> str:
        responses = self.responses_map.get(intent, [])
        if responses:
            return responses[0]
        return "I am here to assist with health symptoms, emergency contacts, or hostel facility complaints."
