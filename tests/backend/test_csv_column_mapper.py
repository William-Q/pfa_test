"""Tests for CSV column mapping normalization."""

import pandas as pd
import pytest

from app.services.csv_column_mapper import (
    InvalidMappingConfigError,
    MissingRequiredColumnsError,
    normalize_columns,
)


def test_normalize_columns_returns_canonical_dataframe() -> None:
    dataframe = pd.DataFrame(
        {
            "Transaction Date": ["2026-04-01"],
            "Amount": [19.95],
            "Description": ["Coffee"],
            "Ignored": ["metadata"],
        }
    )
    mapping_config = {
        "date": "Transaction Date",
        "amount": "Amount",
        "description": "Description",
    }

    normalized = normalize_columns(dataframe, mapping_config)

    assert list(normalized.columns) == ["date", "amount", "description"]
    assert normalized.to_dict(orient="records") == [
        {"date": "2026-04-01", "amount": 19.95, "description": "Coffee"}
    ]


def test_normalize_columns_raises_on_missing_dataframe_columns() -> None:
    dataframe = pd.DataFrame(
        {
            "Transaction Date": ["2026-04-01"],
            "Description": ["Coffee"],
        }
    )
    mapping_config = {
        "date": "Transaction Date",
        "amount": "Amount",
        "description": "Description",
    }

    with pytest.raises(MissingRequiredColumnsError, match="Amount"):
        normalize_columns(dataframe, mapping_config)


def test_normalize_columns_raises_on_missing_required_mapping_keys() -> None:
    dataframe = pd.DataFrame(
        {
            "Transaction Date": ["2026-04-01"],
            "Amount": [19.95],
        }
    )
    mapping_config = {
        "date": "Transaction Date",
        "amount": "Amount",
    }

    with pytest.raises(InvalidMappingConfigError, match="description"):
        normalize_columns(dataframe, mapping_config)
