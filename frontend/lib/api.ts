import type {
  AnswerPayload,
  CostResponse,
  DocumentItem,
  EvaluationResponse,
  IngestResponse,
  MetricsResponse,
  ProviderHealthSummary,
  TraceSpan
} from '@/lib/types'
import {
  EXTERNAL_BACKEND_ENABLED,
  PUBLIC_SUPABASE_STORAGE_BUCKET,
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'
import { getSupabaseBrowserClient } from '@/lib/supabase/browser'

const API_BASE = '/api'

export class APIError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'APIError'
    this.status = status
  }
}

function buildUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${normalizedPath}`
}

function sanitizeStorageName(fileName: string) {
  return (
    fileName
      .toLowerCase()
      .replace(/[^a-z0-9._-]+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '') || 'document'
  )
}

class APIClient {
  private async fetchJSON<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(buildUrl(path), {
      ...options,
      headers,
      cache: 'no-store'
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => ({ message: 'Request failed' }))
      throw new APIError(response.status, payload.detail || payload.message || 'Request failed')
    }

    if (response.status === 204) {
      return undefined as T
    }

    return response.json() as Promise<T>
  }

  async query(text: string, topK = 5) {
    return this.fetchJSON<AnswerPayload>('/answer', {
      method: 'POST',
      body: JSON.stringify({ query: text, top_k: topK, include_trace: true })
    })
  }

  async getDocuments() {
    const items = await this.fetchJSON<Array<Record<string, unknown>>>('/documents')
    return items.map((item) => ({
      id: String(item.id || ''),
      name: String(item.name || item.id || 'Untitled document'),
      status: (item.status as DocumentItem['status']) || 'completed',
      sizeLabel: String(item.sizeLabel || item.size_label || 'Unknown'),
      uploadedAt: String(item.uploadedAt || item.uploaded_at || new Date().toISOString()),
      parserUsed: item.parserUsed
        ? String(item.parserUsed)
        : item.parser_used
          ? String(item.parser_used)
          : undefined,
      chunksIndexed:
        typeof item.chunksIndexed === 'number'
          ? item.chunksIndexed
          : typeof item.chunks_indexed === 'number'
            ? item.chunks_indexed
            : undefined
    }))
  }

  private async uploadDocumentToSupabase(file: File, onProgress?: (value: number) => void) {
    const supabase = getSupabaseBrowserClient()
    const {
      data: { user }
    } = await supabase.auth.getUser()

    if (!user) {
      throw new APIError(401, 'Sign in is required to upload documents.')
    }

    const documentId = crypto.randomUUID()
    const storagePath = `${user.id}/${documentId}/${sanitizeStorageName(file.name)}`

    onProgress?.(10)
    const upload = await supabase.storage
      .from(PUBLIC_SUPABASE_STORAGE_BUCKET)
      .upload(storagePath, file, {
        contentType: file.type || 'application/octet-stream',
        upsert: false
      })

    if (upload.error) {
      throw new APIError(500, upload.error.message)
    }

    onProgress?.(75)
    const insert = await supabase.from('document_uploads').insert({
      id: documentId,
      owner_id: user.id,
      file_name: file.name,
      storage_path: storagePath,
      bucket_name: PUBLIC_SUPABASE_STORAGE_BUCKET,
      file_size: file.size,
      mime_type: file.type || null,
      status: 'uploaded',
      source: 'supabase_storage'
    })

    if (insert.error) {
      await supabase.storage.from(PUBLIC_SUPABASE_STORAGE_BUCKET).remove([storagePath])
      throw new APIError(500, insert.error.message)
    }

    onProgress?.(100)
    return {
      request_id: documentId,
      document_id: documentId,
      status: 'queued',
      parser_used: 'supabase-storage',
      parser_confidence: 1,
      chunks_indexed: 0,
      warnings: [
        'Stored in Supabase Storage. Attach the external Python RAG backend later to process and index this document.'
      ],
      errors: [],
      processing_time_ms: 0,
      indexing_job_id: undefined
    } satisfies IngestResponse
  }

  async uploadDocument(file: File, onProgress?: (value: number) => void) {
    if (SUPABASE_AUTH_ENABLED && !EXTERNAL_BACKEND_ENABLED) {
      return this.uploadDocumentToSupabase(file, onProgress)
    }

    return new Promise<IngestResponse>((resolve, reject) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('metadata', '{}')

      const request = new XMLHttpRequest()
      request.open('POST', buildUrl('/ingest'))
      request.responseType = 'json'

      request.upload.onprogress = (event) => {
        if (!event.lengthComputable) {
          return
        }
        const progress = Math.min(100, Math.round((event.loaded / event.total) * 100))
        onProgress?.(progress)
      }

      request.onload = () => {
        const payload = (request.response || {}) as Partial<IngestResponse> & {
          detail?: string
          message?: string
        }
        if (request.status >= 200 && request.status < 300) {
          onProgress?.(100)
          resolve(payload as IngestResponse)
          return
        }
        reject(new APIError(request.status, String(payload.detail || payload.message || 'Upload failed')))
      }

      request.onerror = () => reject(new APIError(0, 'Upload failed'))
      request.send(formData)
    })
  }

  async deleteDocument(id: string) {
    return this.fetchJSON<{ ok: boolean; id: string }>('/documents/' + id, { method: 'DELETE' })
  }

  async getMetrics() {
    return this.fetchJSON<MetricsResponse>('/metrics')
  }

  async getCosts(hours = 24) {
    return this.fetchJSON<CostResponse>(`/costs?hours=${hours}`)
  }

  async getTraces(limit = 100) {
    return this.fetchJSON<TraceSpan[]>(`/traces?limit=${limit}`)
  }

  async health() {
    return this.fetchJSON<Record<string, unknown>>('/health')
  }

  async evaluate(datasetId: string) {
    return this.fetchJSON<EvaluationResponse>('/evaluate', {
      method: 'POST',
      body: JSON.stringify({ dataset_id: datasetId })
    })
  }

  async getProvidersHealth() {
    return this.fetchJSON<ProviderHealthSummary[]>('/providers/health')
  }
}

export const api = new APIClient()
