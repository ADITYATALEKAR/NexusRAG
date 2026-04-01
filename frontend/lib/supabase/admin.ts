import 'server-only'

import { createClient } from '@supabase/supabase-js'

import { PUBLIC_SUPABASE_URL } from '@/lib/public-config'
import { SUPABASE_SERVICE_ROLE_KEY } from '@/lib/server-config'

let adminClient: ReturnType<typeof createClient> | null = null

export function getSupabaseAdminClient() {
  if (!PUBLIC_SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error(
      'Supabase admin access is not configured. Set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.'
    )
  }

  if (!adminClient) {
    adminClient = createClient(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    })
  }

  return adminClient
}
