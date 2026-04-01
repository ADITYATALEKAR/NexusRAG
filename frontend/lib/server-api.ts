import 'server-only'

import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

import { AUTH_SECRET } from '@/lib/auth'
import {
  BACKEND_API_URL,
  BACKEND_SERVICE_API_KEY
} from '@/lib/server-config'

type ProxyRequest = Request | NextRequest

const MISSING_BACKEND_MESSAGE =
  'The external Python RAG backend is not configured for this deployment. Deploy it separately and set BACKEND_API_URL, or sign in with operator credentials that include a backend URL.'

function buildBackendUrl(path: string, apiUrl: string) {
  return `${apiUrl.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}

async function getBackendContext(request?: ProxyRequest, headers?: HeadersInit) {
  const requestHeaders = new Headers(headers)
  const headerApiKey = requestHeaders.get('X-API-Key') || undefined
  const headerApiUrl = requestHeaders.get('X-Backend-Url') || undefined

  if (!request) {
    return {
      apiKey: headerApiKey || BACKEND_SERVICE_API_KEY,
      apiUrl: headerApiUrl || BACKEND_API_URL
    }
  }

  const token = await getToken({
    req: request as NextRequest,
    secret: AUTH_SECRET
  }).catch(() => null)

  return {
    apiKey:
      headerApiKey ||
      (typeof token?.apiKey === 'string' ? token.apiKey : undefined) ||
      BACKEND_SERVICE_API_KEY,
    apiUrl:
      headerApiUrl ||
      (typeof token?.apiUrl === 'string' ? token.apiUrl : undefined) ||
      BACKEND_API_URL
  }
}

function missingBackendResponse() {
  return Response.json({ message: MISSING_BACKEND_MESSAGE }, { status: 501 })
}

export async function hasAvailableBackend(request?: ProxyRequest, headers?: HeadersInit) {
  const backend = await getBackendContext(request, headers)
  return Boolean(backend.apiUrl)
}

export function externalBackendUnavailableResponse(feature: string) {
  return Response.json(
    {
      message: `${feature} requires the external Python RAG backend. Set BACKEND_API_URL in Vercel or supply an operator backend URL through the credentials mode.`
    },
    { status: 501 }
  )
}

export async function proxyJSON(path: string, request?: ProxyRequest, init: RequestInit = {}) {
  const backend = await getBackendContext(request, init.headers)
  if (!backend.apiUrl) {
    return missingBackendResponse()
  }

  const headers = new Headers(init.headers)
  if (backend.apiKey && !headers.has('X-API-Key')) {
    headers.set('X-API-Key', backend.apiKey)
  }

  const response = await fetch(buildBackendUrl(path, backend.apiUrl), {
    ...init,
    headers,
    cache: 'no-store'
  })

  const bodyText = await response.text()
  const contentType = response.headers.get('content-type') || 'application/json'
  return new Response(bodyText, {
    status: response.status,
    headers: { 'content-type': contentType }
  })
}

export async function safeProxyJSON(
  path: string,
  fallback: unknown,
  request?: ProxyRequest,
  init: RequestInit = {}
) {
  try {
    const backend = await getBackendContext(request, init.headers)
    if (!backend.apiUrl) {
      return Response.json(fallback)
    }

    const headers = new Headers(init.headers)
    if (backend.apiKey && !headers.has('X-API-Key')) {
      headers.set('X-API-Key', backend.apiKey)
    }

    const response = await fetch(buildBackendUrl(path, backend.apiUrl), {
      ...init,
      headers,
      cache: 'no-store'
    })
    if (!response.ok) {
      return Response.json(fallback)
    }
    const payload = await response.json().catch(() => fallback)
    return Response.json(payload)
  } catch {
    return Response.json(fallback)
  }
}

export async function proxyMultipart(path: string, request: ProxyRequest, formData: FormData) {
  const backend = await getBackendContext(request)
  if (!backend.apiUrl) {
    return missingBackendResponse()
  }

  const headers = backend.apiKey ? { 'X-API-Key': backend.apiKey } : undefined

  const response = await fetch(buildBackendUrl(path, backend.apiUrl), {
    method: 'POST',
    headers,
    body: formData,
    cache: 'no-store'
  })
  const bodyText = await response.text()
  return new Response(bodyText, {
    status: response.status,
    headers: { 'content-type': response.headers.get('content-type') || 'application/json' }
  })
}
