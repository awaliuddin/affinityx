#!/usr/bin/env python
"""
Simple database initialization script.
Run this to create all tables in the database.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from context.src.database import init_db

if __name__ == "__main__":
    print("🔧 Initializing database...")
    print("Creating all tables...")

    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("\nYou can now start the orchestrator with:")
        print("  uvicorn orchestrator.src.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is set correctly in .env")
        print("  3. Database 'ai_product_studio' exists")
        sys.exit(1)
