import { proxyMultipart } from '@/lib/server-api'

export async function POST(request: Request) {
  const formData = await request.formData()
  return proxyMultipart('/ingest', request, formData)
}
