"""Wiring introspection routes."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder

from src.layer5_wiring.registry.component_registry import ComponentInfo

router = APIRouter()


@router.get("/graph")
async def wiring_graph(request: Request) -> dict:
    """Return the component and dependency graph."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None:
        return {"components": [], "dependencies": []}
    components = [
        jsonable_encoder(_serialize_component(component))
        for component in startup_result.component_registry.all_components()
    ]
    dependencies = [jsonable_encoder(dependency) for dependency in startup_result.dependency_registry.all()]
    return {"components": components, "dependencies": dependencies}


@router.get("/health")
async def wiring_health(request: Request) -> dict:
    """Return the current startup validation status."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None:
        return {"valid": False, "issues": []}
    validation = startup_result.startup_validation
    issues = []
    for issue in validation.issues:
        issues.append(jsonable_encoder(asdict(issue) if is_dataclass(issue) else issue))
    return {"valid": validation.valid, "issues": issues}


@router.get("/components")
async def list_components(request: Request) -> list[dict]:
    """List all registered components."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None:
        return []
    return [
        jsonable_encoder(_serialize_component(component))
        for component in startup_result.component_registry.all_components()
    ]


def _serialize_component(component: ComponentInfo) -> dict:
    """Serialize component metadata without recursive live instances."""
    return {
        "id": component.id,
        "component_type": component.component_type,
        "layer": component.layer,
        "status": component.status,
        "required": component.required,
        "registered_at": component.registered_at,
        "instance_type": type(component.instance).__name__ if component.instance is not None else None,
    }
