import { ArrowRight, Mail, Phone } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { FOUNDER_CONTACT } from '@/lib/site-content'

export function CTA() {
  return (
    <section id="contact" className="py-24">
      <div className="mx-auto w-full max-w-[1920px] px-6 lg:px-8 xl:px-10 2xl:px-12">
        <div className="surface overflow-hidden bg-[linear-gradient(135deg,rgba(255,255,255,1),rgba(244,247,255,0.92))] p-10 md:p-14">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_360px]">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Contact
              </p>
              <h2 className="mt-4 max-w-3xl text-3xl font-semibold tracking-[-0.05em] text-text-primary md:text-4xl">
                Start with the live workspace. Move to your own deployment when your team is ready.
              </h2>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button size="lg" asChild>
                  <Link href="/dashboard">
                    Try it free
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="/login">Connect your API</Link>
                </Button>
              </div>
            </div>

            <div className="rounded-[14px] border border-border-subtle bg-bg-primary/88 p-6 shadow-sm">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Founder contact
              </p>
              <h3 className="mt-4 text-2xl font-semibold text-text-primary">
                {FOUNDER_CONTACT.name}
              </h3>
              <p className="mt-2 text-sm text-text-secondary">{FOUNDER_CONTACT.role}</p>
              <div className="mt-6 space-y-4 text-sm text-text-secondary">
                <a
                  href={`mailto:${FOUNDER_CONTACT.email}`}
                  className="flex items-center gap-3 rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-3 transition-colors hover:border-border-default hover:text-text-primary"
                >
                  <Mail className="h-4 w-4 text-accent-700 dark:text-accent-100" />
                  <span>{FOUNDER_CONTACT.email}</span>
                </a>
                <a
                  href={`tel:${FOUNDER_CONTACT.phone.replace(/\s+/g, '')}`}
                  className="flex items-center gap-3 rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-3 transition-colors hover:border-border-default hover:text-text-primary"
                >
                  <Phone className="h-4 w-4 text-accent-700 dark:text-accent-100" />
                  <span>{FOUNDER_CONTACT.phone}</span>
                </a>
              </div>
              <p className="mt-6 text-sm leading-6 text-text-secondary">
                Reach out for a walkthrough, deployment help, or a private rollout plan for your team.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

