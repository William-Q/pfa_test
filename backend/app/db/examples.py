"""Example insert/query helpers for transaction data."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.models.transaction import TransactionSourceType


def insert_example_transaction(db: Session) -> Transaction:
    """Insert a sample transaction and persist it."""
    transaction = Transaction(
        import_batch_id="demo_batch_20260115",
        source_type=TransactionSourceType.BANK_CSV,
        account_name="Checking",
        amount=Decimal("42.50"),
        currency="USD",
        transaction_date=date(2026, 1, 15),
        posted_date=date(2026, 1, 16),
        raw_description="SQ *Corner Market 0123",
        normalized_merchant="Corner Market",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def query_transactions_by_merchant(db: Session, merchant: str) -> list[Transaction]:
    """Fetch all transactions for a normalized merchant, most recent first."""
    stmt = (
        select(Transaction)
        .where(Transaction.normalized_merchant == merchant)
        .order_by(Transaction.posted_date.desc(), Transaction.transaction_date.desc())
    )
    return list(db.scalars(stmt).all())
