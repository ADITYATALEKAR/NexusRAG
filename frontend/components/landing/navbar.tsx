'use client'

import Link from 'next/link'
import { ArrowRight, Github } from 'lucide-react'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { GITHUB_REPO_URL } from '@/lib/site-content'

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-border-subtle bg-bg-primary/80 backdrop-blur-lg">
      <div className="mx-auto flex w-full max-w-[1920px] items-center justify-between px-6 py-3 lg:px-10 xl:px-14">
        <Logo />

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
