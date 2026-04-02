import { CTA } from '@/components/landing/cta'
import { Features } from '@/components/landing/features'
import { Hero } from '@/components/landing/hero'
import { Navbar } from '@/components/landing/navbar'
import { TrustSignals } from '@/components/landing/trust-signals'
import { Footer } from '@/components/layout/footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />
      <Hero />
      <Features />
      <TrustSignals />
      <CTA />
      <Footer />
    </div>
  )
}
