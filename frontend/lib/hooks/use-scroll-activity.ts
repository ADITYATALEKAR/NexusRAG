'use client'

import { useEffect, useRef } from 'react'

export function useScrollActivity<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) {
      return
    }

    let timeoutId: number | null = null

    const markScrolling = () => {
      element.dataset.scrolling = 'true'
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId)
      }
      timeoutId = window.setTimeout(() => {
        delete element.dataset.scrolling
      }, 550)
    }

    element.addEventListener('scroll', markScrolling, { passive: true })

    return () => {
      element.removeEventListener('scroll', markScrolling)
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId)
      }
    }
  }, [])

  return ref
}
