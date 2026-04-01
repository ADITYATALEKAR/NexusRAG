"""FastAPI dependency helpers."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from src.layer8_runtime.bootstrap.startup import StartupResult


def get_startup_result(request: Request) -> StartupResult:
    """Return the startup result stored on the app."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System bootstrap has not completed",
        )
    return startup_result
