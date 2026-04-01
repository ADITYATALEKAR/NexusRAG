import { proxyJSON } from '@/lib/server-api'
import {
  BACKEND_PROXY_ENABLED,
  SUPABASE_DATA_ENABLED
} from '@/lib/server-config'
import {
  DEPLOYMENT_TARGET,
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'

export async function GET(request: Request) {
  if (!SUPABASE_AUTH_ENABLED || BACKEND_PROXY_ENABLED) {
    return proxyJSON('/health', request)
  }

  return Response.json({
    status: SUPABASE_AUTH_ENABLED || SUPABASE_DATA_ENABLED ? 'degraded' : 'setup_required',
    deployment_target: DEPLOYMENT_TARGET,
    external_backend_connected: false,
    supabase_auth_enabled: SUPABASE_AUTH_ENABLED,
    supabase_data_enabled: SUPABASE_DATA_ENABLED,
    message:
      'The frontend is running in Vercel + Supabase mode. The external Python RAG backend is not attached, so query and evaluation endpoints remain unavailable.'
  })
}
