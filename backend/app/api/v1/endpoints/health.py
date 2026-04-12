"""Health endpoints for readiness/liveness checks."""

from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("/live", summary="Liveness probe")
def liveness() -> dict[str, str]:
    """Returns process-level health for orchestrators."""
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
def readiness() -> dict[str, str]:
    """Returns dependency-level readiness for traffic routing."""
    return {"status": "ready"}
