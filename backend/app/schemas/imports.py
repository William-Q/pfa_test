"""Schemas for CSV import APIs."""

from pydantic import BaseModel, Field


class CsvImportRequest(BaseModel):
    """Configuration payload used for transaction CSV imports."""

    mapping_config: dict[str, str] = Field(
        description=(
            "Canonical-to-source column mapping for date, amount, description. "
            "For no-header 5-column CSVs, parsed column names default to "
            "Transaction Date, Amount, Type, Reference, Description."
        )
    )
    account_name: str = Field(default="default_account", min_length=1, max_length=120)
    source_type: str = Field(default="bank_csv", min_length=1, max_length=64)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    import_batch_id: str | None = Field(default=None, max_length=64)


class CsvImportSummary(BaseModel):
    """Response payload summarizing CSV import outcomes."""

    total_rows: int
    inserted_rows: int
    failed_rows: int
    error_samples: list[str]
