import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [react(), tailwindcss(),
    // ADR-010: the rider app is a PWA. Riders lose signal in traffic, so the
    // shell must load from cache and say plainly that it is offline.
    VitePWA({
      registerType: 'autoUpdate',
      manifest: false, // public/manifest.webmanifest is the source of truth
      workbox: { globPatterns: ['**/*.{js,css,html,woff2,png,svg}'] },
    })],
  server: { port: 5175, strictPort: true },
  preview: { port: 5175, strictPort: true },
  build: {
    // NFR-07 caps the first customer load at 1.5 MB over 3G, so a chunk growing
    // past this is a warning worth reading, not noise to raise the limit for.
    chunkSizeWarningLimit: 400,
  },
});
