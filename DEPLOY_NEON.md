# Deploy NexusRAG Storage on Neon

## What Neon is used for
- document metadata
- index state
- lexical search using Postgres full-text search
- dense vectors using `pgvector`

## Create the Neon project
1. Create a new Neon project.
2. Copy the connection string for the main database.
3. Keep SSL enabled in the connection string.

## Enable pgvector
Run the migration in Neon SQL Editor or via your migration workflow:

- [20260402000000_neon_pgvector_foundation.sql](/d:/VectorCore_FundamentalLabs/project-root/neon/migrations/20260402000000_neon_pgvector_foundation.sql)

That migration:
- creates `vector` extension
- creates `documents`
- creates `chunks`
- creates `chunk_vectors`
- adds pgvector and FTS indexes
- creates `documents_view` for structured retrieval compatibility

## Required environment variables
Backend only:

```env
DATABASE_URL=postgresql://user:password@your-neon-host/dbname?sslmode=require
```

Optional alias:

```env
NEON_DATABASE_URL=postgresql://user:password@your-neon-host/dbname?sslmode=require
```

## Connection string guidance
- Use the server-side Neon connection string in **Koyeb only**.
- Do **not** expose Neon credentials to Cloudflare Pages.
- Keep `sslmode=require` in the connection string.

## Exact setup steps for this repo
1. Create the Neon project.
2. Open SQL Editor.
3. Paste and run the migration from `neon/migrations/20260402000000_neon_pgvector_foundation.sql`.
4. Copy the connection string.
5. Set that string as `DATABASE_URL` in Koyeb.
6. Redeploy the Koyeb backend.

## What must never go to the frontend
- `DATABASE_URL`
- `NEON_DATABASE_URL`
- provider API keys
- any backend API key used for operator mode
