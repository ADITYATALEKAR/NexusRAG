'use client'

import Link from 'next/link'
import { ArrowRight, Github } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { GITHUB_REPO_URL } from '@/lib/site-content'

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-border-subtle bg-bg-primary/80 backdrop-blur-lg">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between px-6 py-3">
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

        <div className="hidden items-center gap-1 md:flex">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/#how-it-works">How it works</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/#features">Features</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/#architecture">Architecture</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <a href={GITHUB_REPO_URL} target="_blank" rel="noreferrer">
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </Button>
          <Button size="sm" asChild>
            <Link href="/dashboard">
              Try it free
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </div>
    </nav>
  )
}
