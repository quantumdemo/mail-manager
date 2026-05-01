/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c1d3ff',
          300: '#a2bdff',
          400: '#83a7ff',
          500: '#6491ff',
          600: '#5074cc',
          700: '#3c5799',
          800: '#283a66',
          900: '#141d33',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
