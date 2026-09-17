"""
Database Configuration and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://blueprint:blueprint_pass@localhost:5432/master_blueprint"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints
    Provides a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create tables)"""
    from .models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables (use with caution!)"""
    from .models import Base
    Base.metadata.drop_all(bind=engine)
