import pytest
from nlp.safety_router import check_emergency
from nlp.chatbot_engine import ChatbotEngine

def test_emergency_router_critical_patterns():
    # Cardiac emergency
    res1 = check_emergency("student has severe chest pain and cannot breathe")
    assert res1["is_emergency"] is True
    assert res1["doctor_state"] == "urgent"
    assert any("108" in act["label"] for act in res1["actions"])

    # Unconscious collapsed person
    res2 = check_emergency("someone collapsed in the wing corridor unconscious")
    assert res2["is_emergency"] is True
    assert res2["doctor_state"] == "urgent"

    # Non-emergency
    res3 = check_emergency("what time does the hostel mess close?")
    assert res3["is_emergency"] is False

def test_chatbot_engine_symptoms():
    engine = ChatbotEngine()
    res = engine.process_message("I have a fever and chills", session_id="test_symptom")
    assert res["intent"] in ["symptom_information", "medical_emergency"]
    assert res["doctor_state"] in ["concerned", "normal"]
    assert len(res["response"]) > 20

def test_chatbot_engine_multiturn():
    engine = ChatbotEngine()
    session_id = "test_multiturn_flow"
    engine.process_message("I have a bad headache", session_id=session_id)
    followup = engine.process_message("since yesterday morning", session_id=session_id)
    # Context should link headache to the follow-up
    assert followup["matched_faq_id"] == "faq_symptom_headache" or "headache" in followup["response"].lower()

def test_chatbot_engine_facility_complaint():
    engine = ChatbotEngine()
    res = engine.process_message("drinking water smells bad in cooler", session_id="test_comp")
    assert res["intent"] == "water_quality_complaint"
    assert any("Water" in act["label"] for act in res["suggested_actions"])

def test_chatbot_engine_emergency_contacts():
    engine = ChatbotEngine()
    res = engine.process_message("give me the ambulance and local auto number", session_id="test_contacts")
    assert "+91 6379878266" in res["response"]
    assert "+91 82488 64404" in res["response"]
    assert "108" in res["response"]
