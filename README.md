# VectorCore

VectorCore is a state-of-the-art retrieval operating system for enterprise RAG.

It combines a layered Python backend, a modern Next.js frontend, strict safety rails, provider failover, hybrid retrieval, evidence-first answer generation, evaluation tooling, observability, CLI and SDK surfaces, and deployment-ready infrastructure in one cohesive platform.

## Why VectorCore

Most RAG systems stop at "retrieve a few chunks and call an LLM." VectorCore is built as a full operating system for retrieval-heavy applications:

- typed contracts across every major subsystem
- fail-fast configuration and wiring validation
- hybrid, routed, and graph-aware retrieval
- evidence assembly, grounding, abstention, and citation handling
- multi-provider LLM failover and health-aware execution
- evaluation, tracing, metrics, and cost visibility
- production hardening for API, frontend, CLI, SDK, and deployment workflows

## What Is In The Repo

- `src/`: layered backend runtime and domain architecture
- `apps/api/`: FastAPI application and HTTP routes
- `frontend/`: Next.js dashboard, auth, analytics, and admin UX
- `cli/`: Typer-based CLI for querying, ingestion, and evaluation
- `sdk/`: sync and async Python client surfaces
- `configs/`: YAML-first system configuration
- `docs/`: architecture and decision records
- `eval/`: golden datasets, evaluation scripts, and report generation
- `deploy/`: Docker, Render, AWS, Azure, Cloudflare, and local deployment scaffolds

## Architecture

VectorCore enforces a strict layered model:

1. `Layer 8: Runtime` - bootstrap, lifecycle, feature flags, startup
2. `Layer 7: Interfaces` - API, CLI, SDK, telemetry interfaces
3. `Layer 6: Security` - auth, guards, rate limiting, masking, audit
4. `Layer 5: Wiring` - registries, validation, monitoring, observability
5. `Layer 4: Providers` - LLMs, embeddings, rerankers, parsers, stores, caches
6. `Layer 3: Flows` - orchestration for ingestion, indexing, retrieval, answer, routing
7. `Layer 2: Domain` - system intelligence and retrieval logic
8. `Layer 1: Contracts` - schemas, interfaces, policies, events
9. `Layer 0: Core` - IDs, enums, errors, values, time, constants

Dependency rule: a layer may only import from lower layers.

## Capabilities

### Backend

- typed Pydantic contracts for documents, chunks, queries, retrieval, evidence, answers, health, security, evaluation, and observability
- YAML configuration with environment overrides and startup validation
- provider registry with health tracking and LLM failover state machine
- ingestion, parsing, normalization, chunking, indexing, freshness, and lifecycle tracking
- dense, lexical, hybrid, reranked, routed, structured, and multi-hop retrieval
- contextual indexing, graph retrieval, and benchmark-gated compression
- evidence selection, citation validation, prompt building, abstention, and grounded answer generation
- evaluation, regression checks, metrics, tracing, and cost tracking

### Frontend

- Next.js App Router workspace
- session-backed auth with NextAuth
- dashboard, query workspace, document management, analytics, settings, and admin views
- backend proxy routes and production build pipeline

### Delivery Surfaces

- FastAPI app
- Typer CLI via `rag-cli`
- Python SDK with sync and async clients
- Docker and platform deployment scaffolds

## Implementation Status

Phases `0` through `9` are implemented in this repository:

- `Phase 0` - architectural spine and safety rails
- `Phase 1` - ingestion, parsing, normalization
- `Phase 2` - chunking and indexing
- `Phase 3` - retrieval and reranking
- `Phase 4` - evidence and grounded answer generation
- `Phase 5` - query understanding, routing, structured and multi-hop retrieval
- `Phase 6` - advanced retrieval with feature flags, contextual indexing, graph retrieval, compression
- `Phase 7` - evaluation and observability
- `Phase 8` - production hardening, CLI, SDK, deployment assets
- `Phase 9` - frontend product surface

## Quickstart

### 1. Backend setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

### 2. Frontend setup

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment

Create a local `.env` from the safe example file and set real values outside Git:

```bash
copy .env.example .env
```

Important variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`
- `NEXTAUTH_SECRET`
- `RAG__SECURITY__API_KEYS`

### 4. Run the API

```bash
python -m apps.api.main
```

Alternative:

```bash
uvicorn apps.api.main:app --reload
```

### 5. Run the frontend

```bash
cd frontend
npm run dev
```

### 6. Use the CLI

```bash
rag-cli --help
```

## Core Routes

- `/health`
- `/providers/health`
- `/wiring/graph`
- `/retrieval/retrieve`
- `/answer`
- `/query`
- `/ingest`
- `/metrics`
- `/eval`

## Quality And Validation

The project includes:

- unit, integration, contract, and benchmark tests
- frontend typecheck, lint, and production build validation
- compile checks for backend modules
- wiring validation and bootstrap readiness checks
- safety tests for masking, injection, and rate limiting

Most recent local validation pass completed with:

- `153 passed`
- `4 skipped` for env-gated live-provider tests that require real credentials

## Security Posture

VectorCore is designed to avoid accidental unsafe behavior:

- secret masking in provider and application error paths
- explicit `.gitignore` coverage for local env files, databases, uploads, build outputs, caches, and cloud-local state
- input sanitization, query safety checks, injection detection, and output guards
- auth, API key controls, rate limiting, and request-scoped observability

Never commit real secrets. Keep them in a local `.env` or in your deployment platform's secret manager.

## Deployment

Deployment assets are included for:

- Docker
- Render
- AWS
- Azure
- Cloudflare
- local development

Useful entry points:

- [Dockerfile](./Dockerfile)
- [docker-compose.yml](./docker-compose.yml)
- [render.yaml](./deploy/render.yaml)

## Documentation

Start here:

- [system-overview.md](./docs/architecture/system-overview.md)
- [layer-model.md](./docs/architecture/layer-model.md)
- [retrieval-lifecycle.md](./docs/architecture/retrieval-lifecycle.md)
- [generation-lifecycle.md](./docs/architecture/generation-lifecycle.md)
- [security-model.md](./docs/architecture/security-model.md)

## Vision

VectorCore is not just a demo RAG stack. It is intended to be a robust retrieval platform that can evolve into a high-trust, enterprise-ready system for search, reasoning, grounding, evaluation, and deployment across multiple environments.
