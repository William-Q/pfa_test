"""Pydantic schemas for transaction APIs."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionSourceType


class TransactionBase(BaseModel):
    """Shared canonical transaction fields."""

    import_batch_id: str = Field(min_length=1, max_length=64)
    source_type: TransactionSourceType
    account_name: str = Field(min_length=1, max_length=120)

    amount: Decimal = Field(description="Signed amount in account currency.")
    currency: str = Field(default="USD", min_length=3, max_length=3)

    transaction_date: date | None = None
    posted_date: date | None = None

    raw_description: str = Field(min_length=1, max_length=512)
    normalized_merchant: str | None = Field(default=None, max_length=255)


class TransactionCreate(TransactionBase):
    """Request schema for creating/importing a transaction."""


class TransactionResponse(TransactionBase):
    """Response schema for canonical transaction payloads."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
