"""
FastAPI Backend Integration Tests for SchoolGPT
RSR Technologies
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["organization"] == "RSR Technologies"
    assert data["application"] == "SchoolGPT"

def test_demo_accounts_endpoint():
    response = client.get("/api/auth/demo-accounts")
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) >= 5
    roles = [a["role"] for a in accounts]
    assert "Super Admin" in roles
    assert "Principal" in roles
    assert "Student" in roles

def test_login_flow():
    response = client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "Super Admin"

def test_chat_query_authenticated():
    # Login as student
    login_res = client.post("/api/auth/login", json={"username": "student", "password": "password123"})
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    chat_res = client.post("/api/chat", json={"question": "What is the schools leave policy for students?"}, headers=headers)
    assert chat_res.status_code == 200
    result = chat_res.json()
    assert "answer" in result
    assert "sources" in result
    assert result["response_time"] >= 0.0
