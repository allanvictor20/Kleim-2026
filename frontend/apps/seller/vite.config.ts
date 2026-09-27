import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5174, strictPort: true },
  preview: { port: 5174, strictPort: true },
  build: {
    // NFR-07 caps the first customer load at 1.5 MB over 3G, so a chunk growing
    // past this is a warning worth reading, not noise to raise the limit for.
    chunkSizeWarningLimit: 400,
  },
});
