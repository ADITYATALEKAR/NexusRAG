import type { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { z } from 'zod'

export const AUTH_SECRET = process.env.NEXTAUTH_SECRET || 'vectorcore-dev-secret-change-me'
export const DEFAULT_BACKEND_URL =
  process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const credentialsSchema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

function normalizeBackendUrl(apiUrl: string) {
  return apiUrl.replace(/\/$/, '')
}

async function verifyBackendAccess(apiUrl: string, apiKey: string) {
  const baseUrl = normalizeBackendUrl(apiUrl)
  const headers = { 'X-API-Key': apiKey }

  try {
    const response = await fetch(`${baseUrl}/providers/health`, {
      headers,
      cache: 'no-store'
    })
    if (response.status === 401 || response.status === 403) {
      return false
    }
    return response.ok || response.status === 503
  } catch {
    try {
      const healthResponse = await fetch(`${baseUrl}/health`, {
        headers,
        cache: 'no-store'
      })
      return healthResponse.ok || healthResponse.status === 503
    } catch {
      return false
    }
  }
}

export const authOptions: NextAuthOptions = {
  secret: AUTH_SECRET,
  session: {
    strategy: 'jwt'
  },
  pages: {
    signIn: '/login'
  },
  providers: [
    CredentialsProvider({
      name: 'API Key',
      credentials: {
        apiUrl: { label: 'API URL', type: 'text' },
        apiKey: { label: 'API Key', type: 'password' }
      },
      async authorize(credentials) {
        const parsed = credentialsSchema.safeParse(credentials)
        if (!parsed.success) {
          return null
        }

        const apiUrl = normalizeBackendUrl(parsed.data.apiUrl)
        const apiKey = parsed.data.apiKey.trim()
        const isReachable = await verifyBackendAccess(apiUrl, apiKey)
        if (!isReachable) {
          return null
        }

        return {
          id: 'vectorcore-operator',
          name: 'VectorCore Operator',
          apiUrl,
          apiKey
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.apiUrl = typeof user.apiUrl === 'string' ? user.apiUrl : DEFAULT_BACKEND_URL
        token.apiKey = typeof user.apiKey === 'string' ? user.apiKey : undefined
      }
      return token
    },
    async session({ session, token }) {
      session.apiUrl = typeof token.apiUrl === 'string' ? token.apiUrl : DEFAULT_BACKEND_URL
      if (session.user) {
        session.user.name = session.user.name || 'VectorCore Operator'
      }
      return session
    }
  }
}
