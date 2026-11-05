import json
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from nlp.preprocessor import clean_text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, 'dataset', 'intents.json')
REPORT_PATH = os.path.join(CURRENT_DIR, 'dataset', 'evaluation_report.json')

def run_evaluation():
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = []
    labels = []
    for item in data.get('intents', []):
        tag = item['tag']
        for pattern in item.get('patterns', []):
            cleaned = clean_text(pattern)
            if cleaned:
                texts.append(cleaned)
                labels.append(tag)

    print(f"Total samples: {len(texts)}, Unique classes: {len(set(labels))}")

    # Stratified Train-Test Split (75% train, 25% test)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
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

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)

    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    results = {
        "model_architecture": "TF-IDF (1-2 ngrams) + LogisticRegression(C=2.0, class_weight='balanced')",
        "total_samples": len(texts),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_classes": len(set(labels)),
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(p_macro), 4),
        "macro_recall": round(float(r_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_f1": round(float(f1_weighted), 4),
        "detailed_metrics": report_dict
    }

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print("\n--- CLASSIFICATION EVALUATION REPORT ---")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"Overall Accuracy: {acc:.2%}")
    print(f"Weighted F1: {f1_weighted:.4f}")
    print(f"Saved evaluation report to {REPORT_PATH}")
    return results

if __name__ == '__main__':
    run_evaluation()
