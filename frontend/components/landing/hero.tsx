'use client'

import { motion } from 'framer-motion'
import {
  ArrowRight,
  Database,
  FileSearch,
  Network,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const howToUseSteps = [
  {
    title: 'Upload your operating knowledge',
    description:
      'Bring in PDFs, DOCX, Markdown, and text. NexusRAG indexes them into a searchable evidence layer instead of a loose chat dump.',
  },
  {
    title: 'Ask focused, decision-grade questions',
    description:
      'Query policies, product docs, client material, or research and get retrieval-backed answers designed for follow-up, not guesswork.',
  },
  {
    title: 'Review sources before you act',
    description:
      'Every answer is paired with source excerpts, document names, and relevance context so teams can audit what the system used.',
  },
]

const accessModes = [
  {
    title: 'Free hosted evaluation',
    description: `Use our live hosted API for up to ${PUBLIC_TRIAL_QUERY_LIMIT} questions and see the full workflow end to end.`,
    ctaLabel: 'Start free',
    href: '/dashboard',
  },
  {
    title: 'Bring your own API',
    description:
      'Point the same interface at your own NexusRAG API endpoint and key for unlimited usage on your own infrastructure.',
    ctaLabel: 'Use your own API',
    href: '/login',
  },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border-subtle">
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.035]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-accent-50/80 to-transparent dark:from-accent-500/10" />
      <div className="relative mx-auto max-w-6xl px-6 pb-24 pt-24 lg:pb-28 lg:pt-32">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="mx-auto inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50 px-3 py-1 text-sm font-medium text-accent-700 dark:border-accent-500/20 dark:bg-accent-500/10 dark:text-accent-100"
        >
          <Sparkles className="h-4 w-4" />
          Cloudflare Pages + Render + Neon live
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="mx-auto mt-8 max-w-5xl text-balance text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl lg:text-6xl"
        >
          Retrieval that shows its work,
          <span className="block text-accent-600 dark:text-accent-100">
            not just another answer box
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.12 }}
          className="mt-6 max-w-3xl text-lg leading-8 text-text-secondary"
        >
          NexusRAG turns documents into a production-grade knowledge workspace with hybrid
          retrieval, citation-backed answers, and a deployment shape real teams can operate:
          Cloudflare Pages on the edge, Render for the live API, and Neon pgvector for the
          evidence layer.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-10 flex flex-col gap-4 sm:flex-row"
        >
          <Button size="lg" asChild>
            <Link href="/dashboard">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Use your own API</Link>
          </Button>
        </motion.div>
        <div className="mt-6 max-w-3xl text-sm leading-7 text-text-secondary">
          Start with the hosted trial for {PUBLIC_TRIAL_QUERY_LIMIT} questions, then switch to
          your own NexusRAG API endpoint for unlimited usage without changing the interface.
        </div>
        <div className="mt-12 flex flex-wrap gap-4 text-sm text-text-secondary">
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <ShieldCheck className="h-4 w-4 text-success" />
            Citation-backed answers
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <Network className="h-4 w-4 text-info" />
            Hybrid retrieval and auditable evidence
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <Database className="h-4 w-4 text-success" />
            Neon pgvector deployment already live
          </div>
        </div>

        <div
          id="how-to-use"
          className="mt-16 grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.8fr)]"
        >
          <div className="surface space-y-6 p-8">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                How to use
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-text-primary">
                Three steps from raw files to defensible answers
              </h2>
            </div>
            <div className="space-y-4">
              {howToUseSteps.map((step, index) => (
                <div
                  key={step.title}
                  className="grid gap-3 rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4 md:grid-cols-[44px_minmax(0,1fr)]"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-sm font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                    0{index + 1}
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-text-primary">{step.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-text-secondary">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {accessModes.map((mode) => (
              <div key={mode.title} className="surface space-y-4 p-6">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                  <FileSearch className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{mode.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-text-secondary">
                    {mode.description}
                  </p>
                </div>
                <Button variant="outline" className="w-full justify-between" asChild>
                  <Link href={mode.href}>
                    {mode.ctaLabel}
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
