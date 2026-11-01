import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hostelcare_ai_super_secret_key_2026')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hostelcare.db')
    
    # Exact user-specified Emergency Contacts
    EMERGENCY_CONTACTS = {
        "ambulance": {
            "name": "Ambulance",
            "phone": "108",
            "description": "Medical emergency assistance",
            "urgent": True
        },
        "auto": {
            "name": "Local Auto",
            "phone": "+91 6379878266",
            "raw_phone": "+916379878266",
            "description": "Local auto contact",
            "urgent": False
        },
        "cab": {
            "name": "City Cab",
            "phone": "+91 82488 64404",
            "raw_phone": "+918248864404",
            "description": "Local cab contact",
            "urgent": False
        }
    }

    # Default administrative access
    DEFAULT_ADMIN_USER = os.environ.get('ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'HostelCare@2026')
