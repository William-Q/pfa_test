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


def test_parse_csv_upload_supports_chase_export_with_ragged_rows() -> None:
    contents = (
        b"Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #\n"
        b"DEBIT,04/06/2026,\"Zelle payment to Jay JPM99cbyuvao\",-62.00,CHASE_TO_PARTNERFI,7038.91,,\n"
    )

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == [
        "Details",
        "Posting Date",
        "Description",
        "Amount",
        "Type",
        "Balance",
        "Check or Slip #",
    ]
    assert dataframe.iloc[0].to_dict() == {
        "Details": "DEBIT",
        "Posting Date": "04/06/2026",
        "Description": "Zelle payment to Jay JPM99cbyuvao",
        "Amount": -62.00,
        "Type": "CHASE_TO_PARTNERFI",
        "Balance": 7038.91,
        "Check or Slip #": "",
    }


def test_parse_csv_upload_supports_discover_no_header_export() -> None:
    contents = (
        b"\"10/10/2023\",\"-161.20\",\"*\",\"\",\"DISCOVER E-PAYMENT 231008 7122 QIU JICONG\"\n"
    )

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == [
        "Transaction Date",
        "Amount",
        "Type",
        "Reference",
        "Description",
    ]
    assert dataframe.iloc[0].to_dict() == {
        "Transaction Date": "10/10/2023",
        "Amount": -161.20,
        "Type": "*",
        "Reference": "",
        "Description": "DISCOVER E-PAYMENT 231008 7122 QIU JICONG",
    }


def test_parse_csv_upload_supports_discover_no_header_multiple_rows() -> None:
    contents = (
        b"\"10/23/2023\",\"-24.99\",\"*\",\"\",\"VERIZON PAYMENTREC URRING 9572565140001 FIRST NAME LAST NAME\"\n"
        b"\"10/20/2023\",\"250.00\",\"*\",\"\",\"NAVY FEDERAL CRE DIR DEP 231020 XXXXX5649 Qiu Jicong\"\n"
    )

    dataframe = parse_csv_upload(contents)

    assert dataframe.to_dict(orient="records") == [
        {
            "Transaction Date": "10/23/2023",
            "Amount": -24.99,
            "Type": "*",
            "Reference": "",
            "Description": "VERIZON PAYMENTREC URRING 9572565140001 FIRST NAME LAST NAME",
        },
        {
            "Transaction Date": "10/20/2023",
            "Amount": 250.00,
            "Type": "*",
            "Reference": "",
            "Description": "NAVY FEDERAL CRE DIR DEP 231020 XXXXX5649 Qiu Jicong",
        },
    ]


def test_parse_csv_upload_supports_capital_one_style_headers() -> None:
    contents = (
        b"Posted Date,Reference Number,Payee,Address,Amount\n"
        b"10/10/2023,24943003283400175000607,\"KFC K071153 STERLING VA\",\"STERLING      VA \",-5.29\n"
    )

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == [
        "Posted Date",
        "Reference Number",
        "Payee",
        "Address",
        "Amount",
    ]
    assert dataframe.iloc[0]["Payee"] == "KFC K071153 STERLING VA"


def test_parse_csv_upload_supports_card_statement_headers() -> None:
    contents = (
        b"Card,Transaction Date,Post Date,Description,Category,Type,Amount,Memo\n"
        b"3732,10/22/2023,10/23/2023,EZPASSVA AUTO REPLENIS,Travel,Sale,-35.00,\n"
    )

    dataframe = parse_csv_upload(contents)

    assert list(dataframe.columns) == [
        "Card",
        "Transaction Date",
        "Post Date",
        "Description",
        "Category",
        "Type",
        "Amount",
        "Memo",
    ]
    assert dataframe.iloc[0]["Amount"] == -35.00
