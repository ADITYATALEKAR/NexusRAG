# Northflank Deployment

This directory documents the recommended Northflank layout for NexusRAG.

## Recommended service topology

Create two public services:

1. `nexusrag-api`
2. `nexusrag-web`

Optional:

3. managed Redis addon or external Redis
4. managed Qdrant or external Qdrant endpoint

## API service

Use the repository root Dockerfile:

- build type: Dockerfile
- Dockerfile path: `/Dockerfile`
- build context: `/`
- target stage: `production`
- public port: `8000`
- health check: `/health/liveness`

### API environment variables

Use values from `api.env.example` as a starting point.

Important:

- if you do **not** provide `QDRANT_URL`, the API will store vectors locally under `/app/data/qdrant`
- metadata, lexical search, uploads, graph state, and compression state are still stored under `/app/data`
- mount a persistent volume to `/app/data`

## Web service

Use the frontend Dockerfile:

- build type: Dockerfile
- Dockerfile path: `/frontend/Dockerfile`
- build context: `/frontend`
- public port: `3000`

### Web environment variables

Use values from `web.env.example` as a starting point.

Important:

- set `BACKEND_API_URL` to the internal or public API URL that the Next.js server can reach
- set `BACKEND_SERVICE_API_KEY` to the same backend API key configured on the API service
- keep `NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP=true` so users are not asked to enter API keys in the browser
- because Next.js inlines `NEXT_PUBLIC_*` values into the client bundle, configure these as build-time variables too:
  - `NEXT_PUBLIC_API_URL`
  - `NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP`
  - `NEXT_PUBLIC_NEXUSRAG_APP_NAME`

## Persistent storage

Minimum recommendation:

- one persistent volume mounted at `/app/data` on the API service
- start with `10 GB`

## Suggested rollout order

1. deploy `nexusrag-api`
2. verify `/health/liveness`, `/health/readiness`, and `/providers/health`
3. deploy `nexusrag-web`
4. open the landing page and navigate to `/dashboard`
5. upload a document and run a query
6. add custom domains after both services are healthy
