import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { FOUNDER_CONTACT, GITHUB_REPO_URL } from '@/lib/site-content'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto w-full max-w-[1920px] px-6 py-12 lg:px-8 xl:px-10 2xl:px-12">
        <div className="grid gap-12 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)]">
          <div className="space-y-4">
            <Logo />
            <p className="max-w-sm text-sm leading-6 text-text-secondary">
              Open-source enterprise RAG for grounded answers from private knowledge.
            </p>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-semibold text-text-primary">Contact</p>
            <div className="space-y-2 text-sm leading-6 text-text-secondary">
              <p className="font-medium text-text-primary">{FOUNDER_CONTACT.name}</p>
              <p>{FOUNDER_CONTACT.role}</p>
              <a href={`mailto:${FOUNDER_CONTACT.email}`} className="block hover:text-text-primary">
                {FOUNDER_CONTACT.email}
              </a>
              <a
                href={`tel:${FOUNDER_CONTACT.phone.replace(/\s+/g, '')}`}
                className="block hover:text-text-primary"
              >
                {FOUNDER_CONTACT.phone}
              </a>
            </div>
          </div>

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

        <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-border-subtle pt-6 text-xs text-text-tertiary sm:flex-row">
          <p>&copy; {new Date().getFullYear()} Fundamental Labs. All rights reserved.</p>
          <div className="flex gap-6">
            <Link href="/terms" className="hover:text-text-secondary">
              Terms of Use
            </Link>
            <Link href="/privacy" className="hover:text-text-secondary">
              Privacy Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
