# NexusRAG Deployment Decision

## Target stack
- **Cloudflare Pages** runs the exported static frontend from `frontend/`.
- **Koyeb** runs the FastAPI backend from the repo root Dockerfile.
- **Neon Postgres + pgvector** stores application metadata, lexical search state, and dense vectors.

## What runs where
- **Cloudflare Pages**
  - landing page
  - dashboard UI
  - direct browser calls to the backend using `NEXT_PUBLIC_API_BASE_URL`
  - optional operator-mode override where a founder can point the app at a different protected backend
- **Koyeb**
  - ingestion
  - chunking
  - indexing
  - retrieval
  - reranking
  - answer generation
  - observability endpoints and health checks
- **Neon**
  - `documents` table for document metadata and index state
  - `chunks` table for chunk content plus lexical search state
  - `chunk_vectors` table for pgvector embeddings

## Minimum viable free-tier architecture
- Public demo frontend on Cloudflare Pages
- Single Koyeb web service for the FastAPI backend
- One Neon database using pgvector
- No external Redis, Qdrant, or Supabase dependency
- Ephemeral uploads on Koyeb, durable metadata/vectors in Neon

## What is intentionally deferred
- Vercel/Supabase/NextAuth deployment paths
- local SQLite and Qdrant as production storage backends
- durable raw file storage beyond the temporary Koyeb upload path
- worker split or background job queue
- always-on graph persistence files and local compression state files

## Known limitations of this setup
- Koyeb free tier can cold-start and may sleep between requests
- Cloudflare Pages static export means no Next.js middleware or route handlers in the deployed frontend
- Neon free tier storage and compute are enough for a demo, not a large multi-tenant workload
- Public demo mode should keep rate limiting on and avoid exposing server-only credentials
