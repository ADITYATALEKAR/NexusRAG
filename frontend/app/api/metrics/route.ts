import { proxyJSON } from '@/lib/server-api'

export async function GET(request: Request) {
  const url = new URL(request.url)
  return proxyJSON(`/metrics${url.search}`, request)
}
