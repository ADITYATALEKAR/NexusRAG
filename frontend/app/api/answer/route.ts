import { proxyJSON, externalBackendUnavailableResponse } from '@/lib/server-api'
import { BACKEND_PROXY_ENABLED } from '@/lib/server-config'
import { SUPABASE_AUTH_ENABLED } from '@/lib/public-config'

export async function POST(request: Request) {
  if (SUPABASE_AUTH_ENABLED && !BACKEND_PROXY_ENABLED) {
    return externalBackendUnavailableResponse('Answer generation')
  }

  return proxyJSON('/answer', request, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: await request.text()
  })
}
