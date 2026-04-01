import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US').format(value)
}

export function formatLatency(value: number) {
  if (value < 1000) {
    return `${Math.round(value)}ms`
  }
  return `${(value / 1000).toFixed(2)}s`
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2
  }).format(value)
}

export function formatRelativeTime(value: string | number | Date) {
  const date = new Date(value)
  const diffMs = date.getTime() - Date.now()
  const formatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const intervals = [
    { unit: 'day', ms: 1000 * 60 * 60 * 24 },
    { unit: 'hour', ms: 1000 * 60 * 60 },
    { unit: 'minute', ms: 1000 * 60 },
    { unit: 'second', ms: 1000 }
  ] as const

  for (const interval of intervals) {
    if (Math.abs(diffMs) >= interval.ms || interval.unit === 'second') {
      return formatter.format(Math.round(diffMs / interval.ms), interval.unit)
    }
  }

  return 'just now'
}

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}