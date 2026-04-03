import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { GITHUB_REPO_URL } from '@/lib/site-content'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto grid max-w-[1440px] gap-8 px-6 py-12 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(260px,320px)]">
        <div className="space-y-4">
          <Logo />
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
              <p>Frontend - Cloudflare Pages</p>
              <p>API - Render (FastAPI)</p>
              <p>Data - Neon Postgres + pgvector</p>
              <p>LLM - GPT-4o + multi-provider failover</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-text-primary">Deployment</p>
          <div className="space-y-2 text-sm leading-6 text-text-secondary">
            <p>Hosted evaluation for quick trials.</p>
            <p>Bring Your Own API for unlimited usage.</p>
            <p>Public GitHub repo and live cloud deployment available today.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
