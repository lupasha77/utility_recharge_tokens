import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  css: {
    modules: {
      localsConvention: 'camelCase',
    },
  },
  build: {
    sourcemap: false,  // Disable in production
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-router-dom', '@mantine/core'],
          common: ['bcrypt', 'jwt-decode']
        }
      }
    },
    minify: 'esbuild',
  },
  optimizeDeps: {
    include: ['react', 'react-router-dom', '@mantine/core']
  },
  
})