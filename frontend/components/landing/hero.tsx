'use client'

import { motion } from 'framer-motion'
import {
  ArrowRight,
  CheckCircle2,
  Cloud,
  Database,
  FileSearch,
  Quote,
  Search,
  Server,
  ShieldCheck,
} from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const howToUseSteps = [
  {
    title: 'Upload documents',
    description:
      'Ingest PDF, DOCX, TXT, Markdown, HTML, CSV, or JSON files up to 50 MB each. NexusRAG applies semantic chunking with a 512-token target and 64-token overlap.',
  },
  {
    title: 'Run hybrid retrieval',
    description:
      'Dense vector search and BM25 keyword matching run in parallel, then fuse and rerank the strongest passages before generation.',
  },
  {
    title: 'Verify every answer',
    description:
      'Answers include inline citations, document names, and relevance context. If the evidence is weak, NexusRAG abstains instead of guessing.',
  },
]

const accessModes = [
  {
    title: 'Hosted evaluation',
    description: `${PUBLIC_TRIAL_QUERY_LIMIT} free hosted queries to test the full ingest -> retrieve -> answer loop without setup.`,
    ctaLabel: 'Try it free',
    href: '/dashboard',
  },
  {
    title: 'Bring your own API',
    description:
      'Point the same workspace at your own NexusRAG deployment for unlimited usage, private data, and full operational control.',
    ctaLabel: 'Connect your API',
    href: '/login',
  },
]

const architecturePreview = [
  {
    icon: Cloud,
    title: 'Cloudflare Pages',
    description: 'Static frontend at the edge',
  },
  {
    icon: Server,
    title: 'Render',
    description: 'FastAPI ingestion and retrieval runtime',
  },
  {
    icon: Database,
    title: 'Neon pgvector',
    description: 'Document, chunk, and embedding storage',
  },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border-subtle">
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.035]" />
      <div className="absolute inset-x-0 top-0 h-[440px] bg-gradient-to-b from-accent-50/90 to-transparent dark:from-accent-500/10" />

      <div className="relative mx-auto w-full max-w-[1920px] px-6 pb-18 pt-14 lg:px-10 lg:pb-22 lg:pt-16 xl:px-14">
        <div className="grid gap-10 xl:grid-cols-[minmax(720px,1.18fr)_minmax(560px,0.82fr)] xl:items-start">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45 }}
              className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50 px-3 py-1 text-sm font-medium text-accent-700 dark:border-accent-500/20 dark:bg-accent-500/10 dark:text-accent-100"
            >
              <CheckCircle2 className="h-4 w-4" />
              Open-source · GPT-4o + multi-provider failover · Self-hostable
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.05 }}
              className="mt-8 max-w-[860px] text-balance text-5xl font-semibold tracking-tight text-text-primary sm:text-6xl xl:text-[88px] xl:leading-[0.95]"
            >
              Enterprise RAG with
              <span className="block text-accent-600 dark:text-accent-100">evidence built in</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.12 }}
              className="mt-6 max-w-[860px] text-xl leading-9 text-text-secondary"
            >
              NexusRAG is an API-first retrieval platform for teams that need grounded answers
              from private documents. Hybrid search, inline citations, abstention when evidence
              is thin, and a self-hostable stack, not another chat wrapper.
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
              {PUBLIC_TRIAL_QUERY_LIMIT} free queries on the hosted API · No account required
            </div>

            <div className="mt-10 flex flex-wrap gap-3 text-sm text-text-secondary">
              <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
                <Quote className="h-4 w-4 text-accent-600 dark:text-accent-100" />
                Citation-backed answers with abstention
              </div>
              <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
                <Search className="h-4 w-4 text-accent-600 dark:text-accent-100" />
                Hybrid retrieval: dense vectors + BM25
              </div>
              <div className="inline-flex items-center gap-2 rounded-full bg-bg-elevated px-4 py-2 shadow-sm">
                <ShieldCheck className="h-4 w-4 text-accent-600 dark:text-accent-100" />
                Self-hostable · Full REST API
              </div>
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.55, delay: 0.15 }}
            className="grid gap-4"
          >
            <div className="surface overflow-hidden p-7">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Live architecture
              </p>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight text-text-primary">
                Evaluate the same stack you would ship
              </h2>
              <p className="mt-3 text-sm leading-7 text-text-secondary">
                Browser requests land on a static frontend, reach a dedicated API runtime, and
                write document metadata plus vectors into managed Postgres with pgvector.
              </p>

              <div className="mt-6 grid gap-3">
                {architecturePreview.map((layer, index) => (
                  <div
                    key={layer.title}
                    className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                        <layer.icon className="h-5 w-5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-text-primary">{layer.title}</p>
                          <span className="text-[11px] font-medium uppercase tracking-[0.18em] text-text-tertiary">
                            0{index + 1}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-text-secondary">{layer.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-text-tertiary">
                      Retrieval
                    </p>
                    <p className="mt-1 text-sm font-medium text-text-primary">Dense + BM25 + rerank</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-text-tertiary">
                      Answers
                    </p>
                    <p className="mt-1 text-sm font-medium text-text-primary">Inline citations with evidence</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-text-tertiary">
                      Modes
                    </p>
                    <p className="mt-1 text-sm font-medium text-text-primary">Hosted trial or your own API</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {accessModes.map((mode) => (
                <div key={mode.title} className="surface space-y-4 p-6">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                    <FileSearch className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">{mode.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-text-secondary">{mode.description}</p>
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
          </motion.div>
        </div>

        <div
          id="how-it-works"
          className="mt-14 grid gap-6 xl:grid-cols-[minmax(0,1.38fr)_minmax(380px,0.62fr)]"
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
            <div className="grid gap-4 xl:grid-cols-3">
              {howToUseSteps.map((step, index) => (
                <div
                  key={step.title}
                  className="rounded-2xl border border-border-subtle bg-bg-primary px-5 py-5"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-sm font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                    0{index + 1}
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-text-primary">{step.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-text-secondary">{step.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="surface space-y-4 p-8">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
              Why teams pick it
            </p>
            <h3 className="text-2xl font-semibold tracking-tight text-text-primary">
              Grounded answers without a bloated stack
            </h3>
            <div className="space-y-3 text-sm leading-7 text-text-secondary">
              <p>Built for legal, consulting, support, ops, and internal knowledge teams.</p>
              <p>Developer-first API plus a ready-to-use workspace for operators and analysts.</p>
              <p>Evidence-first answers with abstention when the source material is not strong enough.</p>
              <p>Hosted evaluation for speed, self-hosting for control.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
