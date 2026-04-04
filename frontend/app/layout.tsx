import type { Metadata } from 'next'
import { IBM_Plex_Mono, IBM_Plex_Sans } from 'next/font/google'

import { Providers } from '@/app/providers'
import { ErrorBoundary } from '@/components/shared/error-boundary'
import '@/styles/globals.css'

const plexSans = IBM_Plex_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['400', '500', '600', '700'],
})
const plexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500'],
})

export const metadata: Metadata = {
  title: 'NexusRAG',
  description: 'Enterprise RAG with evidence built in.'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${plexSans.variable} ${plexMono.variable} min-h-screen bg-bg-primary text-text-primary`}>
        <Providers>
          <ErrorBoundary>{children}</ErrorBoundary>
        </Providers>
      </body>
    </html>
  )
}

