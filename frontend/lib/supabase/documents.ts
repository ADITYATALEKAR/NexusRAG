import 'server-only'

import type { User } from '@supabase/supabase-js'

import { SUPABASE_STORAGE_BUCKET } from '@/lib/server-config'
import { getSupabaseServerClient } from '@/lib/supabase/server'

export interface DocumentUploadRow {
  id: string
  owner_id: string
  file_name: string
  storage_path: string
  bucket_name: string
  file_size: number | null
  mime_type: string | null
  status: string
  source: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export async function getAuthenticatedSupabaseUser(): Promise<User | null> {
  const supabase = getSupabaseServerClient()
  const {
    data: { user }
  } = await supabase.auth.getUser()

  return user
}

export function formatBytes(size: number | null | undefined): string {
  const bytes = size || 0
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function mapDocumentUpload(row: DocumentUploadRow) {
  const statusMap: Record<string, 'queued' | 'processing' | 'completed' | 'failed'> = {
    uploaded: 'queued',
    queued: 'queued',
    processing: 'processing',
    indexed: 'completed',
    completed: 'completed',
    failed: 'failed'
  }

  return {
    id: row.id,
    name: row.file_name,
    status: statusMap[row.status] || 'queued',
    sizeLabel: formatBytes(row.file_size),
    uploadedAt: row.created_at,
    parserUsed: row.source === 'supabase_storage' ? 'supabase-storage' : row.source,
    chunksIndexed: row.status === 'indexed' || row.status === 'completed' ? 0 : undefined,
    error: row.error_message || undefined
  }
}

export function buildStoragePath(userId: string, documentId: string, fileName: string): string {
  const safeName = fileName
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'document'

  return `${userId}/${documentId}/${safeName}`
}

export function getStorageBucketName() {
  return SUPABASE_STORAGE_BUCKET
}
