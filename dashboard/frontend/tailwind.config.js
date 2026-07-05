/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono','IBM Plex Mono','monospace'],
        sans: ['Inter','system-ui','sans-serif'],
      },
      colors: {
        surface: { DEFAULT:'#0B0F19', 1:'#111827', 2:'#1a2235', 3:'#1f2d40' },
        border: '#1e2d42',
        up: '#00e87a',
        down: '#ff4d6a',
        accent: '#3b82f6',
        amber: '#f59e0b',
        text: { primary:'#e2e8f0', secondary:'#8ba3c1', muted:'#4a6080' },
      },
    },
  },
  plugins: [],
}
