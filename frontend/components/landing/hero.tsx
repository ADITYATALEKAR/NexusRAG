'use client'

import { motion } from 'framer-motion'
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  Quote,
  Search,
  ShieldCheck,
  Layers,
} from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const howToUseSteps = [
  {
    title: 'Upload documents',
    description:
      'Ingest PDF, DOCX, TXT, Markdown, HTML, CSV, or JSON files up to 50 MB each. NexusRAG applies semantic chunking (512-token target, 64-token overlap) and indexes every chunk for hybrid retrieval.',
  },
  {
    title: 'Ask a question',
    description:
      'Query your knowledge base in natural language. The system runs dense vector search and BM25 keyword matching in parallel, fuses the top 50 results from each, reranks to 25, and returns the best 10 passages to the generation model.',
  },
  {
    title: 'Verify with citations',
    description:
      'Every answer includes inline source references with document names, chunk positions, and relevance scores. If the evidence is insufficient, the system abstains rather than guessing.',
  },
]

const accessModes = [
  {
    title: 'Hosted evaluation',
    description: `Try the full pipeline — upload, retrieve, and verify — with ${PUBLIC_TRIAL_QUERY_LIMIT} free queries on our managed API. No account required.`,
    ctaLabel: 'Start free',
    href: '/dashboard',
  },
  {
    title: 'Self-hosted deployment',
    description:
      'Deploy your own NexusRAG API and connect the same workspace for unlimited queries, private data, and full operational control.',
    ctaLabel: 'Connect your API',
    href: '/login',
  },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border-subtle">
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.035]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-accent-50/80 to-transparent dark:from-accent-500/10" />
      <div className="relative mx-auto max-w-[1440px] px-6 pb-24 pt-20 lg:pb-28 lg:pt-24">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50 px-3 py-1 text-sm font-medium text-accent-700 dark:border-accent-500/20 dark:bg-accent-500/10 dark:text-accent-100"
        >
          <CheckCircle2 className="h-4 w-4" />
          Open-source &middot; GPT-4o + multi-provider failover &middot; Self-hostable
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="mt-8 max-w-4xl text-balance text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl lg:text-6xl"
        >
          Enterprise RAG with
          <span className="block text-accent-600 dark:text-accent-100">
            evidence built in
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.12 }}
          className="mt-6 max-w-2xl text-lg leading-8 text-text-secondary"
        >
          NexusRAG is an API-first retrieval platform for teams that need grounded answers
          from private documents. Hybrid search, inline citations, abstention when evidence
          is thin, and a self-hostable stack — not another chat wrapper.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-10 flex flex-col gap-4 sm:flex-row"
        >
          <Button size="lg" asChild>
            <Link href="/dashboard">
              Try it free
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Connect your own API</Link>
          </Button>
        </motion.div>
        <div className="mt-5 text-sm text-text-tertiary">
          {PUBLIC_TRIAL_QUERY_LIMIT} free queries on the hosted API &middot; No account required
        </div>

        <div className="mt-12 flex flex-wrap gap-3 text-sm text-text-secondary">
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <Quote className="h-4 w-4 text-accent-600 dark:text-accent-100" />
            Citation-backed answers with abstention
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <Search className="h-4 w-4 text-accent-600 dark:text-accent-100" />
            Hybrid retrieval: dense vectors + BM25
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <Layers className="h-4 w-4 text-accent-600 dark:text-accent-100" />
            GPT-4o default &middot; Claude &middot; Gemini &middot; Llama failover
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
            <ShieldCheck className="h-4 w-4 text-accent-600 dark:text-accent-100" />
            Self-hostable &middot; Full REST API
          </div>
        </div>

        <div
          id="how-it-works"
          className="mt-16 grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.8fr)]"
        >
          <div className="surface space-y-6 p-8">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                How it works
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-text-primary">
                From raw files to cited answers in three steps
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
