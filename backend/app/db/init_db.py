"""Database initialization helpers."""

from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Create database tables for all registered ORM models."""
    Base.metadata.create_all(bind=engine)
