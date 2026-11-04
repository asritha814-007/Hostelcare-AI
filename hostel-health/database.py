import sqlite3
import os
import hashlib
import secrets
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_db_path() -> str:
    # If explicit path provided in environment
    if os.environ.get('DATABASE_PATH'):
        return os.environ['DATABASE_PATH']
    # If running on Vercel or AWS Lambda serverless
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_db = '/tmp/hostelcare.db'
        bundled_db = os.path.join(CURRENT_DIR, 'hostelcare.db')
        if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
            import shutil
            try:
                shutil.copyfile(bundled_db, tmp_db)
            except Exception as e:
                print(f"[Database] Could not copy initial db to /tmp: {e}")
        return tmp_db
    return os.path.join(CURRENT_DIR, 'hostelcare.db')

def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    # SHA-256 hash with static salt for demonstration
    salt = "hostelcare_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Complaints table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        tracking_pin TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT,
        student_name TEXT,
        student_contact TEXT,
        status TEXT NOT NULL DEFAULT 'Submitted',
        admin_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    # Admin users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin',
        created_at TEXT NOT NULL
    )
    ''')

    # Seed default admin if none exists
    cursor.execute('SELECT COUNT(*) FROM admin_users')
    if cursor.fetchone()[0] == 0:
        default_admin = "admin"
        default_pass = "HostelCare@2026"
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute(
            'INSERT INTO admin_users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
            (default_admin, hash_password(default_pass), 'warden', created_at)
        )

    # If complaints is empty, seed 3 realistic baseline records so dashboard preview has clean initial data
    cursor.execute('SELECT COUNT(*) FROM complaints')
    if cursor.fetchone()[0] == 0:
        now = datetime.datetime.now(datetime.timezone.utc)
        sample_records = [
            (
                "HC-2026-101",
                "1234",
                "Drinking Water",
                "Water dispenser on 2nd floor Block A is dispensing murky water.",
                "Block A, Floor 2",
                "Rahul Sharma",
                "+91 98765 11223",
                "In Progress",
                "Maintenance technician assigned to replace RO filter cartridge.",
                (now - datetime.timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M"),
                (now - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")
            ),
            (
                "HC-2026-102",
                "5678",
                "Electrical & Fire Safety",
                "Fluorescent tube flickering and loose switchboard in corridor.",
                "Block C, Corridor East",
                "Ananya Patel",
                "+91 98765 44556",
                "Resolved",
                "Electrician replaced faulty switchboard socket and ballast. Tested safe.",
                (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            ),
            (
                "HC-2026-103",
                "9012",
                "Food Hygiene",
                "Mess dinner utensils had oil residue. Requested steam wash check.",
                "Dining Hall 1",
                "Sneha Rao",
                "+91 98765 77889",
                "Submitted",
                None,
                (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
            )
        ]
        cursor.executemany('''
        INSERT INTO complaints (id, tracking_pin, category, description, location, student_name, student_contact, status, admin_notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_records)

    conn.commit()
    conn.close()

def generate_complaint_id() -> str:
    # e.g. HC-2026-4829
    rand_num = secrets.randbelow(9000) + 1000
    return f"HC-2026-{rand_num}"

def generate_tracking_pin() -> str:
    return f"{secrets.randbelow(9000) + 1000}"

def create_complaint(category: str, description: str, location: str = "", student_name: str = "", student_contact: str = "") -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    complaint_id = generate_complaint_id()
    tracking_pin = generate_tracking_pin()
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    INSERT INTO complaints (id, tracking_pin, category, description, location, student_name, student_contact, status, admin_notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'Submitted', NULL, ?, ?)
    ''', (complaint_id, tracking_pin, category, description, location, student_name, student_contact, now_str, now_str))

    conn.commit()
    conn.close()

    return {
        "id": complaint_id,
        "tracking_pin": tracking_pin,
        "category": category,
        "description": description,
        "location": location,
        "student_name": student_name,
        "status": "Submitted",
        "created_at": now_str
    }

def get_complaint_by_id(complaint_id: str, pin: str = None) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()

    if pin:
        cursor.execute('SELECT * FROM complaints WHERE id = ? AND tracking_pin = ?', (complaint_id.strip(), pin.strip()))
    else:
        cursor.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id.strip(),))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def get_complaints(category: str = None, status: str = None, search: str = None, limit: int = 50, offset: int = 0) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM complaints WHERE 1=1'
    params = []

    if category and category.lower() != 'all':
        query += ' AND category = ?'
        params.append(category)

    if status and status.lower() != 'all':
        query += ' AND status = ?'
        params.append(status)

    if search:
        query += ' AND (id LIKE ? OR description LIKE ? OR location LIKE ? OR student_name LIKE ?)'
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

def get_dashboard_complaints(limit: int = 5) -> list[dict]:
    """Returns safe, minimal complaint summary for the public dashboard table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, category, status, created_at, location
    FROM complaints
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_complaint_status(complaint_id: str, new_status: str, admin_notes: str = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    if admin_notes is not None:
        cursor.execute('''
        UPDATE complaints
        SET status = ?, admin_notes = ?, updated_at = ?
        WHERE id = ?
        ''', (new_status, admin_notes, now_str, complaint_id))
    else:
        cursor.execute('''
        UPDATE complaints
        SET status = ?, updated_at = ?
        WHERE id = ?
        ''', (new_status, now_str, complaint_id))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_stats() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM complaints')
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Submitted' OR status = 'In Progress'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE category IN ('Electrical & Fire Safety', 'Drinking Water') AND status != 'Resolved'")
    open_safety = cursor.fetchone()[0]

    conn.close()

    return {
        "total_complaints": total,
        "pending_complaints": pending,
        "resolved_complaints": resolved,
        "open_safety_reports": open_safety,
        "health_resources_count": 17  # Number of verified health & safety guides
    }

def verify_admin(username: str, password: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM admin_users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False
    return row['password_hash'] == hash_password(password)
