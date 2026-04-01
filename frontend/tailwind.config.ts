import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
    './styles/**/*.css'
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'hsl(var(--color-bg-primary) / <alpha-value>)',
          secondary: 'hsl(var(--color-bg-secondary) / <alpha-value>)',
          tertiary: 'hsl(var(--color-bg-tertiary) / <alpha-value>)',
          elevated: 'hsl(var(--color-bg-elevated) / <alpha-value>)'
        },
        border: {
          default: 'hsl(var(--color-border-default) / <alpha-value>)',
          subtle: 'hsl(var(--color-border-subtle) / <alpha-value>)',
          strong: 'hsl(var(--color-border-strong) / <alpha-value>)'
        },
        text: {
          primary: 'hsl(var(--color-text-primary) / <alpha-value>)',
          secondary: 'hsl(var(--color-text-secondary) / <alpha-value>)',
          tertiary: 'hsl(var(--color-text-tertiary) / <alpha-value>)',
          inverted: 'hsl(var(--color-text-inverted) / <alpha-value>)'
        },
        accent: {
          50: 'hsl(var(--color-accent-50) / <alpha-value>)',
          100: 'hsl(var(--color-accent-100) / <alpha-value>)',
          500: 'hsl(var(--color-accent-500) / <alpha-value>)',
          600: 'hsl(var(--color-accent-600) / <alpha-value>)',
          700: 'hsl(var(--color-accent-700) / <alpha-value>)'
        },
        success: 'hsl(var(--color-success) / <alpha-value>)',
        warning: 'hsl(var(--color-warning) / <alpha-value>)',
        error: 'hsl(var(--color-error) / <alpha-value>)',
        info: 'hsl(var(--color-info) / <alpha-value>)'
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        glow: 'var(--shadow-glow)'
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)'
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)']
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.6s linear infinite'
      }
    }
  },
  plugins: []
}

export default config
