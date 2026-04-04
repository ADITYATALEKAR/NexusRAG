import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { GITHUB_REPO_URL } from '@/lib/site-content'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto grid w-full max-w-[1920px] gap-8 px-6 py-12 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:px-8 xl:px-10 2xl:px-12">
        <div className="space-y-4">
          <Logo />
          <p className="max-w-sm text-sm leading-6 text-text-secondary">
            Open-source enterprise RAG for grounded answers from private knowledge.
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
              <a
                href={GITHUB_REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="block hover:text-text-primary"
              >
                GitHub repository
              </a>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Designed for</p>
            <div className="space-y-2 text-sm leading-6 text-text-secondary">
              <p>Private knowledge workspaces</p>
              <p>Internal search and support enablement</p>
              <p>Developer-grade retrieval rollouts</p>
              <p>Teams that need cited answers</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

