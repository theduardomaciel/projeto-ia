import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

const target = process.env.BACKEND_URL || 'http://localhost:8000';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      // Forward /api/* to the backend to avoid CORS during dev
      '/api': {
        target,
        changeOrigin: true
      }
    }
  }
});
