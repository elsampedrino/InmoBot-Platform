// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://navines-landing-page.vercel.app',
  integrations: [sitemap()],
  devToolbar: {
    enabled: false
  },
  vite: {
    plugins: [tailwindcss()]
  }
});
