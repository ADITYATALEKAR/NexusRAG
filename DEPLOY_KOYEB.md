# Deploy NexusRAG Backend on Koyeb

## Service type
- **Web Service**
- deploy from **GitHub**

## Build settings
- **Repository:** `ADITYATALEKAR/NexusRAG`
- **Branch:** `main`
- **Build method:** Dockerfile
- **Dockerfile path:** `Dockerfile`
- **Context:** repository root
- **Exposed port:** `8000`
- **Health check path:** `/health/liveness`
- **Auto-deploy:** enable it

## Start behavior
- The container command binds to `0.0.0.0:${PORT:-8000}`.
- Koyeb can supply `PORT`; the Dockerfile now respects it.

## Required environment variables
Set these in the Koyeb dashboard:

```env
PORT=8000
DATABASE_URL=postgresql://user:password@your-neon-host/dbname?sslmode=require
RAG__ENV=production
RAG__DEBUG=false
RAG__LOG_LEVEL=info
RAG__SERVER__HOST=0.0.0.0
RAG__SERVER__PORT=8000
RAG__SERVER__WORKERS=1
RAG__SECURITY__API_KEY_REQUIRED=false
RAG__SECURITY__RATE_LIMIT_ENABLED=true
RAG__SECURITY__CORS_ORIGINS=https://your-cloudflare-pages-domain.pages.dev
RAG__SECURITY__CORS_ALLOW_CREDENTIALS=false
NEXUSRAG_PUBLIC_DEMO_MODE=true
NEXUSRAG_UPLOAD_DIR=/tmp/nexusrag-uploads
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
```

## Optional self-host/operator mode variables
Use these only if you want to keep API-key protection enabled:

```env
RAG__SECURITY__API_KEY_REQUIRED=true
RAG__SECURITY__API_KEYS=rag_live_your_key_here
NEXUSRAG_PUBLIC_DEMO_MODE=false
```

## Exact Koyeb dashboard values
- **Service type:** Web Service
- **Source:** GitHub
- **Dockerfile path:** `Dockerfile`
- **HTTP port:** `8000`
- **Health check:** `/health/liveness`
- **Region:** choose the closest free region to your users
- **Auto-deploy:** On

## Free-tier limitations to watch
- cold starts and service sleeping
- ephemeral filesystem, so uploads must be treated as temporary
- one small service is realistic; avoid extra worker services unless you truly need them
