# Deploy NexusRAG Frontend on Vercel

## Framework detected

- Framework: Next.js 14 App Router
- Frontend root directory: `frontend`
- Repository type: mixed monorepo (`frontend` + Python backend)

## What Vercel will host

Vercel should host only the `frontend/` app.

This includes:

- the Next.js UI
- Next.js route handlers under `frontend/app/api`
- Supabase auth-aware pages and proxy routes
- light document staging to Supabase Storage

It does **not** host the Python RAG backend from `apps/api`.

## Vercel dashboard values

Use these exact values in the Vercel dashboard when importing the repo:

- Git provider: `GitHub`
- Repository: `ADITYATALEKAR/NexusRAG`
- Framework Preset: `Next.js`
- Root Directory: `frontend`
- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: leave blank so Vercel auto-detects Next.js output
- Node.js Version: `20.x`
- Auto-deploy from GitHub: `Enabled`

## Environment variables to set in Vercel

### Safe to expose to the browser

These start with `NEXT_PUBLIC_` and are safe for client exposure:

```env
NEXT_PUBLIC_NEXUSRAG_APP_NAME=NexusRAG
NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP=true
NEXT_PUBLIC_NEXUSRAG_DEPLOYMENT_TARGET=vercel-supabase
NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND=false
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET=documents
```

### Server-only in Vercel

These must never be exposed to the browser:

```env
BACKEND_API_URL=
BACKEND_SERVICE_API_KEY=
SUPABASE_SERVICE_ROLE_KEY=
NEXTAUTH_URL=https://your-vercel-domain.vercel.app
NEXTAUTH_SECRET=replace_with_a_long_random_secret_if_using_nextauth
```

Notes:

- `SUPABASE_SERVICE_ROLE_KEY` is optional for the current MVP and should stay unset unless you add admin-only server workflows later.
- `BACKEND_API_URL` and `BACKEND_SERVICE_API_KEY` stay blank in the pure Vercel + Supabase setup.

## Minimum viable free-tier setup

For the smallest working Vercel + Supabase deployment, set:

```env
NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND=false
```

That mode supports:

- landing page
- Supabase-backed sign up / sign in
- document uploads staged in Supabase Storage
- document list / delete

That mode does **not** support:

- answer generation
- retrieval
- evaluation
- provider health
- the Python RAG pipeline

## When you deploy the Python backend later

Once the external FastAPI backend exists elsewhere, update Vercel with:

```env
BACKEND_API_URL=https://your-python-backend.example.com
BACKEND_SERVICE_API_KEY=your_backend_service_api_key
NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND=true
```

After that, the dashboard query and backend-powered routes will light up.

## Notes

- Keep `SUPABASE_SERVICE_ROLE_KEY`, `BACKEND_SERVICE_API_KEY`, and model provider keys server-only.
- Do not put `SUPABASE_SERVICE_ROLE_KEY` in `NEXT_PUBLIC_*` vars.
- If you are only using Supabase Auth, `NEXTAUTH_SECRET` is optional because the credentials-based operator mode is not active.
