/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          950: '#071A12',
          900: '#0E3B28',
          800: '#14532D',
          700: '#166534',
          600: '#15803D',
          500: '#22C55E',
          400: '#4ADE80',
          300: '#86EFAC',
          200: '#BBF7D0',
          100: '#DCFCE7',
          50: '#F0FDF4',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          subtle: '#F8FAFC',
          muted: '#F1F5F9',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        '2xl': '18px',
        '3xl': '24px',
        '4xl': '32px',
      },
      boxShadow: {
        'subtle': '0 1px 3px rgba(0,0,0,0.03), 0 4px 12px rgba(0,0,0,0.02)',
        'card': '0 2px 8px -2px rgba(0,0,0,0.04), 0 10px 24px -4px rgba(0,0,0,0.04)',
        'card-hover': '0 8px 24px -4px rgba(0,0,0,0.08), 0 16px 32px -4px rgba(0,0,0,0.04)',
        'glow-emerald': '0 0 24px rgba(16, 185, 129, 0.25)',
      }
    },
  },
  plugins: [],
}
