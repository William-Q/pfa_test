"""Aggregates V1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, imports

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(imports.router)
