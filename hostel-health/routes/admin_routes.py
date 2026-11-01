import secrets
import time
from functools import wraps
from flask import Blueprint, request, jsonify
from database import verify_admin, get_complaints, update_complaint_status, get_stats

admin_bp = Blueprint('admin', __name__)

# Active session tokens: token -> { username: str, expires_at: float }
ADMIN_SESSIONS = {}
SESSION_DURATION_SECS = 24 * 3600  # 24 hours

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = ''
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1].strip()
        elif request.args.get('token'):
            token = request.args.get('token').strip()

        if not token or token not in ADMIN_SESSIONS:
            return jsonify({"success": False, "error": "Unauthorized. Admin session required."}), 401

        session_info = ADMIN_SESSIONS[token]
        if time.time() > session_info['expires_at']:
            del ADMIN_SESSIONS[token]
            return jsonify({"success": False, "error": "Admin session expired. Please sign in again."}), 401

        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required."}), 400

    if not verify_admin(username, password):
        return jsonify({"success": False, "error": "Invalid administrator credentials."}), 401

    token = secrets.token_hex(32)
    ADMIN_SESSIONS[token] = {
        "username": username,
        "role": "warden",
        "expires_at": time.time() + SESSION_DURATION_SECS
    }

    return jsonify({
        "success": True,
        "message": "Admin authenticated successfully",
        "token": token,
        "user": {
            "username": username,
            "role": "Hostel Warden / Administrator"
        }
    })

@admin_bp.route('/api/admin/verify', methods=['GET'])
@require_admin
def admin_verify():
    return jsonify({"success": True, "authenticated": True})

@admin_bp.route('/api/admin/complaints', methods=['GET'])
@require_admin
def list_admin_complaints():
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    limit = request.args.get('limit', 100, type=int)

    records = get_complaints(category=category, status=status, search=search, limit=limit)
    stats = get_stats()

    return jsonify({
        "success": True,
        "data": records,
        "stats": stats
    })

@admin_bp.route('/api/admin/complaints/<complaint_id>/status', methods=['PATCH'])
@require_admin
def update_status(complaint_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    admin_notes = data.get('admin_notes')

    valid_statuses = ["Submitted", "In Progress", "Resolved", "Rejected"]
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

    updated = update_complaint_status(complaint_id, new_status, admin_notes)
    if not updated:
        return jsonify({"success": False, "error": "Complaint not found or could not be updated."}), 404

    return jsonify({
        "success": True,
        "message": f"Complaint {complaint_id} updated to '{new_status}' successfully"
    })
