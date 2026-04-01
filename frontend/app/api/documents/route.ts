import { safeProxyJSON } from '@/lib/server-api'
import {
  BACKEND_PROXY_ENABLED,
  SUPABASE_DATA_ENABLED
} from '@/lib/server-config'
import {
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'
import {
  getAuthenticatedSupabaseUser,
  mapDocumentUpload
} from '@/lib/supabase/documents'
import { getSupabaseServerClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
  if (!SUPABASE_AUTH_ENABLED || BACKEND_PROXY_ENABLED) {
    return safeProxyJSON('/documents', [], request)
  }

  if (!SUPABASE_DATA_ENABLED) {
    return Response.json([])
  }

  const user = await getAuthenticatedSupabaseUser()
  if (!user) {
    return Response.json({ message: 'Sign in is required to view documents.' }, { status: 401 })
  }

  const supabase = getSupabaseServerClient()
  const { data, error } = await supabase
    .from('document_uploads')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    return Response.json(
      { message: `Unable to load documents from Supabase: ${error.message}` },
      { status: 500 }
    )
  }

  return Response.json((data || []).map(mapDocumentUpload))
}
