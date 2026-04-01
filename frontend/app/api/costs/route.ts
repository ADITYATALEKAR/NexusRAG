import { safeProxyJSON } from '@/lib/server-api'

export async function GET(request: Request) {
  const url = new URL(request.url)
  return safeProxyJSON(`/costs${url.search}`, { total_usd: 0, by_model: {} }, request)
}
