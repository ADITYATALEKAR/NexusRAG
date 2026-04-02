import Link from 'next/link'

import { GITHUB_REPO_URL, FOUNDER_CONTACT } from '@/lib/site-content'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto grid max-w-6xl gap-8 px-6 py-12 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(260px,320px)]">
        <div className="space-y-4">
          <Link href="/" className="flex items-center gap-2.5" aria-label="NexusRAG home">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-600 text-sm font-bold text-white dark:bg-accent-500">
              &lt;&gt;
            </span>
            <div className="flex flex-col leading-none">
              <span className="text-base font-semibold tracking-tight text-text-primary">
                NexusRAG
              </span>
              <span className="text-[10px] font-medium tracking-wide text-text-tertiary">
                by Fundamental Labs
              </span>
            </div>
          </Link>
          <p className="max-w-sm text-sm leading-6 text-text-secondary">
            Open-source enterprise RAG with hybrid retrieval, citation-backed answers,
            and a self-hostable production stack.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Product</p>
            <div className="space-y-2 text-sm text-text-secondary">
              <Link href="/dashboard" className="block hover:text-text-primary">
                Open workspace
              </Link>
              <Link href="/login" className="block hover:text-text-primary">
                Connect your API
              </Link>
              <Link href="/#how-it-works" className="block hover:text-text-primary">
                How it works
              </Link>
              <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer" className="block hover:text-text-primary">
                GitHub repository
              </a>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Stack</p>
            <div className="space-y-2 text-sm leading-6 text-text-secondary">
              <p>Frontend — Cloudflare Pages</p>
              <p>API — Render (FastAPI)</p>
              <p>Data — Neon Postgres + pgvector</p>
              <p>LLM — GPT-4o + multi-provider failover</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-text-primary">Contact</p>
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
