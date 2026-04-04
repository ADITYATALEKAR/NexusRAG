import { Features } from '@/components/landing/features'
import { Hero } from '@/components/landing/hero'
import { Navbar } from '@/components/landing/navbar'
import { Positioning } from '@/components/landing/positioning'
import { TrustSignals } from '@/components/landing/trust-signals'
import { Footer } from '@/components/layout/footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Navbar />
      <Hero />
      <TrustSignals />
      <Positioning />
      <Features />
      <Footer />
    </div>
  )
}
