import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // 1. SILENCE THE WARNING
    // Three.js is huge (1MB+), so we bump the warning limit to 1600kB (1.6MB).
    // This tells Vite: "It's a 3D app, big files are expected."
    chunkSizeWarningLimit: 1600,

    rollupOptions: {
      output: {
        // 2. ISOLATE THE HEAVY 3D ENGINE
        // We keep 'three' separate so it caches nicely in the browser.
        // We removed 'react-vendor' because it was generating empty chunk warnings.
        manualChunks: {
          'three-vendor': ['three'],
        },
      },
    },
  },
});
