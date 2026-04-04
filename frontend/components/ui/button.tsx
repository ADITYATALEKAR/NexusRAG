'use client'

import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-sm text-sm font-medium transition-all duration-[var(--duration-fast)] disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-500/18',
  {
    variants: {
      variant: {
        default: 'bg-accent-600 text-white shadow-sm hover:bg-accent-700 hover:shadow-[0_14px_28px_-22px_rgba(15,98,254,0.45)]',
        outline: 'border border-border-default bg-bg-elevated text-text-primary hover:border-border-strong hover:bg-bg-secondary/90 hover:shadow-sm',
        ghost: 'text-text-secondary hover:bg-bg-secondary hover:text-text-primary',
        subtle: 'bg-bg-secondary text-text-primary hover:bg-bg-tertiary'
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 px-3 text-xs',
        lg: 'h-12 px-6 text-[0.98rem]',
        icon: 'h-10 w-10'
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'default'
    }
  }
)

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : 'button'
  return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
})
Button.displayName = 'Button'

export { Button, buttonVariants }
