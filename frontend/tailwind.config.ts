import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          400: '#8b6df0',
          500: '#6d45e8',
          600: '#5833c9',
          700: '#4625a5',
        },
        accent: { 50: '#ecfdf5', 500: '#14b88a', 600: '#0f9671' },
      },
      boxShadow: {
        card: '0 8px 30px rgb(15 23 42 / 0.08)',
        float: '0 20px 55px rgb(47 31 104 / 0.16)',
      },
    },
  },
  plugins: [],
} satisfies Config
