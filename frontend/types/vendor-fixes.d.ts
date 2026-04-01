declare module 'framer-motion' {
  export const motion: any
}

declare module 'react-hook-form' {
  import type { BaseSyntheticEvent } from 'react'

  export type FieldError = {
    message?: string
  }

  export type RegisterResult = {
    name: string
    onBlur?: (...args: unknown[]) => void
    onChange?: (...args: unknown[]) => void
    ref?: (...args: unknown[]) => void
  }

  export interface UseFormReturn<TFieldValues> {
    register: (name: keyof TFieldValues & string) => RegisterResult
    reset: (values?: Partial<TFieldValues>) => void
    handleSubmit: (
      onValid: (values: TFieldValues) => unknown | Promise<unknown>
    ) => (event?: BaseSyntheticEvent) => Promise<void>
    formState: {
      errors: Partial<Record<keyof TFieldValues, FieldError>>
      isSubmitting: boolean
      isSubmitSuccessful: boolean
    }
  }

  export function useForm<TFieldValues>(options?: {
    resolver?: unknown
    defaultValues?: Partial<TFieldValues>
    values?: TFieldValues
  }): UseFormReturn<TFieldValues>
}
