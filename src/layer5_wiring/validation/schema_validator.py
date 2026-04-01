"""Schema validation helper."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from src.layer0_core.errors.base import ConfigurationError

T = TypeVar("T", bound=BaseModel)


class SchemaValidator:
    """Validate data against Pydantic schemas with consistent errors."""

    @staticmethod
    def validate(data: dict[str, Any], schema: type[T]) -> T:
        """Validate a mapping against a schema."""
        try:
            return schema.model_validate(data)
        except PydanticValidationError as error:
            raise ConfigurationError(f"Schema validation failed for {schema.__name__}: {error}") from error
