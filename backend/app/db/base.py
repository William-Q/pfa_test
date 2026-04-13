"""Declarative base import surface for SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# Ensure model metadata is registered on import.
from app.models.transaction import Transaction  # noqa: E402,F401
