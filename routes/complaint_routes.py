from flask import Blueprint, request, jsonify
from database import create_complaint, get_complaint_by_id, get_dashboard_complaints

complaint_bp = Blueprint('complaints', __name__)

VALID_CATEGORIES = [
    "Drinking Water",
    "Food Hygiene",
    "Washrooms & Sanitation",
    "Waste Disposal",
    "Pest Control",
    "Electrical & Fire Safety",
    "First-Aid Supplies",
    "General Maintenance"
]

@complaint_bp.route('/api/complaints', methods=['POST'])
def submit_complaint():
    data = request.get_json() or {}
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    location = data.get('location', '').strip()
    student_name = data.get('student_name', '').strip()
    student_contact = data.get('student_contact', '').strip()

    if not category:
        return jsonify({"success": False, "error": "Please select an issue category."}), 400

    if category not in VALID_CATEGORIES:
        return jsonify({"success": False, "error": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"}), 400

    if not description or len(description) < 8:
        return jsonify({"success": False, "error": "Please provide a detailed description (at least 8 characters)."}), 400

    record = create_complaint(
        category=category,
        description=description,
        location=location,
        student_name=student_name,
        student_contact=student_contact
    )

    return jsonify({
        "success": True,
        "message": f"Complaint registered successfully with ID {record['id']}",
        "data": record
    }), 201

@complaint_bp.route('/api/complaints/track', methods=['GET'])
def track_complaint():
    complaint_id = request.args.get('id', '').strip()
    pin = request.args.get('pin', '').strip()

    if not complaint_id:
        return jsonify({"success": False, "error": "Complaint ID is required."}), 400

    record = get_complaint_by_id(complaint_id, pin=pin if pin else None)
    if not record:
        return jsonify({"success": False, "error": "No matching complaint found. Please check your Complaint ID and PIN."}), 404

    # If pin was not supplied, return non-sensitive public progress data
    if not pin:
        return jsonify({
            "success": True,
            "data": {
                "id": record["id"],
                "category": record["category"],
                "status": record["status"],
                "created_at": record["created_at"],
                "location": record["location"],
                "admin_notes": record["admin_notes"] if record["status"] in ["In Progress", "Resolved"] else "Under review by hostel administration.",
                "requires_pin_for_full_details": True
            }
        })

    # If valid PIN provided, return complete details
    return jsonify({
        "success": True,
        "data": {
            "id": record["id"],
            "category": record["category"],
            "description": record["description"],
            "location": record["location"],
            "student_name": record["student_name"],
            "status": record["status"],
            "admin_notes": record["admin_notes"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"]
        }
    })

@complaint_bp.route('/api/complaints/recent', methods=['GET'])
def get_recent():
    limit = request.args.get('limit', 5, type=int)
    limit = min(max(1, limit), 20)
    records = get_dashboard_complaints(limit=limit)
    return jsonify({
        "success": True,
        "data": records
    })
