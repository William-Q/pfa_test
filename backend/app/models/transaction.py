"""Transaction ORM model."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransactionSourceType(StrEnum):
    """Supported import source types for canonical transactions."""

    BANK_CSV = "bank_csv"
    CREDIT_CARD_CSV = "credit_card_csv"
    PAYPAL_CSV = "paypal_csv"


class Transaction(Base):
    """Canonical persistent transaction record for imported data."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    import_batch_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_type: Mapped[TransactionSourceType] = mapped_column(
        Enum(TransactionSourceType, native_enum=False), nullable=False, index=True
    )
    account_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    raw_description: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_merchant: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
