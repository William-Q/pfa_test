"""CSV import endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.imports import CsvImportSummary
from app.services.transaction_import_service import import_transactions, parse_csv_upload

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post(
    "/transactions/csv",
    response_model=CsvImportSummary,
    summary="Import transactions from CSV",
)
async def import_transactions_csv(
    file: UploadFile = File(..., description="CSV file"),
    mapping_config: str = Form(..., description="JSON object mapping canonical fields to CSV columns"),
    account_name: str = Form("default_account"),
    source_type: str = Form("bank_csv"),
    currency: str = Form("USD"),
    import_batch_id: str | None = Form(None),
    db: Session = Depends(get_db),
) -> CsvImportSummary:
    """Accept multipart CSV + JSON mapping config, then persist normalized rows."""
    try:
        parsed_mapping = json.loads(mapping_config)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mapping_config JSON: {exc.msg}",
        ) from exc

    if not isinstance(parsed_mapping, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mapping_config must be a JSON object.",
        )

    csv_bytes = await file.read()
    try:
        dataframe = parse_csv_upload(csv_bytes)
    except Exception as exc:  # pandas parser errors are not stable across versions
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to parse CSV file: {exc}",
        ) from exc

    result = import_transactions(
        db=db,
        csv_dataframe=dataframe,
        mapping_config=parsed_mapping,
        account_name=account_name,
        source_type=source_type,
        currency=currency,
        import_batch_id=import_batch_id,
    )
    return CsvImportSummary(
        total_rows=result.total_rows,
        inserted_rows=result.inserted_rows,
        failed_rows=result.failed_rows,
        error_samples=result.error_samples,
    )
