"""
SchoolGPT - Demonstration Data & User Seeder
Creates demo accounts for each role and indexes the 6 demo school documents.
RSR Technologies
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db import init_db
from database.models import get_user_by_username
from auth.authentication import register_user
from services.document_service import document_service
from scripts.generate_sample_docs import DOCS_CONTENT, OUTPUT_DIR, main as generate_docs

DEMO_USERS = [
    {
        "username": "admin",
        "email": "admin@rsrtechnologies.co.in",
        "full_name": "RSR Executive Administrator",
        "role": "Super Admin",
        "password": "AdminPassword123!"
    },
    {
        "username": "school_admin",
        "email": "admin@rsracademy.edu",
        "full_name": "Rajesh Kumar (School Admin)",
        "role": "School Administrator",
        "password": "SchoolAdmin123!"
    },
    {
        "username": "principal",
        "email": "principal@rsracademy.edu",
        "full_name": "Dr. Ananya Rao (Principal)",
        "role": "Principal",
        "password": "Principal123!"
    },
    {
        "username": "teacher_sharma",
        "email": "sharma.v@rsracademy.edu",
        "full_name": "Vikram Sharma (Senior Teacher)",
        "role": "Teacher",
        "password": "Teacher123!"
    },
    {
        "username": "student_aarav",
        "email": "aarav.patel@student.rsracademy.edu",
        "full_name": "Aarav Patel (Grade 10 Student)",
        "role": "Student",
        "password": "Student123!"
    },
    {
        "username": "parent_priya",
        "email": "priya.patel@gmail.com",
        "full_name": "Priya Patel (Parent)",
        "role": "Parent",
        "password": "Parent123!"
    }
]

DOC_FILES = [
    ("Student_Handbook.pdf", "student_handbook"),
    ("Student_Leave_Policy.pdf", "leave_policy"),
    ("Admission_Policy.docx", "admission_policy"),
    ("School_Fee_Structure.pdf", "fee_structure"),
    ("Examination_Schedule.txt", "examination_schedule"),
    ("School_Transport_Policy.pdf", "transport_policy")
]

def seed():
    print("=" * 60)
    print("Initializing SchoolGPT Database...")
    init_db()

    print("\nRegistering Demo User Accounts...")
    admin_id = 1
    for u in DEMO_USERS:
        existing = get_user_by_username(u["username"])
        if existing:
            print(f"  • User '{u['username']}' ({u['role']}) already exists.")
            if u["role"] == "Super Admin":
                admin_id = existing["id"]
        else:
            ok, msg = register_user(
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                role=u["role"],
                password=u["password"]
            )
            print(f"  • {msg} [{u['role']}] - Password: {u['password']}")

    # Ensure demo documents are generated on disk
    generate_docs()

    print("\nIngesting and Indexing Demo Documents into ChromaDB...")
    for filename, key in DOC_FILES:
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            print(f"  ⚠️ Warning: {filename} not found.")
            continue

        meta = DOCS_CONTENT[key]
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        ok, msg, doc_id = document_service.process_and_index_document(
            file_bytes=file_bytes,
            filename=filename,
            title=meta["title"],
            category=meta["category"],
            academic_year=meta["academic_year"],
            description=f"Official {meta['category']} document for demonstration testing.",
            allowed_roles=meta["allowed_roles"],
            uploaded_by_user_id=admin_id
        )
        print(f"  • {filename} -> {'SUCCESS' if ok else 'FAILED'}: {msg}")

    print("\n" + "=" * 60)
    print("DEMO SEEDING COMPLETE!")
    print("Ready to launch SchoolGPT!")
    print("=" * 60)

if __name__ == "__main__":
    seed()
