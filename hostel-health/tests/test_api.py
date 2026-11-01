import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"

def test_exact_contacts_endpoint(client):
    res = client.get('/api/contacts')
    assert res.status_code == 200
    data = res.get_json()["data"]
    # Verify exact user-specified numbers
    assert data["auto"]["phone"] == "+91 6379878266"
    assert data["cab"]["phone"] == "+91 82488 64404"
    assert data["ambulance"]["phone"] == "108"

def test_stats_endpoint(client):
    res = client.get('/api/stats')
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "total_complaints" in data
    assert "pending_complaints" in data
    assert "resolved_complaints" in data

def test_chat_api(client):
    res = client.post('/api/chat', json={"message": "I have an emergency chest pain", "session_id": "test_api_sess"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["is_urgent"] is True
    assert data["doctor_state"] == "urgent"

def test_complaint_submission_and_tracking(client):
    # Test submission
    post_res = client.post('/api/complaints', json={
        "category": "Drinking Water",
        "description": "2nd floor Block B water dispenser filter needs replacement.",
        "location": "Block B, Floor 2",
        "student_name": "Test Student",
        "student_contact": "+91 99999 88888"
    })
    assert post_res.status_code == 201
    post_data = post_res.get_json()["data"]
    complaint_id = post_data["id"]
    tracking_pin = post_data["tracking_pin"]
    assert complaint_id.startswith("HC-2026-")

    # Test tracking with PIN
    track_res = client.get(f'/api/complaints/track?id={complaint_id}&pin={tracking_pin}')
    assert track_res.status_code == 200
    track_data = track_res.get_json()["data"]
    assert track_data["category"] == "Drinking Water"
    assert track_data["status"] == "Submitted"

def test_admin_authentication_and_workflow(client):
    # Invalid login
    bad_login = client.post('/api/admin/login', json={"username": "admin", "password": "WrongPassword"})
    assert bad_login.status_code == 401

    # Valid login
    login_res = client.post('/api/admin/login', json={"username": "admin", "password": "HostelCare@2026"})
    assert login_res.status_code == 200
    token = login_res.get_json()["token"]

    # Access protected complaints list
    list_res = client.get('/api/admin/complaints', headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    complaints = list_res.get_json()["data"]
    assert len(complaints) > 0

    # Update status of first complaint
    first_id = complaints[0]["id"]
    update_res = client.patch(
        f'/api/admin/complaints/{first_id}/status',
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "In Progress", "admin_notes": "Technician dispatched on priority."}
    )
    assert update_res.status_code == 200
