import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { GITHUB_REPO_URL, FOUNDER_CONTACT } from '@/lib/site-content'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto grid max-w-6xl gap-8 px-6 py-12 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(260px,320px)]">
        <div className="space-y-4">
          <Logo />
          <p className="max-w-sm text-sm leading-6 text-text-secondary">
            NexusRAG is a citation-first retrieval workspace for teams that need grounded answers,
            clear source evidence, and a deployment path they can actually operate.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Product</p>
            <div className="space-y-2 text-sm text-text-secondary">
              <Link href="/dashboard" className="block hover:text-text-primary">
                Open live workspace
              </Link>
              <Link href="/login" className="block hover:text-text-primary">
                Use your own API
              </Link>
              <Link href="/#how-to-use" className="block hover:text-text-primary">
                How to use NexusRAG
              </Link>
              <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" className="block hover:text-text-primary">
                Source repository
              </a>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Architecture</p>
            <div className="space-y-2 text-sm leading-6 text-text-secondary">
              <p>Frontend: Cloudflare Pages</p>
              <p>Backend: Render-hosted NexusRAG API</p>
              <p>Data layer: Neon Postgres + pgvector</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-text-primary">Founder contact</p>
          <div className="space-y-2 text-sm leading-6 text-text-secondary">
            <p className="font-medium text-text-primary">{FOUNDER_CONTACT.name}</p>
            <p>{FOUNDER_CONTACT.role}</p>
            <a href={`mailto:${FOUNDER_CONTACT.email}`} className="block hover:text-text-primary">
              {FOUNDER_CONTACT.email}
            </a>
            <a href={`tel:${FOUNDER_CONTACT.phone.replace(/\s+/g, '')}`} className="block hover:text-text-primary">
              {FOUNDER_CONTACT.phone}
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
