export interface CitationItem {
  chunk_id: string
  document_id: string
  document_name: string
  content: string
  score: number
  citation_key?: string
  page_numbers?: number[]
}

export interface AnswerPayload {
  answer_id: string
  query_id: string
  text: string
  status: 'success' | 'partial' | 'abstained' | 'failed' | 'filtered'
  citations: CitationItem[]
  trace?: {
    latency_ms?: number
    provider_used?: string
    model_used?: string
    prompt_tokens?: number
    completion_tokens?: number
  } | null
}

export interface QueryHistoryItem {
  id: string
  prompt: string
  createdAt: string
  answer?: string
  status: 'idle' | 'loading' | 'success' | 'error'
  citations: CitationItem[]
}

export interface DocumentItem {
  id: string
  name: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  sizeLabel: string
  uploadedAt: string
  parserUsed?: string
  chunksIndexed?: number
  progress?: number
  error?: string
}

export interface MetricsResponse {
  counters?: Record<string, number>
  gauges?: Record<string, number>
  histograms?: Record<string, {
    count?: number
    sum?: number
    avg?: number
    min?: number
    max?: number
    p50?: number
    p95?: number
    p99?: number
  }>
}

export interface CostResponse {
  total_usd: number
  by_model: Record<string, number>
}

export interface EvaluationResponse {
  run_id: string
  dataset_id: string
  avg_latency_ms: number
  total_cost_usd: number
  retrieval_metrics?: Record<string, unknown>
  generation_metrics?: Record<string, unknown>
}

export interface IngestResponse {
  request_id: string
  document_id: string
  status: string
  parser_used?: string
  parser_confidence?: number
  chunks_indexed?: number
  warnings?: string[]
  errors?: string[]
  processing_time_ms?: number
  indexing_job_id?: string
}

export interface ProviderHealthSummary {
  provider_id: string
  vendor: string
  status: string
  avg_latency_ms?: number | null
  successful_requests: number
  failed_requests: number
}

export interface TraceSpan {
  trace_id: string
  span_id: string
  parent_span_id?: string | null
  operation: string
  service: string
  start_time: string
  end_time?: string | null
  status: string
  attributes?: Record<string, unknown>
}
