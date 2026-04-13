"""Utilities to normalize canonical transaction fields."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

import pandas as pd

CANONICAL_TRANSACTION_COLUMNS: tuple[str, str, str] = ("date", "amount", "description")


class TransactionNormalizationError(ValueError):
    """Base error for transaction normalization failures."""


class DateNormalizationError(TransactionNormalizationError):
    """Raised when one or more dates cannot be normalized to ISO format."""


class AmountNormalizationError(TransactionNormalizationError):
    """Raised when one or more amounts cannot be normalized to Decimal values."""


class MissingCanonicalColumnsError(TransactionNormalizationError):
    """Raised when required canonical transaction columns are missing."""


def normalize_transactions(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a canonical transaction dataframe with normalized values.

    Normalization behavior:
    - Ensures required canonical columns are present.
    - Trims whitespace from all text-like columns.
    - Converts ``date`` values to ISO format (``YYYY-MM-DD``).
    - Converts ``amount`` values to ``Decimal`` for precision-safe storage.
    - Standardizes ``description`` text to lowercase with single-space separators.

    Args:
        dataframe: Dataframe that includes canonical transaction columns.

    Returns:
        A new dataframe with canonical columns ``date``, ``amount``, and
        ``description`` in that order.

    Raises:
        MissingCanonicalColumnsError: If required canonical columns are absent.
        DateNormalizationError: If date parsing fails for any row.
        AmountNormalizationError: If amount parsing fails for any row.
    """
    _validate_canonical_columns(dataframe)

    normalized = dataframe.copy()
    normalized = _trim_text_columns(normalized)

    normalized["date"] = _normalize_date_column(normalized["date"])
    normalized["amount"] = _normalize_amount_column(normalized["amount"])
    normalized["description"] = normalized["description"].map(_standardize_description)

    return normalized.loc[:, list(CANONICAL_TRANSACTION_COLUMNS)]


def _validate_canonical_columns(dataframe: pd.DataFrame) -> None:
    """Validate that canonical transaction columns are present."""
    missing_columns = [col for col in CANONICAL_TRANSACTION_COLUMNS if col not in dataframe.columns]
    if missing_columns:
        available = ", ".join(map(str, dataframe.columns.tolist()))
        raise MissingCanonicalColumnsError(
            "Missing required canonical columns: "
            f"{', '.join(missing_columns)}. Available columns: {available}"
        )


def _trim_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Trim leading and trailing whitespace in text-like columns."""
    result = dataframe.copy()
    text_columns = result.select_dtypes(include=["object", "string"]).columns
    for col in text_columns:
        result[col] = result[col].map(_strip_if_string)
    return result


def _strip_if_string(value: object) -> object:
    """Strip a value if it is a string; otherwise return it unchanged."""
    return value.strip() if isinstance(value, str) else value


def _normalize_date_column(series: pd.Series) -> pd.Series:
    """Normalize a date series to ISO date strings."""
    parsed = pd.to_datetime(series, errors="coerce")
    invalid_mask = parsed.isna() & series.notna()

    if invalid_mask.any():
        invalid_rows = [
            f"index={idx}, value={series.loc[idx]!r}"
            for idx in series.index[invalid_mask].tolist()
        ]
        raise DateNormalizationError(
            "Invalid date value(s): " + "; ".join(invalid_rows)
        )

    return parsed.dt.strftime("%Y-%m-%d")


def _normalize_amount_column(series: pd.Series) -> pd.Series:
    """Normalize amount values to ``Decimal`` instances."""
    normalized_values: list[Decimal | None] = []
    invalid_entries: list[str] = []

    for idx, raw_value in series.items():
        if pd.isna(raw_value):
            normalized_values.append(None)
            continue

        try:
            normalized_values.append(_parse_decimal_amount(raw_value))
        except (InvalidOperation, ValueError):
            invalid_entries.append(f"index={idx}, value={raw_value!r}")

    if invalid_entries:
        raise AmountNormalizationError(
            "Invalid amount value(s): " + "; ".join(invalid_entries)
        )

    return pd.Series(normalized_values, index=series.index, dtype="object")


def _parse_decimal_amount(value: object) -> Decimal:
    """Parse an amount-like value into a ``Decimal``.

    Supports optional currency symbols, thousands separators, and accounting
    negatives in parentheses.
    """
    text = str(value).strip()
    if not text:
        raise ValueError("Amount cannot be empty.")

    is_accounting_negative = text.startswith("(") and text.endswith(")")
    if is_accounting_negative:
        text = text[1:-1]

    cleaned = re.sub(r"[^0-9.\-]", "", text.replace(",", ""))
    if cleaned.count(".") > 1:
        raise ValueError("Amount has multiple decimal points.")

    decimal_value = Decimal(cleaned)
    return -decimal_value if is_accounting_negative else decimal_value


def _standardize_description(value: object) -> object:
    """Standardize description text by collapsing spaces and lowercasing."""
    if not isinstance(value, str):
        return value
    collapsed = " ".join(value.split())
    return collapsed.lower()
