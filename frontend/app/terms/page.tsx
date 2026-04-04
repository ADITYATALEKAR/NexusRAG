import { Navbar } from '@/components/landing/navbar'
import { Footer } from '@/components/layout/footer'

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />
      <main className="mx-auto w-full max-w-[1920px] px-6 py-16 lg:px-8 xl:px-10 2xl:px-12">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-semibold tracking-tight text-text-primary">Terms of Use</h1>
          <p className="mt-2 text-sm text-text-tertiary">Last updated: April 4, 2026</p>

          <div className="mt-10 space-y-8 text-sm leading-7 text-text-secondary">
            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">1. Acceptance of Terms</h2>
              <p>
                By accessing or using NexusRAG (&ldquo;the Service&rdquo;), operated by Fundamental
                Labs, you agree to be bound by these Terms of Use. If you do not agree, do not use
                the Service.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">2. Description of Service</h2>
              <p>
                NexusRAG is a retrieval-augmented generation platform that allows users to upload
                documents, query them using hybrid search, and receive citation-backed answers. The
                Service is available through a hosted evaluation mode and a self-hosted deployment
                option.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">3. Hosted Evaluation</h2>
              <p>
                The hosted evaluation provides a limited number of free queries on our managed API.
                This is intended for evaluation purposes only. We reserve the right to modify or
                discontinue the hosted evaluation at any time without notice.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">4. User Responsibilities</h2>
              <p>
                You are responsible for the documents you upload and the queries you submit. You
                must not upload content that is illegal, infringes on intellectual property rights,
                or violates any applicable laws or regulations.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">5. Data and Privacy</h2>
              <p>
                Documents uploaded to the hosted evaluation may be processed and temporarily stored
                to provide the Service. For details on data handling, see our{' '}
                <a href="/privacy" className="text-accent-600 hover:underline">
                  Privacy Policy
                </a>
                .
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">6. Intellectual Property</h2>
              <p>
                NexusRAG is an open-source project. You retain all rights to your uploaded documents
                and generated outputs. The NexusRAG name and logo are trademarks of Fundamental
                Labs.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">7. Disclaimer of Warranties</h2>
              <p>
                The Service is provided &ldquo;as is&rdquo; without warranties of any kind, whether
                express or implied. Generated answers may contain inaccuracies and should be
                verified against source documents before acting on them.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">8. Limitation of Liability</h2>
              <p>
                Fundamental Labs shall not be liable for any indirect, incidental, special, or
                consequential damages arising from your use of the Service.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">9. Changes to Terms</h2>
              <p>
                We may update these Terms at any time. Continued use of the Service after changes
                constitutes acceptance of the updated Terms.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-text-primary">10. Contact</h2>
              <p>
                For questions about these Terms, contact us at{' '}
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
