import os
import sys

# Ensure project root directory is in sys.path for reliable module resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes import chat_bp, complaint_bp, admin_bp, stats_bp

# =========================================================================
# Top-Level Flask Application Instance (Vercel & WSGI Entry Point)
# =========================================================================
app = Flask(__name__, static_folder=CURRENT_DIR, static_url_path='')
app.config.from_object(Config)

# Enable CORS for cross-origin access and flexible deployment
CORS(app)

# Initialize SQLite database and default admin/sample records
try:
    init_db()
except Exception as e:
    print(f"[App Init] Database initialization notice: {e}")

# Register API blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(complaint_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(stats_bp)

# Static and Page Delivery Routes
@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_from_directory(CURRENT_DIR, 'index.html')

@app.route('/styles.css')
def serve_css():
    return send_from_directory(CURRENT_DIR, 'styles.css')

@app.route('/app.js')
def serve_js():
    return send_from_directory(CURRENT_DIR, 'app.js')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(CURRENT_DIR, 'assets'), filename)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "HostelCare AI Backend", "version": "1.0.0"})

# Factory function kept for test client and factory compatibility
def create_app():
    return app

# WSGI application alias
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f" HostelCare AI Server running on http://127.0.0.1:{port}")
    print(f" Default Admin: admin | Password: HostelCare@2026")
    print(f" Emergency Contacts: Ambulance: 108 | Auto: +91 6379878266 | Cab: +91 82488 64404")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
