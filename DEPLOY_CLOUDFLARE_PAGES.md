# Deploy NexusRAG on Cloudflare Pages

## Framework detected
- **Next.js 14**
- deployed as a **static export**

## Root directory
- `frontend`

## Build settings
- **Framework preset:** Next.js
- **Build command:** `npm run build`
- **Build output directory:** `out`
- **Root directory:** `frontend`
- **Auto-deploy from GitHub:** enable it

## Public environment variables
Set these in the Cloudflare Pages dashboard:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-koyeb-backend.koyeb.app
NEXT_PUBLIC_NEXUSRAG_APP_NAME=NexusRAG
NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP=true
NEXT_PUBLIC_NEXUSRAG_DEPLOYMENT_TARGET=cloudflare-pages-koyeb-neon
NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND=true
NEXT_PUBLIC_NEXUSRAG_REQUIRE_OPERATOR_LOGIN=false
```

## Exact dashboard values
- **Production branch:** `main`
- **Build command:** `npm run build`
- **Build output directory:** `out`
- **Root directory:** `frontend`
- **Node version:** leave default unless your team standardizes it separately

## Backend API base URL
- `NEXT_PUBLIC_API_BASE_URL` must point to the public Koyeb backend URL.
- Example:

```env
NEXT_PUBLIC_API_BASE_URL=https://nexusrag-api-your-org.koyeb.app
```

## Safe exposure rules
- Only `NEXT_PUBLIC_*` variables belong in Cloudflare Pages browser config.
- Never put `DATABASE_URL`, provider API keys, or backend service keys into the Pages project.
