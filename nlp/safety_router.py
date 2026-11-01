import re

# High-risk clinical and environmental emergency regex patterns
EMERGENCY_PATTERNS = [
    # Cardiac / Cardiovascular
    r'\b(chest\s*pain|heart\s*attack|cardiac\s*arrest|heart\s*racing\s*pain|chest\s*tightness|crushing\s*chest)\b',
    # Respiratory distress
    r'\b(can(\'?)t\s*breathe|cannot\s*breathe|unable\s*to\s*breathe|suffocat(ing|ion)|severe\s*asthma|choking|gasping\s*for\s*air)\b',
    # Neurological / Consciousness
    r'\b(unconscious|passed\s*out|collapsed|fainted\s*and\s*not\s*waking|unresponsive|seizure|convulsion|stroke|slurred\s*speech\s*sudden|half\s*face\s*droop)\b',
    # Severe Trauma / Bleeding
    r'\b(heavy\s*bleed(ing)?|profuse\s*bleed(ing)?|blood\s*gushing|deep\s*wound\s*won(\'?)t\s*stop|arterial\s*bleed|stab|fracture\s*bone\s*sticking|head\s*trauma\s*vomiting)\b',
    # Severe Toxicology / Burns / Electric shock
    r'\b(swallowed\s*poison|drank\s*phenyl|chemical\s*ingestion|overdose|severe\s*electric\s*shock|electrocution|third\s*degree\s*burn|burn\s*all\s*over)\b',
    # Severe Allergic / Anaphylaxis
    r'\b(anaphylaxis|throat\s*swelling\s*shut|tongue\s*swollen\s*cannot\s*breathe|allergic\s*shock)\b',
    # Self-harm / Crisis
    r'\b(suicid(e|al)|kill\s*myself|end\s*my\s*life|want\s*to\s*die)\b'
]

# Secondary high-urgency keywords
URGENT_KEYWORDS = [
    'emergency', 'urgent', 'ambulance', 'collapsed', 'unconscious',
    'choking', 'poison', 'suffocating', 'severe bleeding', 'seizure'
]

EMERGENCY_RESPONSE_TEMPLATE = (
    "🚨 CRITICAL EMERGENCY ALERT 🚨\n\n"
    "This sounds like a potentially serious or life-threatening situation requiring IMMEDIATE medical intervention.\n\n"
    "Please take these immediate steps:\n"
    "1. 📞 Call Ambulance immediately: 108\n"
    "2. 🛺 Local Transport Options:\n"
    "   • Local Auto: +91 6379878266\n"
    "   • City Cab: +91 82488 64404\n"
    "3. 📢 Alert your hostel floor warden, roommate, or security guard immediately so someone is with you.\n"
    "4. Sit in a comfortable, safe position and do not exert yourself while help arrives."
)

def check_emergency(text: str) -> dict:
    """
    Evaluates text for critical safety risks before any intent classification or FAQ retrieval.
    Returns:
        dict with keys:
            is_emergency (bool): True if critical emergency patterns detected.
            confidence (float): 1.0 for hard rule match.
            trigger (str): Pattern or keyword that triggered the alert.
            response (str or None): Standard emergency advisory response.
            actions (list): Quick action suggestions for frontend.
    """
    if not text:
        return {"is_emergency": False, "confidence": 0.0, "trigger": None, "response": None, "actions": []}

    text_lower = text.lower().strip()

    # 1. Regex pattern check
    for pattern in EMERGENCY_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return {
                "is_emergency": True,
                "confidence": 1.0,
                "trigger": match.group(0),
                "response": EMERGENCY_RESPONSE_TEMPLATE,
                "doctor_state": "urgent",
                "actions": [
                    {"label": "Call Ambulance (108)", "url": "tel:108", "type": "call", "urgent": True},
                    {"label": "Call Local Auto", "url": "tel:+916379878266", "type": "call"},
                    {"label": "Call City Cab", "url": "tel:+918248864404", "type": "call"}
                ]
            }

    # 2. Urgent keywords check with context
    for kw in URGENT_KEYWORDS:
        if kw in text_lower:
            return {
                "is_emergency": True,
                "confidence": 0.95,
                "trigger": kw,
                "response": EMERGENCY_RESPONSE_TEMPLATE,
                "doctor_state": "urgent",
                "actions": [
                    {"label": "Call Ambulance (108)", "url": "tel:108", "type": "call", "urgent": True},
                    {"label": "Call Local Auto", "url": "tel:+916379878266", "type": "call"},
                    {"label": "Call City Cab", "url": "tel:+918248864404", "type": "call"}
                ]
            }

    return {
        "is_emergency": False,
        "confidence": 0.0,
        "trigger": None,
        "response": None,
        "doctor_state": "normal",
        "actions": []
    }
