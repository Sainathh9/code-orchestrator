import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.db.models  # Ensures all tables are registered on startup

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/orchestrator_db",
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()