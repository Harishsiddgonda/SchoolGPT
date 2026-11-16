"""
FastAPI Backend Integration Tests for SchoolGPT
RSR Technologies
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.factory import seed_initial_data

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    seed_initial_data()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_api_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "service" in data
    assert "database" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["organization"] == "RSR Technologies"
    assert data["application"] == "SchoolGPT"

def test_demo_accounts_endpoint():
    response = client.get("/api/v1/auth/demo-accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) >= 5
    roles = [a["role"] for a in accounts]
    assert "Super Admin" in roles
    assert "Principal" in roles
    assert "Student" in roles

def test_login_flow():
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "Super Admin"

def test_chat_query_authenticated():
    # Login as student
    login_res = client.post("/api/v1/auth/login", json={"username": "student", "password": "password123"})
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    chat_res = client.post("/api/v1/chat", json={"question": "What is the schools leave policy for students?"}, headers=headers)
    assert chat_res.status_code == 200
    result = chat_res.json()
    assert "answer" in result
    assert "sources" in result
    assert result["response_time"] >= 0.0

def test_notifications_endpoint():
    login_res = client.post("/api/v1/auth/login", json={"username": "student", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    notif_res = client.get("/api/v1/notifications", headers=headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert len(notifs) >= 1

def test_spa_serving():
    # Browser request with Accept: text/html
    html_res = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers.get("content-type", "")
    assert "SchoolGPT" in html_res.text

    # Android user agent request
    android_res = client.get("/", headers={"User-Agent": "SchoolGPT-AndroidApp/2.5"})
    assert android_res.status_code == 200
    assert "SchoolGPT" in android_res.text
