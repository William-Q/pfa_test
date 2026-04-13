"""Database initialization helpers."""

from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Create database tables for all registered ORM models."""
    # Import models so SQLAlchemy registers table metadata before create_all.
    from app.models.transaction import Transaction  # noqa: F401

    Base.metadata.create_all(bind=engine)
