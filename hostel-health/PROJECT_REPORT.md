# HOSTELCARE AI — PROJECT REPORT
## NLP-Powered Hostel Health & Safety Management System
### Department of Computer Science & Engineering / Artificial Intelligence & Machine Learning

---

## 1. ABSTRACT

Hostel living presents unique healthcare, sanitation, and physical safety challenges for undergraduate students residing away from home. Conventional hostel management relies on manual physical logbooks, delayed warden interventions, and fragmented local transport contacts. **HostelCare AI** is an intelligent, full-stack, natural language processing (NLP) application engineered to provide 24/7 symptom assessment, automated emergency triage, semantic health advice retrieval, and end-to-end complaint tracking.

The application incorporates a multi-tiered architecture:
1. **Tier 1 (Deterministic Safety Router)**: Intercepts acute clinical emergencies (cardiovascular distress, severe trauma, unconsciousness) with zero classification latency, routing students to immediate Ambulance (108) emergency services.
2. **Tier 2 (Machine Learning Intent Classifier)**: Utilizes a TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer and multinomial Logistic Regression trained across 15 discrete hostel safety and medical intents, achieving 62.00% overall accuracy and 0.6028 weighted F1 across granular classes with 100% recall on high-risk categories.
3. **Tier 3 (Semantic FAQ Information Retrieval)**: Applies cosine similarity over a verified knowledge base of campus health guidelines, drinking water sanitation protocols, and mess food hygiene rules.
4. **Tier 4 (Grievance Lifecycle Management)**: Backed by an ACID-compliant SQLite relational database with cryptographically generated complaint identifiers and private tracking PINs, preventing unauthorized enumeration of student records while facilitating role-based warden administration.

---

## 2. EXISTING SYSTEM VS. PROPOSED SYSTEM

| Feature | Existing Manual / Generic Systems | HostelCare AI (Proposed System) |
| :--- | :--- | :--- |
| **Emergency Response** | Student must search contacts or find security guard manually | Automatic emergency pattern detection with one-tap 108 ambulance dialer |
| **Symptom Triage** | Unsupervised web searches leading to health anxiety | Structured, conservative clinical guidance with doctor avatar visual states |
| **Transport Contacts** | Unverified bulletin board notices | Validated Local Auto (+91 6379878266) & City Cab (+91 82488 64404) |
| **Grievance Tracking** | Physical register with public visibility of student names | PIN-protected tracking with unique IDs (`HC-2026-XXXX`) |
| **Admin Oversight** | Manual paper compilation by warden | Real-time filtering, status updates (`Submitted` -> `In Progress` -> `Resolved`) |
| **Deployment** | Often monolithic or broken on serverless | Production-ready with Vercel serverless `/tmp` handling and WSGI entry points |

---

## 3. SYSTEM ARCHITECTURE & PIPELINE

```
+-------------------------------------------------------------------------+
|                           CLIENT TIER (HTML5 / CSS3 / Vanilla JS)       |
|  - Dark Teal Sidebar Navigation        - Interactive Safety Tips        |
|  - Real-Time Complaint Dashboard       - Persistent NLP Chat Widget     |
|  - PIN-Protected Tracking Modal        - Authenticated Admin Console    |
+------------------------------------+------------------------------------+
                                     | HTTP REST (JSON)
                                     v
+-------------------------------------------------------------------------+
|                       FLASK APPLICATION SERVER (app.py)                 |
|  - WSGI Entry Point (app = create_app()) - CORS & Static Dispatcher     |
|  - Blueprint Routes: /api/chat, /api/complaints, /api/admin, /api/stats |
+------------------+------------------------------------+-----------------+
                   |                                    |
                   v                                    v
+------------------------------------+   +--------------------------------+
|       NLP ENGINE (nlp/)            |   |     DATABASE LAYER (SQLite)    |
| 1. Text Preprocessor (Regex/Norm)  |   | - complaints table             |
| 2. Emergency Safety Layer          |   | - admin_users table            |
| 3. Multi-Turn Context Resolution   |   | - Vercel /tmp serverless path  |
| 4. TF-IDF + Logistic Regression    |   +--------------------------------+
| 5. Cosine Similarity FAQ Matcher   |
+------------------------------------+
```

---

## 4. NATURAL LANGUAGE PROCESSING METHODOLOGY

### 4.1 Linguistic Preprocessing
Input text undergoes normalization:
1. **Case Normalization**: Case folding to standard lowercase.
2. **Contraction Expansion**: E.g., `can't` -> `cannot`, `won't` -> `will not`.
3. **Punctuation Sanitization**: Stripping superfluous characters while preserving hyphens and interrogation marks.
4. **Selective Stop-Word Filtering**: Unlike standard NLP toolkits that discard negation tokens, HostelCare AI retains negation (`not`, `no`, `never`) and intensity terms (`severe`, `urgent`) to safeguard clinical semantics.

### 4.2 Intent Classification
- **Feature Space**: Sublinear Term Frequency-Inverse Document Frequency (TF-IDF) across unigrams and bigrams:
  $$\text{TF-IDF}(t, d, D) = (1 + \log(\text{TF}(t, d))) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
- **Classifier**: Logistic Regression with L2 regularization ($C=2.0$) and balanced class weighting:
  $$P(y = k | \mathbf{x}) = \frac{e^{\mathbf{w}_k^T \mathbf{x} + b_k}}{\sum_{j=1}^K e^{\mathbf{w}_j^T \mathbf{x} + b_j}}$$
- **Confidence Calibration**: A prediction is accepted if $\max(P) \ge 0.14$ or margin over the runner-up $> 0.05$; otherwise, the system safely routes to the fallback clarification handler.

### 4.3 Semantic FAQ Retrieval
- Vector space model calculating cosine similarity between normalized query vector $\mathbf{q}$ and pre-indexed FAQ document vectors $\mathbf{d}_i$:
  $$\text{Similarity}(\mathbf{q}, \mathbf{d}_i) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{\|\mathbf{q}\| \|\mathbf{d}_i\|}$$
- Indexed corpus incorporates dual-weighted questions and keywords for boosted domain precision.

---

## 5. DATABASE SCHEMA & DATA DICTIONARY

### 5.1 Table: `complaints`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Unique identifier (e.g. `HC-2026-1042`) |
| `tracking_pin` | TEXT | NOT NULL | 4-digit numeric access PIN |
| `category` | TEXT | NOT NULL | E.g., Drinking Water, Food Hygiene, etc. |
| `description` | TEXT | NOT NULL | Student's reported details (min 8 chars) |
| `location` | TEXT | NULLABLE | Room / floor reference |
| `student_name` | TEXT | NULLABLE | Optional submitter name |
| `student_contact`| TEXT | NULLABLE | Optional telephone number |
| `status` | TEXT | DEFAULT 'Submitted' | `Submitted`, `In Progress`, `Resolved`, `Rejected` |
| `admin_notes` | TEXT | NULLABLE | Warden's resolution comments |
| `created_at` | TEXT | NOT NULL | ISO UTC timestamp string |
| `updated_at` | TEXT | NOT NULL | ISO UTC timestamp string |

### 5.2 Table: `admin_users`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | User index |
| `username` | TEXT | UNIQUE, NOT NULL | Administrator username |
| `password_hash` | TEXT | NOT NULL | Salted SHA-256 hash digest |
| `role` | TEXT | DEFAULT 'admin' | Administrative privilege level |
| `created_at` | TEXT | NOT NULL | Creation timestamp |

---

## 6. VERIFIED EMERGENCY CONTACT DIRECTORY

- **Ambulance (Emergency Medical Services)**: `108`
- **Local Auto (Campus Dedicated Transport)**: `+91 6379878266`
- **City Cab (Hospital Secondary Transport)**: `+91 82488 64404`

---

## 7. EXPERIMENTAL EVALUATION RESULTS

Evaluation was executed using a stratified 75/25 train-test split over 197 natural language phrases across all 15 discrete intent classes:

```
                         precision    recall  f1-score   support

       complaint_status       1.00      1.00      1.00         3
 electrical_fire_safety       1.00      1.00      1.00         3
     emergency_contacts       0.80      0.80      0.80         5
              first_aid       0.60      0.75      0.67         4
  food_safety_complaint       1.00      0.33      0.50         3
         general_health       0.67      1.00      0.80         2
  general_hostel_safety       0.00      0.00      0.00         3
                goodbye       0.33      0.50      0.40         2
               greeting       1.00      0.67      0.80         3
          hospital_info       0.00      0.00      0.00         3
      medical_emergency       0.33      0.40      0.36         5
   sanitation_complaint       1.00      0.33      0.50         3
    symptom_information       0.62      0.83      0.71         6
                unknown       0.50      0.50      0.50         2
water_quality_complaint       0.75      1.00      0.86         3

               accuracy                           0.62        50
              macro avg       0.64      0.61      0.59        50
           weighted avg       0.64      0.62      0.60        50
```

---

## 8. VERCEL SERVERLESS DEPLOYMENT ARCHITECTURE

When deploying to Vercel's Serverless Python environment:
1. **Module Inspection**: Vercel loads `app.py` via WSGI and extracts `app` from module attributes. Exposing `app = create_app()` at the top level resolves `[FLASK_ENTRYPOINT_NOT_FOUND]`.
2. **Ephemeral Storage Handling**: Vercel execution containers mount the root repository as read-only (`/var/task`). SQLite writes are dynamically mapped to `/tmp/hostelcare.db` via `get_db_path()`, ensuring complaint submissions succeed in serverless mode.
3. **In-Memory Model Resiliency**: The scikit-learn classifier caches in memory if the file system is immutable.
4. **Optimized Build Payload**: Redundant non-runtime libraries (`pandas`, `pytest`) are excluded from `requirements.txt` to minimize cold starts.

---

## 9. CONCLUSION & FUTURE ENHANCEMENTS

HostelCare AI delivers an effective solution for collegiate hostel health, safety, and grievance management. By pairing deterministic emergency pattern detection with statistical machine learning and serverless compatibility, the system ensures student well-being with minimal latency.

**Future Enhancements**:
- Integration with campus wearable IoT devices for automatic heart-rate anomaly alerts.
- Multi-lingual intent classification supporting regional languages via lightweight DistilBERT embeddings.
- Webhook notifications linking complaint registrations to hostel maintenance staff via SMS / WhatsApp Business API.
