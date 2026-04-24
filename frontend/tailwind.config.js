export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#0f172a',
        panel: '#111c33',
        accent: '#60a5fa',
        accent2: '#f97316',
      },
      boxShadow: {
        glow: '0 20px 40px rgba(96, 165, 250, 0.12)',
      },
    },
  },
  plugins: [],
};
