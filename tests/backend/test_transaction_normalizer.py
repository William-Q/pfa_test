"""Tests for canonical transaction normalization."""

from decimal import Decimal

import pandas as pd
import pytest

from app.services.transaction_normalizer import (
    AmountNormalizationError,
    DateNormalizationError,
    MissingCanonicalColumnsError,
    normalize_transactions,
)


def test_normalize_transactions_returns_canonical_dataframe() -> None:
    dataframe = pd.DataFrame(
        {
            "date": [" 04/01/2026 "],
            "amount": [" $1,234.50 "],
            "description": ["  STARBUCKS   STORE  "],
            "category": ["  Dining  "],
        }
    )

    normalized = normalize_transactions(dataframe)

    assert list(normalized.columns) == ["date", "amount", "description"]
    assert normalized.to_dict(orient="records") == [
        {
            "date": "2026-04-01",
            "amount": Decimal("1234.50"),
            "description": "starbucks store",
        }
    ]


def test_normalize_transactions_parses_accounting_negative_amount() -> None:
    dataframe = pd.DataFrame(
        {"date": ["2026-04-01"], "amount": ["($45.10)"], "description": ["refund"]}
    )

    normalized = normalize_transactions(dataframe)

    assert normalized.loc[0, "amount"] == Decimal("-45.10")


def test_normalize_transactions_raises_on_bad_date() -> None:
    dataframe = pd.DataFrame(
        {"date": ["not-a-date"], "amount": ["10.00"], "description": ["Coffee"]}
    )

    with pytest.raises(DateNormalizationError, match="not-a-date"):
        normalize_transactions(dataframe)


def test_normalize_transactions_raises_on_multiple_bad_dates() -> None:
    dataframe = pd.DataFrame(
        {
            "date": ["2026-04-01", "13/40/2026", "bad-date"],
            "amount": ["10.00", "20.00", "30.00"],
            "description": ["one", "two", "three"],
        }
    )

    with pytest.raises(DateNormalizationError, match="13/40/2026"):
        normalize_transactions(dataframe)


def test_normalize_transactions_raises_on_bad_amount() -> None:
    dataframe = pd.DataFrame(
        {"date": ["2026-04-01"], "amount": ["12.3.4"], "description": ["Coffee"]}
    )

    with pytest.raises(AmountNormalizationError, match="12.3.4"):
        normalize_transactions(dataframe)


def test_normalize_transactions_normalizes_amount_formats() -> None:
    dataframe = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "amount": ["$1,200.00", "-10", "(45.67)"],
            "description": ["salary", "fee", "refund"],
        }
    )

    normalized = normalize_transactions(dataframe)

    assert normalized["amount"].tolist() == [
        Decimal("1200.00"),
        Decimal("-10"),
        Decimal("-45.67"),
    ]


def test_normalize_transactions_handles_empty_rows_without_errors() -> None:
    dataframe = pd.DataFrame(
        {
            "date": ["2026-04-01", None],
            "amount": ["10.00", None],
            "description": ["Coffee", None],
        }
    )

    normalized = normalize_transactions(dataframe)

    assert normalized.loc[0, "date"] == "2026-04-01"
    assert normalized.loc[0, "amount"] == Decimal("10.00")
    assert normalized.loc[0, "description"] == "coffee"

    assert pd.isna(normalized.loc[1, "date"])
    assert normalized.loc[1, "amount"] is None
    assert normalized.loc[1, "description"] is None


def test_normalize_transactions_raises_on_missing_columns() -> None:
    dataframe = pd.DataFrame({"date": ["2026-04-01"], "amount": ["10.00"]})

    with pytest.raises(MissingCanonicalColumnsError, match="description"):
        normalize_transactions(dataframe)
