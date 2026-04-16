"""Regression tests for transaction import service module loading."""

from importlib import import_module


def test_transaction_import_service_module_imports() -> None:
    module = import_module("app.services.transaction_import_service")

    assert hasattr(module, "parse_csv_upload")
    assert hasattr(module, "import_transactions")
