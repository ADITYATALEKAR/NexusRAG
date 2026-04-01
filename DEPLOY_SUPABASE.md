# Deploy NexusRAG Services on Supabase

## What Supabase is used for in this stack

For the Vercel + Supabase deployment, Supabase is used for:

- `Auth`: end-user sign up / sign in
- `Postgres`: lightweight metadata tables (`profiles`, `document_uploads`)
- `Storage`: private `documents` bucket for staged uploads

Supabase is **not** hosting the Python RAG backend.

## Required environment values

You will copy these into Vercel after creating the Supabase project:

### Browser-safe

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET=documents
```

### Server-only

```env
SUPABASE_SERVICE_ROLE_KEY=
```

For the current minimum viable setup, you can leave `SUPABASE_SERVICE_ROLE_KEY` empty.

## Exact manual setup steps

1. Create a new Supabase project.
2. Open `Project Settings` and copy:
   - Project URL
   - anon / publishable key
   - service role key
3. Open `Authentication` and enable `Email` sign-in.
4. Decide whether email confirmation should be on:
   - `off` for the fastest solo-founder setup
   - `on` if you want email verification from day one
5. Run the repository migration:
   - file: `supabase/migrations/20260401100000_vercel_supabase_foundation.sql`
6. Confirm the following now exist:
   - table `public.profiles`
   - table `public.document_uploads`
   - private bucket `documents`
   - row-level security policies on both tables and the bucket

## How to run the migration

### Option A: Supabase SQL Editor

1. Open `SQL Editor`
2. Create a new query
3. Paste the contents of:
   - `supabase/migrations/20260401100000_vercel_supabase_foundation.sql`
4. Run it once

### Option B: Supabase CLI

If you use the CLI locally:

```bash
supabase link --project-ref your-project-ref
supabase db push
```

## Storage bucket notes

The migration creates a private bucket named `documents`.

Expected behavior:

- users upload to their own folder path in the bucket
- users can only see and delete their own files
- the Vercel app stages files there even when no Python backend is attached yet

## Auth notes

The repo now supports Supabase-backed public-user auth for the frontend.

Recommended first setup:

- email/password auth enabled
- email confirmation optional
- no OAuth providers until you actually need them

## Secrets that must never go in the frontend

These must stay server-only and never be exposed in `NEXT_PUBLIC_*` vars:

- `SUPABASE_SERVICE_ROLE_KEY`
- `BACKEND_SERVICE_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`

## Edge Functions

Edge Functions are not required for the current minimum viable setup.

Reason:

- the frontend already uses Vercel route handlers for lightweight orchestration
- the heavy Python RAG logic still belongs in a separate compute service later

Only add Supabase Edge Functions later if you have a very small, stateless server-side task that does not justify a separate backend.
