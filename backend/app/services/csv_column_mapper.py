"""Utilities for mapping vendor CSV columns to canonical transaction fields."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeAlias

import pandas as pd

MappingConfig: TypeAlias = Mapping[str, str]


class ColumnMappingError(ValueError):
    """Base error for invalid or unusable column mapping configuration."""


class MissingRequiredColumnsError(ColumnMappingError):
    """Raised when one or more required source columns are absent."""


class InvalidMappingConfigError(ColumnMappingError):
    """Raised when the mapping config shape or content is invalid."""


REQUIRED_CANONICAL_FIELDS: frozenset[str] = frozenset({"date", "amount", "description"})


def normalize_columns(dataframe: pd.DataFrame, mapping_config: MappingConfig) -> pd.DataFrame:
    """Return a normalized dataframe with canonical column names.

    Args:
        dataframe: Raw transaction dataframe with source/vendor column names.
        mapping_config: Mapping of canonical field names to source column names.

    Returns:
        A new dataframe with canonical names as columns.

    Raises:
        InvalidMappingConfigError: If mapping keys are missing or malformed.
        MissingRequiredColumnsError: If mapped source columns are not present.
    """
    _validate_mapping_config(mapping_config)

    source_columns_by_canonical = dict(mapping_config)
    missing_source_columns = sorted(
        source_columns_by_canonical[canonical]
        for canonical in source_columns_by_canonical
        if source_columns_by_canonical[canonical] not in dataframe.columns
    )

    if missing_source_columns:
        available_columns = ", ".join(map(str, dataframe.columns.tolist()))
        missing_columns_text = ", ".join(missing_source_columns)
        raise MissingRequiredColumnsError(
            "Missing required source columns in dataframe: "
            f"{missing_columns_text}. Available columns: {available_columns}"
        )

    normalized = dataframe.loc[:, source_columns_by_canonical.values()].copy()
    normalized.columns = list(source_columns_by_canonical.keys())
    return normalized


def _validate_mapping_config(mapping_config: MappingConfig) -> None:
    """Validate mapping config keys and values before applying mappings."""
    if not mapping_config:
        raise InvalidMappingConfigError("Mapping config cannot be empty.")

    missing_required_fields = sorted(REQUIRED_CANONICAL_FIELDS - set(mapping_config))
    if missing_required_fields:
        raise InvalidMappingConfigError(
            "Mapping config is missing required canonical fields: "
            f"{', '.join(missing_required_fields)}"
        )

    invalid_entries = [
        canonical
        for canonical, source in mapping_config.items()
        if not canonical or not isinstance(canonical, str) or not source or not isinstance(source, str)
    ]
    if invalid_entries:
        raise InvalidMappingConfigError(
            "Mapping config contains invalid entries for canonical fields: "
            f"{', '.join(sorted(invalid_entries))}. "
            "Both canonical and source column names must be non-empty strings."
        )
