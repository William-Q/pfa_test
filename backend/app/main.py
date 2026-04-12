"""FastAPI entrypoint with application-wide wiring."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="Personal finance backend API.",
)

app.include_router(api_router, prefix="/api/v1")
