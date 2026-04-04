'use client'

import { Menu } from 'lucide-react'

import { Sidebar } from '@/components/layout/sidebar'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/stores/app-store'

export default function DashboardGroupLayout({ children }: { children: React.ReactNode }) {
  const mobileSidebarOpen = useAppStore((state) => state.mobileSidebarOpen)
  const desktopSidebarCollapsed = useAppStore((state) => state.desktopSidebarCollapsed)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)
  const sidebarWidth = desktopSidebarCollapsed ? '92px' : '304px'

  return (
    <div
      className="relative h-dvh overflow-hidden bg-bg-primary"
      style={{ ['--workspace-sidebar-width' as string]: sidebarWidth }}
    >
      <Sidebar />
      {!mobileSidebarOpen ? (
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="fixed left-4 top-4 z-30 rounded-full bg-bg-primary/95 shadow-sm md:hidden"
          aria-label="Open navigation"
          onClick={() => setMobileSidebarOpen(true)}
        >
          <Menu className="h-4 w-4" />
        </Button>
      ) : null}
      <div className="h-full min-w-0 transition-[margin] duration-200 md:ml-[var(--workspace-sidebar-width)]">
        <main className="h-full min-w-0 overflow-hidden">{children}</main>
      </div>
    </div>
  )
}

