import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

import { AUTH_SECRET, DEFAULT_BACKEND_URL } from '@/lib/auth'

type ProxyRequest = Request | NextRequest

function buildBackendUrl(path: string, apiUrl: string) {
  return `${apiUrl.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}

async function getBackendContext(request?: ProxyRequest, headers?: HeadersInit) {
  const requestHeaders = new Headers(headers)
  const headerApiKey = requestHeaders.get('X-API-Key') || undefined
  const headerApiUrl = requestHeaders.get('X-Backend-Url') || undefined

  if (!request) {
    return {
      apiKey: headerApiKey,
      apiUrl: headerApiUrl || DEFAULT_BACKEND_URL
    }
  }

  const token = await getToken({
    req: request as NextRequest,
    secret: AUTH_SECRET
  }).catch(() => null)

  return {
    apiKey: headerApiKey || (typeof token?.apiKey === 'string' ? token.apiKey : undefined),
    apiUrl: headerApiUrl || (typeof token?.apiUrl === 'string' ? token.apiUrl : DEFAULT_BACKEND_URL)
  }
}

export async function proxyJSON(path: string, request?: ProxyRequest, init: RequestInit = {}) {
  const backend = await getBackendContext(request, init.headers)
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
