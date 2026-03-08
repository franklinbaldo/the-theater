import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [mdx()],
  site: 'https://franklinbaldo.github.io',
  base: '/the-november-log',
  content: {
    collections: true,
  },
});
