import { proxyJSON } from '@/lib/server-api'

export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  return proxyJSON(`/documents/${params.id}`, request, { method: 'DELETE' })
}
