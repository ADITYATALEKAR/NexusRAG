'use client'

import { Menu } from 'lucide-react'

import { Sidebar } from '@/components/layout/sidebar'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/stores/app-store'

export default function DashboardGroupLayout({ children }: { children: React.ReactNode }) {
  const mobileSidebarOpen = useAppStore((state) => state.mobileSidebarOpen)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)

  return (
    <div className="flex h-screen overflow-hidden bg-bg-primary">
      <Sidebar />
      {!mobileSidebarOpen ? (
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="fixed left-4 top-4 z-30 rounded-xl bg-bg-primary/95 shadow-sm md:hidden"
          aria-label="Open navigation"
          onClick={() => setMobileSidebarOpen(true)}
        >
          <Menu className="h-4 w-4" />
        </Button>
      ) : null}
      <main className="min-w-0 flex-1 overflow-hidden md:pl-0">{children}</main>
    </div>
  )
}
