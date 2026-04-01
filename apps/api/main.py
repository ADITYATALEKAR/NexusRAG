"""FastAPI application entry point."""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI

from apps.api.lifespan import build_lifespan, load_runtime_config
from apps.api.middleware.cors import configure_cors
from apps.api.middleware.rate_limit import RateLimitMiddleware
from apps.api.middleware.security import SecurityHeadersMiddleware
from src.layer6_security.auth.middleware import AuthMiddleware
from apps.api.middleware.logging import RequestLoggingMiddleware
from apps.api.middleware.metrics import MetricsMiddleware
from apps.api.middleware.tracing import TracingMiddleware
from apps.api.routes.answer import router as answer_router
from apps.api.routes.documents import router as documents_router
from apps.api.routes.eval import router as eval_router
from apps.api.routes.health import router as health_router
from apps.api.routes.ingest import router as ingest_router
from apps.api.routes.metrics import router as metrics_router
from apps.api.routes.providers import router as providers_router
from apps.api.routes.query import router as query_router
from apps.api.routes.retrieval import router as retrieval_router
from apps.api.routes.wiring import router as wiring_router
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import AppFileConfig

config_dir = Path(__file__).resolve().parents[2] / "configs"
runtime_config = load_runtime_config(config_dir)

app = FastAPI(title="RAG System", lifespan=build_lifespan(config_dir))


@app.middleware("http")
async def drain_inflight_requests(request, call_next):
    """Track active requests so shutdown can wait for in-flight work."""
    coordinator = getattr(request.app.state, "shutdown_coordinator", None)
    if coordinator is None:
        return await call_next(request)

    await coordinator.request_started()
    try:
        return await call_next(request)
    finally:
        await coordinator.request_finished()


app.add_middleware(AuthMiddleware, enabled=runtime_config.security.api_key_required)
app.add_middleware(RateLimitMiddleware, enabled=runtime_config.security.rate_limit_enabled)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(TracingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
configure_cors(
    app,
    origins=runtime_config.security.cors_origins,
    allow_credentials=runtime_config.security.cors_allow_credentials,
)
app.include_router(answer_router, prefix="/answer", tags=["answer"])
app.include_router(documents_router, tags=["documents"])
app.include_router(eval_router, tags=["evaluation"])
app.include_router(eval_router, prefix="/eval", tags=["evaluation"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(ingest_router, tags=["ingestion"])
app.include_router(metrics_router, tags=["telemetry"])
app.include_router(providers_router, prefix="/providers", tags=["providers"])
app.include_router(query_router, tags=["query"])
app.include_router(retrieval_router, prefix="/retrieval", tags=["retrieval"])
app.include_router(wiring_router, prefix="/wiring", tags=["wiring"])


if __name__ == "__main__":
    import uvicorn

    app_file_config = ConfigLoader(config_dir=config_dir).load_validated("app/app.yaml", AppFileConfig)
    uvicorn.run(
        "apps.api.main:app",
        host=runtime_config.server_host or app_file_config.server.host,
        port=runtime_config.server_port or app_file_config.server.port,
        workers=runtime_config.server_workers or app_file_config.server.workers,
        timeout_keep_alive=runtime_config.timeout_keep_alive,
        reload=False,
    )
