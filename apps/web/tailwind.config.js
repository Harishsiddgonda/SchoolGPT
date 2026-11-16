/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: '#0f172a',
          navyLight: '#1e293b',
          blue: '#1d4ed8',
          royal: '#2563eb',
          accent: '#7c3aed',
          lightAccent: '#8b5cf6',
          bg: '#f8fafc',
          card: '#ffffff'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Manrope', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
