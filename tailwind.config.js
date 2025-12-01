/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk color palette
        cyber: {
          dark: '#0a0e27',
          darker: '#050816',
          primary: '#00f0ff', // Neon cyan
          secondary: '#ff00ff', // Neon magenta
          accent: '#00ff9f', // Neon green
          warning: '#ff3864', // Neon red
          purple: '#b026ff',
          blue: '#0066ff',
        },
        neural: {
          'inactive': '#1a1f3a',
          'active': '#00f0ff',
          'warning': '#ffa500',
          'error': '#ff0055',
          'success': '#00ff9f',
        }
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(to right, rgba(0, 240, 255, 0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 240, 255, 0.1) 1px, transparent 1px)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'scan': 'scan 3s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': {
            boxShadow: '0 0 5px rgba(0, 240, 255, 0.5), 0 0 10px rgba(0, 240, 255, 0.3)',
            textShadow: '0 0 10px rgba(0, 240, 255, 0.8)',
          },
          '100%': {
            boxShadow: '0 0 20px rgba(0, 240, 255, 0.8), 0 0 30px rgba(0, 240, 255, 0.5)',
            textShadow: '0 0 20px rgba(0, 240, 255, 1)',
          },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
