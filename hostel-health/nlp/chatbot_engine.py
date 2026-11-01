import time
from nlp.safety_router import check_emergency
from nlp.intent_classifier import IntentClassifier
from nlp.faq_retriever import FAQRetriever
from nlp.preprocessor import clean_text

class ChatbotEngine:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.faq_retriever = FAQRetriever()
        # In-memory session tracking: session_id -> { history: [...], last_intent: str, last_topic: str, updated_at: float }
        self.sessions = {}

    def get_session(self, session_id: str) -> dict:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or "default_session"
            self.sessions[new_id] = {
                "history": [],
                "last_intent": None,
                "last_symptom": None,
                "updated_at": time.time()
            }
            return self.sessions[new_id]
        return self.sessions[session_id]

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def process_message(self, message: str, session_id: str = "default_session") -> dict:
        """
        Processes student input through the NLP pipeline:
        1. Normalization & validation
        2. Emergency safety routing (Priority Tier 1)
        3. Contextual multi-turn expansion
        4. Intent classification (Tier 2)
        5. Semantic FAQ retrieval (Tier 3)
        6. Response synthesis with metadata
        """
        session = self.get_session(session_id)
        cleaned = clean_text(message)

        if not cleaned:
            return {
                "response": "Please type a message describing your symptom, asking a health & safety question, or reporting a hostel issue.",
                "intent": "empty",
                "confidence": 0.0,
                "doctor_state": "normal",
                "is_urgent": False,
                "suggested_actions": [],
                "quick_replies": ["I have a fever", "Drinking water is dirty", "Emergency numbers", "Mess food complaint"]
            }

        # Step 1: Emergency Safety Router (Runs FIRST before any ML inference)
        emergency_check = check_emergency(cleaned)
        if emergency_check["is_emergency"]:
            session["last_intent"] = "medical_emergency"
            session["last_symptom"] = "emergency"
            session["history"].append({"user": message, "bot": emergency_check["response"], "urgent": True})
            return {
                "response": emergency_check["response"],
                "intent": "medical_emergency",
                "confidence": emergency_check["confidence"],
                "doctor_state": "urgent",
                "is_urgent": True,
                "suggested_actions": emergency_check["actions"],
                "quick_replies": ["Call Ambulance 108", "Call Local Auto", "Contact Warden"]
            }

        # Step 2: Multi-turn Context Resolution
        # Handle follow-up queries like "since this morning", "it hurts a lot", "what medicine?", "since yesterday"
        context_query = cleaned
        followup_signals = ["since", "yesterday", "morning", "night", "worse", "better", "hurts", "medicine", "pill", "tablet"]
        if session.get("last_symptom") and any(sig in cleaned for sig in followup_signals) and len(cleaned.split()) <= 6:
            context_query = f"{session['last_symptom']} {cleaned}"

        # Step 3: Intent Classification
        intent_result = self.intent_classifier.predict(context_query)
        intent = intent_result["intent"]
        intent_conf = intent_result["confidence"]

        # Step 4: Semantic FAQ Retrieval
        faq_match = self.faq_retriever.get_best_match(context_query)

        # Step 5: Response Synthesis
        doctor_state = "normal"
        is_urgent = False
        suggested_actions = []
        quick_replies = []

        # Update symptoms context if detected
        symptom_keywords = {
            "fever": "fever", "headache": "headache", "stomach": "stomach pain",
            "vomit": "vomiting", "diarrhea": "diarrhea", "cough": "cough cold",
            "burn": "burn", "sprain": "sprain", "cut": "cut bleeding"
        }
        for kw, symp in symptom_keywords.items():
            if kw in cleaned:
                session["last_symptom"] = symp
                break

        # Determine response logic
        if faq_match and faq_match["similarity"] >= 0.20:
            response_text = faq_match["answer"]
            doctor_state = "concerned" if faq_match.get("severity") in ["medium", "high"] else "normal"
            if faq_match.get("action") == "report_water":
                suggested_actions.append({"label": "Report Water Issue", "action": "open_complaint", "category": "Drinking Water"})
            elif faq_match.get("action") == "report_food":
                suggested_actions.append({"label": "Report Mess Food Issue", "action": "open_complaint", "category": "Food Hygiene"})
            elif faq_match.get("action") == "report_sanitation":
                suggested_actions.append({"label": "Report Washroom Issue", "action": "open_complaint", "category": "Washrooms & Sanitation"})
            elif faq_match.get("action") == "report_electrical":
                suggested_actions.append({"label": "Report Electrical Hazard", "action": "open_complaint", "category": "Electrical & Fire Safety"})
            elif faq_match.get("action") == "emergency":
                suggested_actions.append({"label": "Call Ambulance 108", "url": "tel:108", "type": "call", "urgent": True})
                doctor_state = "urgent"
                is_urgent = True

            quick_replies = ["View Health Guide", "Emergency Contacts", "Report an Issue"]

        elif intent == "symptom_information":
            doctor_state = "concerned"
            response_text = self.intent_classifier.get_response(intent)
            quick_replies = ["When to see doctor?", "First aid advice", "Emergency contacts"]
            suggested_actions.append({"label": "Campus Clinic Hours", "action": "clinic_info"})

        elif intent in ["water_quality_complaint", "food_safety_complaint", "sanitation_complaint", "electrical_fire_safety"]:
            doctor_state = "concerned"
            response_text = self.intent_classifier.get_response(intent)
            cat_map = {
                "water_quality_complaint": "Drinking Water",
                "food_safety_complaint": "Food Hygiene",
                "sanitation_complaint": "Washrooms & Sanitation",
                "electrical_fire_safety": "Electrical & Fire Safety"
            }
            category_name = cat_map.get(intent, "General Maintenance")
            suggested_actions.append({"label": f"File {category_name} Complaint", "action": "open_complaint", "category": category_name})
            quick_replies = ["Track my complaint", "Emergency Contacts", "Hostel safety rules"]

        elif intent == "emergency_contacts" or any(w in cleaned for w in ["auto", "cab", "taxi", "driver", "ambulance", "transport number"]):
            response_text = (
                "Here are your verified emergency transport contacts:\n\n"
                "• 🚑 Ambulance (Medical Emergency): 108\n"
                "• 🛺 Local Auto: +91 6379878266 (Local auto contact)\n"
                "• 🚕 City Cab: +91 82488 64404 (Local cab contact)\n\n"
                "Tap below to dial directly or view on the dashboard."
            )
            doctor_state = "normal"
            suggested_actions = [
                {"label": "Ambulance (108)", "url": "tel:108", "type": "call", "urgent": True},
                {"label": "Local Auto (+91 6379878266)", "url": "tel:+916379878266", "type": "call"},
                {"label": "City Cab (+91 8248864404)", "url": "tel:+918248864404", "type": "call"}
            ]
            quick_replies = ["Nearest hospital", "Campus clinic hours", "First aid tips"]

        elif intent == "complaint_status":
            response_text = self.intent_classifier.get_response(intent)
            suggested_actions.append({"label": "Open My Complaints", "action": "open_complaints_tab"})
            quick_replies = ["Report an Issue", "Hostel Warden contact", "Drinking water complaint"]

        elif intent in ["greeting", "goodbye", "hospital_info", "first_aid", "general_health", "general_hostel_safety"]:
            response_text = self.intent_classifier.get_response(intent)
            doctor_state = "normal"
            quick_replies = ["I have a fever", "Check drinking water", "Report an issue", "Emergency contacts"]

        else:
            # Fallback for unknown/unclear
            doctor_state = "normal"
            response_text = (
                "I didn't quite catch that. As your HostelCare AI assistant, I can help you with:\n"
                "• Health symptom guidance & first aid\n"
                "• Immediate emergency transport (Ambulance 108, Auto, Cab)\n"
                "• Hostel facility complaints (Water, Food, Washroom, Electrical)\n"
                "• Checking complaint status"
            )
            quick_replies = ["I have a fever", "Drinking water issue", "Emergency numbers", "Mess food complaint"]

        session["last_intent"] = intent
        session["history"].append({"user": message, "bot": response_text, "intent": intent})

        return {
            "response": response_text,
            "intent": intent,
            "confidence": intent_conf,
            "doctor_state": doctor_state,
            "is_urgent": is_urgent,
            "matched_faq_id": faq_match["id"] if faq_match else None,
            "faq_similarity": faq_match["similarity"] if faq_match else 0.0,
            "suggested_actions": suggested_actions,
            "quick_replies": quick_replies
        }
