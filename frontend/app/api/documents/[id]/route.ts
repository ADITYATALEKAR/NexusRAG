import { proxyJSON } from '@/lib/server-api'
import {
  BACKEND_PROXY_ENABLED,
  SUPABASE_DATA_ENABLED
} from '@/lib/server-config'
import {
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'
import {
  getAuthenticatedSupabaseUser,
  getStorageBucketName
} from '@/lib/supabase/documents'
import { getSupabaseServerClient } from '@/lib/supabase/server'

export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  if (!SUPABASE_AUTH_ENABLED || BACKEND_PROXY_ENABLED) {
    return proxyJSON(`/documents/${params.id}`, request, { method: 'DELETE' })
  }

  if (!SUPABASE_DATA_ENABLED) {
    return Response.json(
      { message: 'Document deletion requires Supabase data access or an external backend.' },
      { status: 501 }
    )
  }

  const user = await getAuthenticatedSupabaseUser()
  if (!user) {
    return Response.json({ message: 'Sign in is required to delete documents.' }, { status: 401 })
  }

  const supabase = getSupabaseServerClient()
  const { data: row, error: rowError } = await supabase
    .from('document_uploads')
    .select('storage_path, bucket_name')
    .eq('id', params.id)
    .single()

  if (rowError || !row) {
    return Response.json({ message: 'Document not found.' }, { status: 404 })
  }

  await supabase.storage.from(row.bucket_name || getStorageBucketName()).remove([row.storage_path])
  const { error } = await supabase.from('document_uploads').delete().eq('id', params.id)

  if (error) {
    return Response.json(
      { message: `Unable to delete the document from Supabase: ${error.message}` },
      { status: 500 }
    )
  }

  return Response.json({ ok: true, id: params.id })
}
