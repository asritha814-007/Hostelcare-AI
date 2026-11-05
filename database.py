
import os
import sqlite3
import hashlib
import secrets
import datetime

from config import Config
from werkzeug.security import generate_password_hash, check_password_hash


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db_path() -> str:
    """Get the appropriate SQLite database path."""

    if os.environ.get("DATABASE_PATH"):
        return os.environ["DATABASE_PATH"]

    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = "/tmp/hostelcare.db"
        bundled_db = os.path.join(CURRENT_DIR, "hostelcare.db")

        if not os.path.exists(tmp_db) and os.path.exists(bundled_db):
            import shutil
            try:
                shutil.copyfile(bundled_db, tmp_db)
            except Exception as e:
                print(f"[Database] Could not copy initial database: {e}")

        return tmp_db

    return os.path.join(CURRENT_DIR, "hostelcare.db")


def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Securely hash a password using Werkzeug."""
    return generate_password_hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify new hashes and safely upgrade legacy hashes on login."""

    try:
        if check_password_hash(stored_hash, password):
            return True
    except (ValueError, TypeError):
        pass

    # Legacy SHA-256 verification for existing local admin accounts.
    legacy_salt = "hostelcare_salt_2026"
    legacy_hash = hashlib.sha256(
        (password + legacy_salt).encode("utf-8")
    ).hexdigest()

    return secrets.compare_digest(stored_hash, legacy_hash)


def init_db():
    """Create database tables and initialize admin if configured."""

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
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
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL
            )
        """)

        # Create an admin only when an environment password is configured.
        cursor.execute("SELECT COUNT(*) FROM admin_users")

        if cursor.fetchone()[0] == 0:
            default_admin = Config.DEFAULT_ADMIN_USER
            default_pass = Config.DEFAULT_ADMIN_PASS

            if default_pass:
                created_at = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()

                cursor.execute("""
                    INSERT INTO admin_users
                    (username, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    default_admin,
                    hash_password(default_pass),
                    "warden",
                    created_at
                ))

        # No fictional complaint records are inserted.

        conn.commit()

    finally:
        conn.close()


def generate_complaint_id() -> str:
    """Generate a unique complaint ID."""

    return f"HC-2026-{secrets.randbelow(9000) + 1000}"


def generate_tracking_pin() -> str:
    """Generate a four-digit tracking PIN."""

    return f"{secrets.randbelow(9000) + 1000}"


def create_complaint(
    category: str,
    description: str,
    location: str = "",
    student_name: str = "",
    student_contact: str = ""
) -> dict:

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        now_str = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M")

        # Retry if a randomly generated complaint ID already exists.
        for _ in range(10):
            complaint_id = generate_complaint_id()
            tracking_pin = generate_tracking_pin()

            try:
                cursor.execute("""
                    INSERT INTO complaints (
                        id, tracking_pin, category, description,
                        location, student_name, student_contact,
                        status, admin_notes, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Submitted', NULL, ?, ?)
                """, (
                    complaint_id,
                    tracking_pin,
                    category,
                    description,
                    location,
                    student_name,
                    student_contact,
                    now_str,
                    now_str
                ))
                break

            except sqlite3.IntegrityError:
                if _ == 9:
                    raise
        else:
            raise RuntimeError("Could not generate a unique complaint ID.")

        conn.commit()

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

    finally:
        conn.close()


def get_complaint_by_id(
    complaint_id: str,
    pin: str = None
) -> dict | None:

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        if pin:
            cursor.execute("""
                SELECT * FROM complaints
                WHERE id = ? AND tracking_pin = ?
            """, (complaint_id.strip(), pin.strip()))
        else:
            cursor.execute("""
                SELECT * FROM complaints WHERE id = ?
            """, (complaint_id.strip(),))

        row = cursor.fetchone()
        return dict(row) if row else None

    finally:
        conn.close()


def get_complaints(
    category: str = None,
    status: str = None,
    search: str = None,
    limit: int = 50,
    offset: int = 0
) -> list[dict]:

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        query = "SELECT * FROM complaints WHERE 1=1"
        params = []

        if category and category.lower() != "all":
            query += " AND category = ?"
            params.append(category)

        if status and status.lower() != "all":
            query += " AND status = ?"
            params.append(status)

        if search:
            query += """
                AND (
                    id LIKE ? OR description LIKE ?
                    OR location LIKE ? OR student_name LIKE ?
                )
            """
            wildcard = f"%{search}%"
            params.extend([wildcard] * 4)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


def get_dashboard_complaints(limit: int = 5) -> list[dict]:
    """Return a minimal complaint summary for the dashboard."""

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, category, status, created_at, location
            FROM complaints
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


def update_complaint_status(
    complaint_id: str,
    new_status: str,
    admin_notes: str = None
) -> bool:

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        now_str = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M")

        if admin_notes is not None:
            cursor.execute("""
                UPDATE complaints
                SET status = ?, admin_notes = ?, updated_at = ?
                WHERE id = ?
            """, (
                new_status,
                admin_notes,
                now_str,
                complaint_id
            ))
        else:
            cursor.execute("""
                UPDATE complaints
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (
                new_status,
                now_str,
                complaint_id
            ))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


def get_stats() -> dict:
    """Return complaint statistics."""

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM complaints
            WHERE status IN ('Submitted', 'In Progress')
        """)
        pending = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM complaints
            WHERE status = 'Resolved'
        """)
        resolved = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM complaints
            WHERE category IN (
                'Electrical & Fire Safety',
                'Drinking Water'
            )
            AND status != 'Resolved'
        """)
        open_safety = cursor.fetchone()[0]

        return {
            "total_complaints": total,
            "pending_complaints": pending,
            "resolved_complaints": resolved,
            "open_safety_reports": open_safety,
            "health_resources_count": 17
        }

    finally:
        conn.close()


def verify_admin(username: str, password: str) -> bool:
    """Verify admin login and upgrade legacy password hashes."""

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, password_hash
            FROM admin_users
            WHERE username = ?
        """, (username,))

        row = cursor.fetchone()

        if not row:
            return False

        stored_hash = row["password_hash"]

        if not verify_password(stored_hash, password):
            return False

        # Upgrade legacy hash after successful verification.
        if len(stored_hash) == 64:
            cursor.execute("""
                UPDATE admin_users
                SET password_hash = ?
                WHERE id = ?
            """, (
                hash_password(password),
                row["id"]
            ))
            conn.commit()

        return True

    finally:
        conn.close()

