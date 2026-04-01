"""API key authentication helpers."""

from __future__ import annotations

import hashlib
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """Validate API keys using hashed values."""

    def __init__(self, valid_keys: list[str]) -> None:
        self.valid_hashes = {self._hash(key) for key in valid_keys if key}

    def _hash(self, key: str) -> str:
        """Return a stable SHA-256 digest for a key."""
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def validate(self, key: str) -> bool:
        """Return whether the provided key is registered."""
        if not key:
            return False
        return self._hash(key) in self.valid_hashes

    def fingerprint(self, key: str) -> str:
        """Return a short stable fingerprint for logging and tracing."""
        return self._hash(key)[:12]

    @staticmethod
    def generate_key() -> str:
        """Generate a new API key."""
        return f"rag_{secrets.token_urlsafe(32)}"


async def require_api_key(
    api_key: str | None = Security(api_key_header),
    auth: APIKeyAuth | None = None,
) -> str:
    """FastAPI dependency for endpoint-level API key protection."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if auth is None or not auth.validate(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key
