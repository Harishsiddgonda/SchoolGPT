"""
SchoolGPT - Initial Administrator Setup Script
RSR Technologies
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import init_db
from database.models import get_user_by_username
from auth.authentication import register_user

def setup_admin():
    print("Initializing SchoolGPT database...")
    init_db()

    username = "admin"
    email = "admin@rsrtechnologies.co.in"
    full_name = "System Administrator"
    role = "Super Admin"
    password = "AdminPassword123!"

    if get_user_by_username(username):
        print(f"User '{username}' already exists.")
        return

    ok, msg = register_user(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        password=password
    )

    if ok:
        print(f"SUCCESS: Super Admin created!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Role: {role}")
    else:
        print(f"FAILED: {msg}")

if __name__ == "__main__":
    setup_admin()
