'use client'

import Link from 'next/link'
import { ArrowRight, Github } from 'lucide-react'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { GITHUB_REPO_URL } from '@/lib/site-content'

const links = [
  { href: '/#how-it-works', label: 'How it works' },
  { href: '/login', label: 'Bring your own API' },
  { href: '/#contact', label: 'Contact' },
]

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-border-subtle/80 bg-bg-primary/95 backdrop-blur-xl">
      <div className="mx-auto flex h-[84px] w-full max-w-[1920px] items-center justify-between px-6 lg:px-10 xl:px-12 2xl:px-16">
        <Logo iconSize={44} />

        <div className="hidden items-center gap-8 xl:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-[0.95rem] font-medium tracking-[-0.01em] text-text-secondary transition-colors hover:text-text-primary"
            >
              {link.label}
            </Link>
          ))}
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-[0.95rem] font-medium tracking-[-0.01em] text-text-secondary transition-colors hover:text-text-primary"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
          <Button size="lg" className="h-12 px-6" asChild>
            <Link href="/dashboard">
              Try it free
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </nav>
  )
}
