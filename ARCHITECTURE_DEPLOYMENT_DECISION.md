# Architecture Deployment Decision

## Repository inspection result

### Frontend detected

- `frontend/`
- framework: `Next.js 14` with the App Router
- build system: standard `next build`

### Backend detected

- `apps/api/` and `src/`
- framework: `FastAPI` + substantial Python domain logic
- responsibilities: ingestion, indexing, retrieval, reranking, answer generation, failover, observability, evaluation

### Repo shape

This is a mixed repository.

- frontend: deployable on Vercel
- Python backend: not suitable for a Vercel + Supabase-only deployment

## Explicit recommendation

### What should run on Vercel

- the `frontend/` Next.js app
- Vercel-hosted Next.js route handlers
- Supabase session-aware pages
- lightweight UI orchestration
- lightweight document staging flows

### What should run on Supabase

- Auth
- Postgres tables for user and upload metadata
- Storage bucket for staged documents

### What should NOT run in this stack yet

Do not try to force these into Vercel + Supabase only:

- the Python RAG backend in `apps/api`
- document parsing and indexing pipelines
- embeddings and reranking
- vector search / Qdrant work
- heavy retrieval orchestration
- answer generation with LLM failover
- evaluation runs and backend observability pipeline

## Why this decision is the cleanest one

Supabase is excellent for:

- auth
- relational metadata
- object storage
- lightweight row-level access control

Vercel is excellent for:

- the Next.js frontend
- server-rendered pages
- lightweight route handlers

The existing Python backend is a real compute service. It depends on:

- Python runtime
- FastAPI
- vector store integrations
- indexing and retrieval workers
- provider orchestration
- file and local runtime storage patterns

That does not belong inside a Vercel + Supabase-only stack.

## Minimum viable free-tier setup

The smallest honest setup is:

- Vercel deploys `frontend/`
- Supabase provides Auth + Postgres + Storage
- users can sign up, sign in, and stage documents
- document metadata is visible in the UI
- query / answer / evaluation stay disabled until a separate backend exists

## Limitations of Vercel + Supabase only

Without the external Python backend, the deployed app will not provide:

- semantic retrieval
- hybrid retrieval
- reranking
- generation
- citations from processed chunks
- provider health
- evaluation runs

It is best understood as a deployable product shell plus user/auth/data foundation.

## Migration path later

When you are ready to restore full RAG behavior:

1. deploy the Python backend separately
2. set `BACKEND_API_URL` in Vercel
3. set `BACKEND_SERVICE_API_KEY` in Vercel
4. switch `NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND=true`

At that point, the frontend can stay on Vercel, Supabase can stay on auth/storage/metadata, and the heavy backend can live on a compute platform better suited to Python RAG workloads.
