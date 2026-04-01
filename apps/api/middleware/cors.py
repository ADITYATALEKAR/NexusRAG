"""CORS configuration helpers for the API application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def normalize_origins(origins: list[str] | str | None) -> list[str]:
    """Normalize configured CORS origins into a list of strings."""
    if origins is None:
        return ["*"]
    if isinstance(origins, str):
        return [origin.strip() for origin in origins.split(",") if origin.strip()] or ["*"]
    cleaned = [origin.strip() for origin in origins if origin.strip()]
    return cleaned or ["*"]


def configure_cors(
    app: FastAPI,
    origins: list[str] | str | None,
    allow_credentials: bool = False,
) -> None:
    """Attach FastAPI's CORS middleware with the supplied settings."""
    normalized = normalize_origins(origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=normalized,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Request-ID",
            "X-Trace-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
    )
