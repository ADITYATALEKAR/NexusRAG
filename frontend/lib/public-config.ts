export const PUBLIC_APP_ENABLED = process.env.NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP === 'true'

export const PUBLIC_APP_NAME =
  process.env.NEXT_PUBLIC_NEXUSRAG_APP_NAME || 'NexusRAG'

export const DEFAULT_PUBLIC_BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const PUBLIC_SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || ''

export const PUBLIC_SUPABASE_ANON_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  ''

export const PUBLIC_SUPABASE_STORAGE_BUCKET =
  process.env.NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET || 'documents'

export const SUPABASE_AUTH_ENABLED = Boolean(
  PUBLIC_SUPABASE_URL && PUBLIC_SUPABASE_ANON_KEY
)

export const EXTERNAL_BACKEND_ENABLED =
  process.env.NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND === 'true'

export const DEPLOYMENT_TARGET =
  process.env.NEXT_PUBLIC_NEXUSRAG_DEPLOYMENT_TARGET ||
  (SUPABASE_AUTH_ENABLED ? 'vercel-supabase' : 'hybrid')
