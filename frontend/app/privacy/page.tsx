import { Navbar } from '@/components/landing/navbar'
import { Footer } from '@/components/layout/footer'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />
      <main className="mx-auto w-full max-w-[1920px] px-6 py-16 lg:px-8 xl:px-10 2xl:px-12">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-semibold tracking-tight text-text-primary">Privacy Policy</h1>
          <p className="mt-2 text-sm text-text-tertiary">Last updated: April 4, 2026</p>

          <div className="mt-10 space-y-8 text-sm leading-7 text-text-secondary">
            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">1. Overview</h2>
              <p>
                This Privacy Policy describes how Fundamental Labs (&ldquo;we&rdquo;,
                &ldquo;us&rdquo;) collects, uses, and handles your information when you use
                NexusRAG (&ldquo;the Service&rdquo;).
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">2. Information We Collect</h2>
              <p>
                <strong>Documents you upload:</strong> When using the hosted evaluation, documents
                you upload are processed to generate embeddings and enable retrieval. Documents are
                stored temporarily to provide the Service.
              </p>
              <p>
                <strong>Queries:</strong> Questions you submit are processed to generate answers.
                Query content may be logged for service quality and debugging purposes.
              </p>
              <p>
                <strong>Usage data:</strong> We may collect basic usage metrics such as query count
                and error rates to maintain and improve the Service.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">3. How We Use Your Information</h2>
              <p>We use collected information to:</p>
              <ul className="list-disc space-y-1 pl-5">
                <li>Provide and maintain the Service</li>
                <li>Generate retrieval-backed answers to your queries</li>
                <li>Monitor and improve service quality</li>
                <li>Enforce usage limits on the hosted evaluation</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">4. Third-Party Services</h2>
              <p>
                The Service uses third-party providers for LLM generation (OpenAI, Anthropic,
                Google, Groq), hosting (Render, Cloudflare), and data storage (Neon). Your data
                may be processed by these providers in accordance with their respective privacy
                policies.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">5. Self-Hosted Deployments</h2>
              <p>
                When you deploy your own NexusRAG instance, all data remains on your own
                infrastructure. Fundamental Labs does not have access to data in self-hosted
                deployments.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">6. Data Retention</h2>
              <p>
                Documents and query data from the hosted evaluation may be retained for the duration
                of the evaluation session. We do not retain your data indefinitely and do not sell
                your data to third parties.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">7. Data Security</h2>
              <p>
                We implement reasonable technical and organizational measures to protect your data.
                However, no method of transmission or storage is completely secure.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">8. Your Rights</h2>
              <p>
                You may request deletion of your uploaded documents and associated data by
                contacting us. For self-hosted deployments, you have full control over your data.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">9. Changes to This Policy</h2>
              <p>
                We may update this Privacy Policy from time to time. Changes will be reflected by
                updating the &ldquo;Last updated&rdquo; date above.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">10. Contact</h2>
              <p>
                For privacy-related questions, contact us at{' '}
                <a href="mailto:aditya.a.talekar@gmail.com" className="text-accent-600 hover:underline">
                  aditya.a.talekar@gmail.com
                </a>
                .
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
