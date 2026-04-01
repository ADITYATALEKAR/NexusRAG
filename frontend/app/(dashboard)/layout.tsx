import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'

import { authOptions } from '@/lib/auth'
import { PUBLIC_APP_ENABLED } from '@/lib/public-config'
import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'

export default async function DashboardGroupLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions)
  if (!session && !PUBLIC_APP_ENABLED) {
    redirect('/login')
  }

  return (
    <div className="flex min-h-screen bg-bg-primary">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  )
}
