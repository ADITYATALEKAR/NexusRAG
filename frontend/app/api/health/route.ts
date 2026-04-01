import { proxyJSON } from '@/lib/server-api'

export async function GET(request: Request) {
  return proxyJSON('/health', request)
}
