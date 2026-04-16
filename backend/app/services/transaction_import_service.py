"""Service layer for importing CSV transactions."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import StringIO
import uuid

from pandas import DataFrame
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.csv_column_mapper import normalize_columns
from app.services.transaction_normalizer import normalize_transactions

if TYPE_CHECKING:
    from app.models.transaction import TransactionSourceType

MAX_ERROR_SAMPLES = 10
DEFAULT_NO_HEADER_COLUMNS: tuple[str, ...] = (
    "Transaction Date",
    "Amount",
    "Type",
    "Reference",
    "Description",
)
KNOWN_CSV_HEADERS: frozenset[str] = frozenset(
    {
        "details",
        "posting date",
        "description",
        "amount",
        "type",
        "balance",
        "check or slip #",
        "posted date",
        "reference number",
        "payee",
        "address",
        "card",
        "transaction date",
        "post date",
        "category",
        "memo",
    }
)


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
    decoded_contents = contents.decode("utf-8-sig")
    rows = [row for row in csv.reader(StringIO(decoded_contents)) if row]
    if not rows:
        return pd.DataFrame()

    first_row = [cell.strip() for cell in rows[0]]
    has_header = _looks_like_header(first_row)

    if has_header:
        columns = [column.lstrip("\ufeff").strip() for column in first_row]
        data_rows = rows[1:]
    else:
        data_rows = rows
        sample_width = len(first_row)
        if sample_width == len(DEFAULT_NO_HEADER_COLUMNS):
            columns = list(DEFAULT_NO_HEADER_COLUMNS)
        else:
            columns = [f"column_{index}" for index in range(1, sample_width + 1)]

    expected_width = len(columns)
    normalized_rows = [
        _normalize_row_width([str(value).strip() for value in row], expected_width)
        for row in data_rows
    ]

    dataframe = pd.DataFrame(normalized_rows, columns=columns)
    return _drop_leading_unnamed_column(dataframe)


def _looks_like_header(row: list[str]) -> bool:
    normalized_cells = {
        value.strip().lower()
        for value in row
        if value and value.strip()
    }
    return any(cell in KNOWN_CSV_HEADERS for cell in normalized_cells)


def _normalize_row_width(row: list[str], width: int) -> list[str]:
    if len(row) < width:
        return row + [""] * (width - len(row))
    if len(row) > width:
        return row[:width]
    return row


def _drop_leading_unnamed_column(dataframe: DataFrame) -> DataFrame:
    if dataframe.empty:
        return dataframe
    first_column_name = str(dataframe.columns[0]).strip().lower()
    if first_column_name in {"", "unnamed: 0"}:
        return dataframe.drop(columns=[dataframe.columns[0]])
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
