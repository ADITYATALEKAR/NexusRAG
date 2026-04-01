import { safeProxyJSON } from '@/lib/server-api'

export async function GET(request: Request) {
  return safeProxyJSON('/providers/health', [], request)
}
