import Link from 'next/link'

import { Logo } from '@/components/shared/logo'

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-bg-primary">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 md:flex-row md:items-center md:justify-between">
        <Logo />
        <div className="flex flex-wrap items-center gap-5 text-sm text-text-secondary">
          <Link href="/login" className="hover:text-text-primary">Sign in</Link>
          <Link href="/signup" className="hover:text-text-primary">Create workspace</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-text-primary">Source</a>
        </div>
      </div>
    </footer>
  )
}