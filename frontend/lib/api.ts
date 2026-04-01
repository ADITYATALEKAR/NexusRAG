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
import { DEFAULT_PUBLIC_BACKEND_URL } from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'

export class APIError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'APIError'
    this.status = status
  }
}

function normalizeBaseUrl(url?: string | null) {
  return (url || DEFAULT_PUBLIC_BACKEND_URL).replace(/\/$/, '')
}

function buildHeaders(options?: HeadersInit) {
  const headers = new Headers(options)
  const { operatorApiKey } = useAppStore.getState()
  if (operatorApiKey && !headers.has('X-API-Key')) {
    headers.set('X-API-Key', operatorApiKey)
  }
  return headers
}

function buildBackendUrl(path: string) {
  const { operatorApiUrl } = useAppStore.getState()
  const base = normalizeBaseUrl(operatorApiUrl)
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalizedPath}`
}

class APIClient {
  private async fetchJSON<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = buildHeaders(options.headers)
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(buildBackendUrl(path), {
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

  async uploadDocument(file: File, onProgress?: (value: number) => void) {
    return new Promise<IngestResponse>((resolve, reject) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('metadata', '{}')

      const request = new XMLHttpRequest()
      request.open('POST', buildBackendUrl('/ingest'))
      request.responseType = 'json'

      const { operatorApiKey } = useAppStore.getState()
      if (operatorApiKey) {
        request.setRequestHeader('X-API-Key', operatorApiKey)
      }

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
