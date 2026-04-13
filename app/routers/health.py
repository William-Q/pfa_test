"""Health check API routes."""

from fastapi import APIRouter

from app.services.health_service import get_health_status

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return get_health_status()
