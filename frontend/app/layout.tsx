import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { getServerSession } from 'next-auth'

import { authOptions } from '@/lib/auth'
import { Providers } from '@/app/providers'
import { ErrorBoundary } from '@/components/shared/error-boundary'
import { SUPABASE_AUTH_ENABLED } from '@/lib/public-config'
import '@/styles/globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata: Metadata = {
  title: 'NexusRAG',
  description: 'Enterprise-ready retrieval operating system with calm, citation-backed UX.'
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const session = SUPABASE_AUTH_ENABLED ? null : await getServerSession(authOptions)

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} min-h-screen bg-bg-primary text-text-primary`}>
        <Providers session={session}>
          <ErrorBoundary>{children}</ErrorBoundary>
        </Providers>
      </body>
    </html>
  )
}
