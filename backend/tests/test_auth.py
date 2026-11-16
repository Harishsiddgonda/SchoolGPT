"""
SchoolGPT - Test Suite: Authentication & User Management
"""

import pytest
from database.db import init_db
from database.models import get_user_by_username, create_user
from auth.authentication import (
    hash_password,
    verify_password,
    authenticate_user,
    register_user,
    change_password
)
from auth.permissions import has_permission, can_access_document

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()

def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_user_registration_and_auth():
    test_uname = "test_teacher_unique"
    test_email = "test_teacher@rsracademy.edu"
    test_pwd = "TeacherPassword123!"

    # Clean existing
    existing = get_user_by_username(test_uname)
    if not existing:
        ok, msg = register_user(
            username=test_uname,
            email=test_email,
            full_name="Test Teacher",
            role="Teacher",
            password=test_pwd
        )
        assert ok is True

    # Authenticate valid
    user, err = authenticate_user(test_uname, test_pwd)
    assert user is not None
    assert user["username"] == test_uname
    assert user["role"] == "Teacher"
    assert "password_hash" not in user  # Security check: hash must be stripped

    # Authenticate invalid
    bad_user, bad_err = authenticate_user(test_uname, "InvalidPassword")
    assert bad_user is None
    assert "Invalid" in bad_err

def test_role_permissions():
    assert has_permission("Super Admin", "can_manage_users") is True
    assert has_permission("Super Admin", "can_upload_docs") is True
    assert has_permission("Principal", "can_view_analytics") is True
    assert has_permission("Student", "can_upload_docs") is False
    assert has_permission("Student", "can_manage_users") is False
    assert has_permission("Parent", "can_manage_users") is False

def test_document_access_control():
    allowed_roles = ["Super Admin", "School Administrator", "Principal"]
    assert can_access_document("Super Admin", allowed_roles) is True
    assert can_access_document("Principal", allowed_roles) is True
    assert can_access_document("Student", allowed_roles) is False
    assert can_access_document("Parent", allowed_roles) is False
