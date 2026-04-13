"""Service layer for importing CSV transactions."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import uuid

from pandas import DataFrame
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.csv_column_mapper import normalize_columns
from app.services.transaction_normalizer import normalize_transactions

MAX_ERROR_SAMPLES = 10


@dataclass(slots=True)
class ImportResult:
    """In-memory summary of an import attempt."""

    total_rows: int
    inserted_rows: int
    failed_rows: int
    error_samples: list[str]


def import_transactions(
    db: Session,
    csv_dataframe: DataFrame,
    mapping_config: dict[str, str],
    account_name: str,
    source_type: str,
    currency: str,
    import_batch_id: str | None = None,
) -> ImportResult:
    """Map/normalize rows and persist them as transaction records."""
    from app.models.transaction import Transaction

    total_rows = len(csv_dataframe.index)
    inserted_rows = 0
    error_samples: list[str] = []

    try:
        mapped_dataframe = normalize_columns(csv_dataframe, mapping_config)
        normalized_dataframe = normalize_transactions(mapped_dataframe)
    except ValueError as exc:
        return ImportResult(
            total_rows=total_rows,
            inserted_rows=0,
            failed_rows=total_rows,
            error_samples=[str(exc)],
        )

    resolved_batch_id = import_batch_id or str(uuid.uuid4())
    source_enum = _resolve_source_type(source_type)

    for row_index, row in normalized_dataframe.iterrows():
        try:
            with db.begin_nested():
                transaction = Transaction(
                    import_batch_id=resolved_batch_id,
                    source_type=source_enum,
                    account_name=account_name,
                    amount=_to_decimal(row["amount"]),
                    currency=currency.upper(),
                    transaction_date=_to_date(row["date"]),
                    posted_date=None,
                    raw_description=str(row["description"]),
                    normalized_merchant=str(row["description"]),
                )
                db.add(transaction)
                db.flush()
            inserted_rows += 1
        except (SQLAlchemyError, ValueError, TypeError) as exc:
            if len(error_samples) < MAX_ERROR_SAMPLES:
                error_samples.append(f"row={row_index}: {exc}")

    failed_rows = total_rows - inserted_rows
    return ImportResult(
        total_rows=total_rows,
        inserted_rows=inserted_rows,
        failed_rows=failed_rows,
        error_samples=error_samples,
    )


def parse_csv_upload(contents: bytes) -> DataFrame:
    """Parse raw CSV bytes into a DataFrame."""
    csv_buffer = pd.io.common.BytesIO(contents)
    sample = contents[:4096].decode("utf-8-sig", errors="ignore")
    delimiter = _detect_delimiter(sample)

    dataframe = pd.read_csv(
        csv_buffer,
        encoding="utf-8-sig",
        sep=delimiter,
        skipinitialspace=True,
    )
    dataframe.columns = [str(column).replace("\ufeff", "").strip() for column in dataframe.columns]
    return _drop_artifact_index_column(dataframe)


def _detect_delimiter(sample: str) -> str | None:
    """Best-effort delimiter detection for vendor CSV variants."""
    if not sample.strip():
        return None
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return None


def _drop_artifact_index_column(dataframe: DataFrame) -> DataFrame:
    """Drop an artifact index column commonly produced in exported CSVs."""
    if dataframe.empty:
        return dataframe

    first_column = dataframe.columns[0]
    if str(first_column).startswith("Unnamed:"):
        return dataframe.iloc[:, 1:]
    return dataframe


def _to_date(value: object) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(str(value))


def _to_decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _resolve_source_type(source_type: str) -> TransactionSourceType:
    from app.models.transaction import TransactionSourceType

    try:
        return TransactionSourceType(source_type)
    except ValueError:
        return TransactionSourceType.BANK_CSV
