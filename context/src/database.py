"""
Database connection and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Database URL from environment or default to SQLite for dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_product_studio"
)

# For testing, allow SQLite
if "pytest" in os.getenv("_", ""):
    DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO", False)),
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
