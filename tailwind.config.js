/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Enhanced Cyberpunk color palette with better gradients
        cyber: {
          dark: '#0a0e27',
          darker: '#050816',
          darkest: '#020308',
          primary: '#00f0ff', // Neon cyan
          'primary-light': '#33f3ff',
          'primary-dark': '#00b8cc',
          secondary: '#ff00ff', // Neon magenta
          'secondary-light': '#ff66ff',
          'secondary-dark': '#cc00cc',
          accent: '#00ff9f', // Neon green
          'accent-light': '#66ffbf',
          'accent-dark': '#00cc7f',
          warning: '#ff3864', // Neon red
          'warning-light': '#ff6b8a',
          'warning-dark': '#cc2d50',
          purple: '#b026ff',
          'purple-light': '#c966ff',
          'purple-dark': '#8c1ecc',
          blue: '#0066ff',
          'blue-light': '#3385ff',
          'blue-dark': '#0052cc',
          gold: '#ffd700',
          'gold-light': '#ffe34d',
          'gold-dark': '#ccac00',
        },
        neural: {
          'inactive': '#1a1f3a',
          'active': '#00f0ff',
          'warning': '#ffa500',
          'error': '#ff0055',
          'success': '#00ff9f',
          'optimal': '#ffd700',
        }
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(to right, rgba(0, 240, 255, 0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 240, 255, 0.1) 1px, transparent 1px)',
        'grid-pattern-dense': 'linear-gradient(to right, rgba(0, 240, 255, 0.15) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 240, 255, 0.15) 1px, transparent 1px)',
        'cyber-gradient': 'linear-gradient(135deg, #00f0ff 0%, #ff00ff 50%, #00ff9f 100%)',
        'cyber-gradient-radial': 'radial-gradient(ellipse at center, rgba(0, 240, 255, 0.15) 0%, transparent 70%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'glow-fast': 'glow 1s ease-in-out infinite alternate',
        'scan': 'scan 3s linear infinite',
        'scan-fast': 'scan 1.5s linear infinite',
        'float': 'float 3s ease-in-out infinite',
        'rotate-slow': 'rotate 20s linear infinite',
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
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'cyber': '0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3)',
        'cyber-lg': '0 0 20px rgba(0, 240, 255, 0.8), 0 0 40px rgba(0, 240, 255, 0.5)',
        'neural': '0 0 15px rgba(0, 255, 159, 0.6), 0 0 30px rgba(0, 255, 159, 0.4)',
      },
    },
  },
  plugins: [],
}
