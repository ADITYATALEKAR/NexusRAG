import { proxyJSON } from '@/lib/server-api'

export async function POST(request: Request) {
  return proxyJSON(
    '/answer',
    request,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: await request.text()
    }
  )
}
