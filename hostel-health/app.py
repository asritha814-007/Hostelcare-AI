import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from database import init_db
from routes import chat_bp, complaint_bp, admin_bp, stats_bp

def create_app():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, static_folder=root_dir, static_url_path='')
    app.config.from_object(Config)

    # Enable CORS for development flexibility
    CORS(app)

    # Initialize SQLite database and default admin/sample records
    init_db()

    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(stats_bp)

    @app.route('/')
    def serve_index():
        return send_from_directory(root_dir, 'index.html')

    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "HostelCare AI Backend", "version": "1.0.0"}

    return app

if __name__ == '__main__':
    application = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f" HostelCare AI Server running on http://127.0.0.1:{port}")
    print(f" Default Admin: admin | Password: HostelCare@2026")
    print(f" Emergency Contacts: Ambulance: 108 | Auto: +91 6379878266 | Cab: +91 82488 64404")
    print(f"=======================================================\n")
    application.run(host='0.0.0.0', port=port, debug=False)
