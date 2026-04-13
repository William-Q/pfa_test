"""Example insert/query helpers for transaction data."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction


def insert_example_transaction(db: Session) -> Transaction:
    """Insert a sample transaction and persist it."""
    transaction = Transaction(
        date=date(2026, 1, 15),
        amount=Decimal("42.50"),
        description="Grocery store",
        category="Food",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def query_transactions_by_category(db: Session, category: str) -> list[Transaction]:
    """Fetch all transactions in a category, ordered by most recent date."""
    stmt = select(Transaction).where(Transaction.category == category).order_by(Transaction.date.desc())
    return list(db.scalars(stmt).all())
