"""Tests for CSV parsing behavior in transaction import service."""

from app.services.transaction_import_service import parse_csv_upload


def test_parse_csv_upload_drops_leading_unnamed_index_column() -> None:
    contents = (
        b",Transaction Date,Amount,Description\n"
        b"0,2026-04-01,11.50,Coffee\n"
    )

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == ["Transaction Date", "Amount", "Description"]
    assert dataframe.iloc[0].to_dict() == {
        "Transaction Date": "2026-04-01",
        "Amount": 11.50,
        "Description": "Coffee",
    }


def test_parse_csv_upload_removes_bom_from_first_header() -> None:
    contents = (
        "\ufeffTransaction Date,Amount,Description\n"
        "2026-04-01,11.50,Coffee\n"
    ).encode("utf-8")

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == ["Transaction Date", "Amount", "Description"]
