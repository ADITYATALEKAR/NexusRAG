import type { DefaultSession } from 'next-auth'

declare module 'next-auth' {
  interface User {
    apiUrl?: string
    apiKey?: string
  }

  interface Session {
    apiUrl?: string
    user?: DefaultSession['user']
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    apiUrl?: string
    apiKey?: string
  }
}
