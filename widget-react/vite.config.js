// vite.config.js - Configuración de Vite para build
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.NODE_ENV': '"production"'
  },
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.js'),
      name: 'InmoBotModule',
      fileName: 'inmobot-widget',
      formats: ['iife']
    },
    rollupOptions: {
      external: [],
      output: {
        inlineDynamicImports: true,
        assetFileNames: 'inmobot-widget.[ext]',
        globals: {}
      }
    },
    minify: 'esbuild'
  },
  // Para desarrollo local
  server: {
    port: 3000,
    open: true
  }
});
