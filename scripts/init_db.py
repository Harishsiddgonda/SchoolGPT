"""
Database Initialization Script for SchoolGPT
Initializes tables and enables pgvector extension on PostgreSQL.
RSR Technologies
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db import init_db
from backend.app.factory import seed_initial_data

if __name__ == "__main__":
    print("Initializing SchoolGPT Database...")
    init_db()
    print("Database schema successfully verified!")
    print("Seeding demo accounts and school documents...")
    seed_initial_data()
    print("Database initialization complete!")
