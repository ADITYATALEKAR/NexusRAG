'use client'

import { motion } from 'framer-motion'
import { ArrowRight, ShieldCheck, Sparkles } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border-subtle">
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.035]" />
      <div className="absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-accent-50/80 to-transparent dark:from-accent-500/10" />
      <div className="relative mx-auto max-w-6xl px-6 pb-24 pt-24 lg:pb-28 lg:pt-32">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }} className="mx-auto inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50 px-3 py-1 text-sm font-medium text-accent-700 dark:border-accent-500/20 dark:bg-accent-500/10 dark:text-accent-100">
          <Sparkles className="h-4 w-4" />
          Enterprise-ready RAG
        </motion.div>
        <motion.h1 initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.05 }} className="mx-auto mt-8 max-w-4xl text-balance text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl lg:text-6xl">
          Your knowledge, <span className="text-accent-600 dark:text-accent-100">instantly accessible</span>
        </motion.h1>
        <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, delay: 0.12 }} className="mt-6 max-w-2xl text-lg leading-8 text-text-secondary">
          A calm, premium retrieval workspace for teams that need grounded answers, fast ingestion, and operational trust from the very first query.
        </motion.p>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }} className="mt-10 flex flex-col gap-4 sm:flex-row">
          <Button size="lg" asChild>
            <Link href="/signup">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/dashboard">Open live workspace</Link>
          </Button>
        </motion.div>
        <div className="mt-12 flex flex-wrap gap-4 text-sm text-text-secondary">
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <ShieldCheck className="h-4 w-4 text-success" />
            Citation-backed by design
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <ShieldCheck className="h-4 w-4 text-success" />
            Self-hostable and audit-friendly
          </div>
        </div>
      </div>
    </section>
  )
}