import 'server-only'

import {
  PUBLIC_SUPABASE_ANON_KEY,
  PUBLIC_SUPABASE_URL
} from '@/lib/public-config'

export const BACKEND_API_URL = process.env.BACKEND_API_URL || ''

export const BACKEND_SERVICE_API_KEY =
  process.env.BACKEND_SERVICE_API_KEY || process.env.NEXUSRAG_SERVICE_API_KEY || ''

export const BACKEND_PROXY_ENABLED = Boolean(BACKEND_API_URL)

export const SUPABASE_SERVICE_ROLE_KEY =
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''

export const SUPABASE_STORAGE_BUCKET =
  process.env.SUPABASE_STORAGE_BUCKET || 'documents'

export const SUPABASE_DATA_ENABLED = Boolean(
  PUBLIC_SUPABASE_URL && PUBLIC_SUPABASE_ANON_KEY
)
