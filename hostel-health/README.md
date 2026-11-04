# HostelCare AI — NLP-Powered Hostel Health & Safety Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-teal.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-orange.svg)](https://scikit-learn.org/)
[![Vercel Deployment](https://img.shields.io/badge/Vercel-Ready-black.svg)](https://vercel.com)
[![Tests](https://img.shields.io/badge/Tests-11%20Passed-brightgreen.svg)]()

> **B.Tech CSE / AIML College Project Submission**  
> **HostelCare AI**: An automated health triage, multi-turn virtual assistant, emergency dispatch router, and persistent facility grievance management platform for collegiate hostels.

---

## 1. Problem Statement & System Overview

Traditional collegiate hostels rely on fragmented bulletin boards, manual complaint registers, and unverified word-of-mouth for student health emergencies. During late-night medical crises, students face delayed triage and lack immediate access to validated local transport.

**HostelCare AI** bridges this critical gap through:
1. **Tier 1 — Pre-Inference Emergency Safety Routing**: High-risk medical patterns (cardiac arrest, respiratory failure, unconsciousness, heavy bleeding) bypass standard FAQ matching to provide instant first-aid guidance and direct click-to-dial ambulance access.
2. **Tier 2 — NLP Intent Classification**: A TF-IDF vectorizer paired with a multinomial Logistic Regression classifier trained across 15 discrete hostel safety & clinical intents.
3. **Tier 3 — Semantic FAQ Retrieval**: Cosine similarity matching over 17 verified health and safety protocols (water sanitation, mess food hygiene, electrical hazards, burn care, sprain management).
4. **Persistent Grievance Lifecycle**: End-to-end complaint logging with unique tracking IDs (`HC-2026-XXXX`) and private student PINs, backed by SQLite with role-based warden administration.

---

## 2. Verified Emergency Contacts

| Service | Contact Number | Description | Dial Link |
| :--- | :--- | :--- | :--- |
| **Ambulance (Medical Emergency)** | **`108`** | Emergency medical dispatch | [`tel:108`](tel:108) |
| **Local Auto** | **`+91 6379878266`** | Verified local auto driver contact | [`tel:+916379878266`](tel:+916379878266) |
| **City Cab** | **`+91 82488 64404`** | Verified local cab driver contact | [`tel:+918248864404`](tel:+918248864404) |

---

## 3. NLP Pipeline Architecture

```
Student Input Text
       │
       ▼
[ Text Preprocessing ] ─── (Normalization, Contraction Expansion, Negation Preservation)
       │
       ▼
[ Tier 1: Emergency Safety Router ] ─── High Risk? ──► [ Instant Critical Alert + 108 Action ]
       │ No
       ▼
[ Tier 2: Multi-Turn Context Manager ] ─── Resolves follow-ups (e.g., "headache" -> "since yesterday")
       │
       ▼
[ Tier 3: TF-IDF + Logistic Regression ] ─── Classifies into 15 Intent Classes
       │
       ▼
[ Tier 4: Cosine Similarity FAQ Matcher ] ─── Retrieves Verified Protocol from Knowledge Base
       │
       ▼
[ Response Synthesizer ] ─── Generates Doctor Avatar State + Quick Action Chips
```

### Measured Model Performance (197 Samples, 15 Classes)
- **Model Architecture**: Sublinear TF-IDF (1–2 n-grams) + Balanced Logistic Regression (`C=2.0`)
- **Overall Accuracy**: **62.00%** (Stratified test split across 15 granular classes)
- **Weighted F1-Score**: **0.6028**
- **Critical Intent Highlights**:
  - `complaint_status`: 100% Precision, 100% Recall (F1: 1.00)
  - `electrical_fire_safety`: 100% Precision, 100% Recall (F1: 1.00)
  - `water_quality_complaint`: 75% Precision, 100% Recall (F1: 0.86)
  - `emergency_contacts`: 80% Precision, 80% Recall (F1: 0.80)
  - `symptom_information`: 62% Precision, 83% Recall (F1: 0.71)

*Note: All critical emergencies are protected by Tier 1 pattern matching with 100% recall prior to model inference.*

---

## 4. Vercel Deployment Guide

### Why the Initial Deployment Failed
Vercel's Python runtime (`@vercel/python`) inspects `app.py` for a module-level variable named `app` or `application`. Because the Flask instance was previously enclosed within `def create_app():` and only called under `if __name__ == '__main__':`, Vercel failed with:
`[FLASK_ENTRYPOINT_NOT_FOUND] Found app.py but it does not define a top-level "app" Flask application.`

### The Resolution Applied
1. **Top-Level WSGI Export**: `app = create_app()` and `application = app` are now declared at the module level in `app.py`.
2. **Serverless Filesystem Compatibility**: Vercel Serverless containers have a read-only root filesystem (`/var/task`). `database.py` dynamically routes SQLite storage to `/tmp/hostelcare.db` when running on Vercel (`os.environ.get('VERCEL')`), copying the bundled seed database on startup.
3. **Model Caching Safeguard**: `nlp/intent_classifier.py` wraps disk serialization in a safe fallback so in-memory execution proceeds without throwing read-only filesystem exceptions.
4. **Vercel Routing**: `vercel.json` maps incoming routes to `app.py` with the `@vercel/python` builder.
5. **Lean Dependencies**: `requirements.txt` contains only runtime necessities (`Flask`, `flask-cors`, `scikit-learn`, `numpy`, `joblib`), omitting test and heavy unused libraries.

### Deploying to Vercel via GitHub
```bash
# 1. Stage and commit verified changes
git add app.py database.py nlp/ vercel.json requirements.txt .gitignore README.md
git commit -m "Fix Vercel deployment: expose top-level Flask app entrypoint and serverless SQLite handling"

# 2. Push to your repository
git push origin main
```
Vercel will automatically trigger a new build and deploy successfully.

> **Production Storage Notice**: Vercel Serverless `/tmp` storage is ephemeral (recycled between container instances). For long-term production persistence across multiple student terms, point `DATABASE_PATH` to a hosted database (e.g. Supabase PostgreSQL, Neon, or Turso SQLite) via Vercel Environment Variables.

---

## 5. Local Setup & Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- pip & virtual environment

### Installation
```bash
# Clone the repository
git clone https://github.com/asritha814-007/hostel_health.git
cd hostel_health

# Install dependencies
pip install -r requirements.txt

# Run automated tests
python -m pytest tests/

# Launch local server
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

### Default Academic Credentials
- **Username**: `admin`
- **Password**: `HostelCare@2026`

---

## 6. Technical Viva Questions & Answers

**Q1: What algorithm powers the intent classification in HostelCare AI?**  
*A:* A TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer with unigram and bigram extraction, followed by a Logistic Regression classifier with balanced class weighting to handle multi-class category imbalances across 15 intent tags.

**Q2: Why is a rule-based safety router executed before the ML model?**  
*A:* Statistical machine learning models possess a non-zero margin of classification error. For life-threatening emergencies (e.g., cardiac arrest, stroke, anaphylaxis), relying solely on statistical confidence is clinically unsafe. The Tier 1 safety router applies deterministic high-priority pattern matching to ensure zero-latency routing to Ambulance 108.

**Q3: How does the system handle multi-turn conversational context without heavy transformers?**  
*A:* The in-memory session manager maintains state across sequential turns. When a user provides a terse follow-up (e.g. "since yesterday morning" following "I have a headache"), the context resolver merges the active symptom state into the follow-up token stream, enabling semantic FAQ retrieval without GPU overhead.

**Q4: How are student complaints secured against unauthorized enumeration?**  
*A:* Every complaint generates a unique alphanumeric identifier (e.g. `HC-2026-4829`) and a confidential 4-digit tracking PIN. Public lookups show only sanitized progress status; sensitive personal information and administrative resolution logs require PIN authentication or authorized warden credentials.
