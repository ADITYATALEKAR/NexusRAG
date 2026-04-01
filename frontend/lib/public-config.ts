export const PUBLIC_APP_ENABLED = process.env.NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP === 'true'

export const DEFAULT_PUBLIC_BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const PUBLIC_APP_NAME =
  process.env.NEXT_PUBLIC_NEXUSRAG_APP_NAME || 'NexusRAG'
