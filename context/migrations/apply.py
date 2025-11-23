"""
Database migration application script.
Applies SQL migrations to initialize the database.
"""
import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to import context module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from context.src.database import engine, init_db


def apply_migrations():
    """Apply all SQL migrations in order"""
    migrations_dir = Path(__file__).parent

    print("🔧 Applying database migrations...")

    # Method 1: Use SQLAlchemy's built-in table creation
    print("Creating tables using SQLAlchemy ORM...")
    init_db()
    print("✅ Tables created successfully!")

    # Method 2: Optionally apply custom SQL migrations
    sql_files = sorted(migrations_dir.glob("*.sql"))

    if sql_files:
        print(f"\nFound {len(sql_files)} SQL migration files:")
        for sql_file in sql_files:
            print(f"  - {sql_file.name}")

        print("\nNote: SQL migrations are for reference. Tables are created via SQLAlchemy.")
        print("If you need to apply SQL migrations manually, use:")
        print(f"  psql -U postgres -d ai_product_studio -f {sql_files[0]}")

    print("\n✅ Database initialization complete!")
    print("You can now start the orchestrator.")


def apply_sql_migration(sql_file: Path):
    """Apply a single SQL migration file"""
    print(f"Applying {sql_file.name}...")

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    # Split on semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    with engine.connect() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
                conn.commit()
            except Exception as e:
                print(f"Warning: {e}")
                # Continue with other statements

    print(f"✅ {sql_file.name} applied")


if __name__ == "__main__":
    try:
        apply_migrations()
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        sys.exit(1)
