export const PUBLIC_APP_ENABLED =
  process.env.NEXT_PUBLIC_NEXUSRAG_PUBLIC_APP !== 'false'

export const PUBLIC_APP_NAME =
  process.env.NEXT_PUBLIC_NEXUSRAG_APP_NAME || 'NexusRAG'

export const DEFAULT_PUBLIC_BACKEND_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000'

export const DEPLOYMENT_TARGET =
  process.env.NEXT_PUBLIC_NEXUSRAG_DEPLOYMENT_TARGET ||
  'cloudflare-pages-render-neon'

export const EXTERNAL_BACKEND_ENABLED =
  process.env.NEXT_PUBLIC_NEXUSRAG_EXTERNAL_BACKEND !== 'false'

export const REQUIRE_OPERATOR_LOGIN =
  process.env.NEXT_PUBLIC_NEXUSRAG_REQUIRE_OPERATOR_LOGIN === 'true'

export const PUBLIC_DEMO_MODE =
  PUBLIC_APP_ENABLED && !REQUIRE_OPERATOR_LOGIN

export const PUBLIC_TRIAL_QUERY_LIMIT = Number(
  process.env.NEXT_PUBLIC_NEXUSRAG_TRIAL_QUERY_LIMIT || '2'
)
