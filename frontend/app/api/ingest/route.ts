import { proxyMultipart, externalBackendUnavailableResponse } from '@/lib/server-api'
import {
  BACKEND_PROXY_ENABLED,
  SUPABASE_DATA_ENABLED
} from '@/lib/server-config'
import {
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'
import {
  buildStoragePath,
  getAuthenticatedSupabaseUser,
  getStorageBucketName
} from '@/lib/supabase/documents'
import { getSupabaseServerClient } from '@/lib/supabase/server'

export async function POST(request: Request) {
  if (!SUPABASE_AUTH_ENABLED || BACKEND_PROXY_ENABLED) {
    const formData = await request.formData()
    return proxyMultipart('/ingest', request, formData)
  }

  if (!SUPABASE_DATA_ENABLED) {
    return externalBackendUnavailableResponse('Document ingestion')
  }

  const user = await getAuthenticatedSupabaseUser()
  if (!user) {
    return Response.json({ message: 'Sign in is required to upload documents.' }, { status: 401 })
  }

  const formData = await request.formData()
  const file = formData.get('file')

  if (!(file instanceof File)) {
    return Response.json({ message: 'Upload payload is missing a file.' }, { status: 400 })
  }

  const documentId = crypto.randomUUID()
  const storagePath = buildStoragePath(user.id, documentId, file.name)
  const bucket = getStorageBucketName()
  const bytes = await file.arrayBuffer()
  const supabase = getSupabaseServerClient()

  const uploadResult = await supabase.storage.from(bucket).upload(storagePath, bytes, {
    contentType: file.type || 'application/octet-stream',
    upsert: false
  })

  if (uploadResult.error) {
    return Response.json(
      { message: `Unable to store the document in Supabase Storage: ${uploadResult.error.message}` },
      { status: 500 }
    )
  }

  const insertResult = await supabase.from('document_uploads').insert({
    id: documentId,
    owner_id: user.id,
    file_name: file.name,
    storage_path: storagePath,
    bucket_name: bucket,
    file_size: file.size,
    mime_type: file.type || null,
    status: 'uploaded',
    source: 'supabase_storage'
  })

  if (insertResult.error) {
    await supabase.storage.from(bucket).remove([storagePath])
    return Response.json(
      { message: `Unable to save document metadata in Supabase: ${insertResult.error.message}` },
      { status: 500 }
    )
  }

  return Response.json({
    request_id: documentId,
    document_id: documentId,
    status: 'queued',
    parser_used: 'supabase-storage',
    parser_confidence: 1,
    chunks_indexed: 0,
    warnings: [
      'The document is stored in Supabase and staged for future processing. Deploy the external Python backend later to enable indexing and answering.'
    ],
    errors: [],
    processing_time_ms: 0,
    indexing_job_id: null
  })
}
