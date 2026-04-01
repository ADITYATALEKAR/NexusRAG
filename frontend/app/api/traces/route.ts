import { safeProxyJSON } from '@/lib/server-api'

export async function GET(request: Request) {
  const url = new URL(request.url)
  return safeProxyJSON(`/traces${url.search}`, [], request)
}
