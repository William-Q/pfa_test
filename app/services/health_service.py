"""Service logic for health checks."""


def get_health_status() -> dict[str, str]:
    """Return a static status payload for liveness probes."""
    return {"status": "ok"}
